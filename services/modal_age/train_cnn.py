"""Kámárí CNN age model — best-practice training on Modal (GPU).

Pulls the dataset from HF `<HF_NAMESPACE>/kamari-faces-v0`, trains a strong, exportable
multi-head age model, runs a FULL subgroup + latency evaluation on the frozen benchmark,
tracks everything in W&B, checkpoints every epoch (resumable), and uploads weights + ONNX
+ thresholds + metrics + reports + model card to `<HF_NAMESPACE>/cnn-age-v0`.

Built for the project aim (safe African age-gating):
- backbone EfficientNetV2-S (accurate + ONNX/TFLite-exportable)
- composite sampler: inverse-freq over (age-band x skin-band) + 13-21 boost + dark-skin boost
- model selection by a SAFETY composite (MAE + heavy weight on Minor-Pass-Through@18)
- bf16 autocast, cosine LR + warmup, grad clipping, allowed-only augmentation
- eval: MAE overall + by skin/age/dataset/gender, MPTR@18/@21, Adult-Block, latency p50/p95

Secrets:
    modal secret create kamari-hf HF_TOKEN=... HF_NAMESPACE=... WANDB_API_KEY=... WANDB_PROJECT=kamari
Run:
    modal run services/modal_age/train_cnn.py --epochs 30
"""
import os

import modal

GPU = os.environ.get("KAMARI_GPU", "H200")  # user has H200; set "H100"/"B200" to change

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "torch", "torchvision", "timm", "onnx", "onnxruntime",
        "huggingface_hub", "pandas", "pyarrow", "pillow", "numpy", "scikit-learn", "wandb",
    )
)
app = modal.App("kamari-cnn-train", image=image)
ckpt_vol = modal.Volume.from_name("kamari-cnn", create_if_missing=True)
hf_secret = modal.Secret.from_name("kamari-hf")

MEAN = [0.485, 0.456, 0.406]
STD = [0.229, 0.224, 0.225]
CKPT = "/ckpt"
BLOCK_P = 0.70


def _band(a):
    a = int(a)
    for lo, hi in [(0, 12), (13, 15), (16, 17), (18, 20), (21, 25), (26, 35), (36, 50), (51, 120)]:
        if lo <= a <= hi:
            return f"{lo}-{hi}"
    return "na"


@app.function(gpu=GPU, cpu=16.0, memory=65536, timeout=60 * 60 * 24,
              volumes={CKPT: ckpt_vol}, secrets=[hf_secret])
def train(epochs: int = 30, backbone: str = "tf_efficientnetv2_s",
          lr: float = 3e-4, batch_size: int = 512, warmup_frac: float = 0.05,
          val_frac: float = 0.1, seed: int = 7):
    import hashlib
    import json
    import math
    import time
    import numpy as np
    import pandas as pd
    import timm
    import torch
    import torch.nn as nn
    import torchvision.transforms as T
    from huggingface_hub import snapshot_download
    from PIL import Image
    from torch.utils.data import Dataset, DataLoader, WeightedRandomSampler

    torch.manual_seed(seed); np.random.seed(seed)
    torch.backends.cudnn.benchmark = True          # autotune convs for fixed input size
    torch.backends.cuda.matmul.allow_tf32 = True   # TF32 matmuls on H200
    torch.backends.cudnn.allow_tf32 = True
    token, ns = os.environ["HF_TOKEN"], os.environ.get("HF_NAMESPACE", "kamari")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    nworkers = max(4, (os.cpu_count() or 8))
    os.makedirs(CKPT, exist_ok=True)

    # ---------------- data ----------------
    data_dir = snapshot_download(f"{ns}/kamari-faces-v0", repo_type="dataset", token=token)
    _tar = os.path.join(data_dir, "crops_v0.tar")
    if os.path.exists(_tar) and not os.path.isdir(os.path.join(data_dir, "crops")):
        import tarfile
        with tarfile.open(_tar) as _tf:
            _tf.extractall(data_dir)

    def _read(name):
        p = os.path.join(data_dir, "manifests", name)
        return pd.read_parquet(p) if os.path.exists(p) else None

    df = _read("manifest_train_v0.parquet")
    df = df[df["age"].notna()].copy()
    df = df[df["path"].map(lambda p: os.path.exists(os.path.join(data_dir, str(p))))].reset_index(drop=True)
    if not len(df):
        raise RuntimeError("No training crops found — set ALLOW_PRIVATE_CROP_UPLOAD=1 in the data notebook.")

    # ---- data-integrity guard (defends against mis-parsed/categorical ages) ----
    # Per-dataset age audit so bad sources are visible (e.g. filename-as-age -> fake toddlers).
    audit = (df.assign(_u13=(df["age"] < 13).astype(float))
               .groupby("dataset")["age"]
               .agg(n="size", amin="min", amax="max", amean="mean", nunique="nunique"))
    audit["pct_under13"] = df.assign(u=(df["age"] < 13)).groupby("dataset")["u"].mean()
    print("per-dataset age audit:\n", audit.round(2).to_string())
    # Train ONLY on datasets with verified exact-age parsing (override via env).
    trusted = {x.strip() for x in os.environ.get(
        "KAMARI_TRUSTED_AGE_DATASETS", "UTKFace,APPA-REAL,FG-NET,IMDB-WIKI").split(",") if x.strip()}
    keep = df["dataset"].isin(trusted) & df["age"].between(1, 100)
    if "age_exact" in df:
        keep &= (df["age_exact"] == True)
    if (~keep).any():
        print("dropped (untrusted / implausible age):", df.loc[~keep, "dataset"].value_counts().to_dict())
    df = df[keep].reset_index(drop=True)
    if not len(df):
        raise RuntimeError(
            "No trusted exact-age rows after integrity filter. "
            "Set KAMARI_TRUSTED_AGE_DATASETS to your verified-exact-age datasets.")
    print(f"trusted training rows: {len(df)} from {sorted(set(df['dataset']))}")

    def _holdout(key):
        return (int(hashlib.md5(str(key).encode()).hexdigest()[:8], 16) / 0xFFFFFFFF) < val_frac
    key = df["subject_id"].where(df["subject_id"].notna() & (df["subject_id"].astype(str) != ""), df["image_id"])
    is_val = key.map(_holdout)
    train_df, val_df = df[~is_val].reset_index(drop=True), df[is_val].reset_index(drop=True)
    bench = _read("manifest_benchmark_v0.parquet")
    print(f"train {len(train_df)} | val {len(val_df)} | benchmark {0 if bench is None else len(bench)}")

    # ---------------- composite sampling weights ----------------
    strat = train_df["age"].map(_band) + "|" + train_df["skin_band"].astype(str)
    counts = strat.value_counts()
    w = strat.map(1.0 / counts).astype(float)
    w = w / w.mean()
    w *= np.where(train_df["age"].between(13, 21), 3.0, 1.0)               # safety boundary
    w *= np.where(train_df["skin_band"].isin(["brown", "dark"]), 1.5, 1.0)  # fairness
    sampler = WeightedRandomSampler(torch.tensor(w.values, dtype=torch.double), len(train_df), replacement=True)

    train_tf = T.Compose([
        T.RandomResizedCrop(224, scale=(0.85, 1.0)),
        T.RandomHorizontalFlip(),
        T.RandomRotation(8),
        T.ColorJitter(brightness=0.2, contrast=0.2),  # NO hue/sat (would corrupt age/skin)
        T.ToTensor(), T.Normalize(MEAN, STD),
    ])
    eval_tf = T.Compose([T.Resize((224, 224)), T.ToTensor(), T.Normalize(MEAN, STD)])

    class FaceAges(Dataset):
        def __init__(self, frame, tf):
            self.f = frame.reset_index(drop=True); self.tf = tf
        def __len__(self):
            return len(self.f)
        def __getitem__(self, i):
            r = self.f.iloc[i]
            img = Image.open(os.path.join(data_dir, r["path"])).convert("RGB")
            return self.tf(img), torch.tensor(float(r["age"])), torch.tensor(1.0 if r["age"] < 18 else 0.0)

    train_loader = DataLoader(FaceAges(train_df, train_tf), batch_size=batch_size, sampler=sampler,
                              num_workers=nworkers, drop_last=True, pin_memory=True,
                              persistent_workers=True, prefetch_factor=4)

    # ---------------- model ----------------
    class AgeNet(nn.Module):
        def __init__(self):
            super().__init__()
            self.backbone = timm.create_model(backbone, pretrained=True, num_classes=0)
            d = self.backbone.num_features
            self.age = nn.Linear(d, 1); self.minor = nn.Linear(d, 1); self.logvar = nn.Linear(d, 1)
        def forward(self, x):
            f = self.backbone(x)
            return self.age(f).squeeze(1), self.minor(f).squeeze(1), self.logvar(f).squeeze(1)

    model = AgeNet().to(device).to(memory_format=torch.channels_last)  # tensor-core friendly
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    bce = nn.BCEWithLogitsLoss()
    steps = max(1, len(train_loader)) * epochs
    warmup = int(steps * warmup_frac)
    sched = torch.optim.lr_scheduler.LambdaLR(
        opt, lambda s: s / max(1, warmup) if s < warmup
        else 0.5 * (1 + math.cos(math.pi * (s - warmup) / max(1, steps - warmup))))

    use_wandb = bool(os.environ.get("WANDB_API_KEY"))
    if use_wandb:
        import wandb
        wandb.init(project=os.environ.get("WANDB_PROJECT", "kamari"), name=f"cnn-{backbone}",
                   resume="allow", config=dict(epochs=epochs, lr=lr, batch_size=batch_size,
                   backbone=backbone, gpu=GPU, train_rows=len(train_df), val_rows=len(val_df)))

    # ---------------- predict helper (aligned to frame order) ----------------
    @torch.no_grad()
    def predict(frame):
        model.eval()
        loader = DataLoader(FaceAges(frame, eval_tf), batch_size=batch_size, num_workers=nworkers,
                            shuffle=False, pin_memory=True)
        preds, p_un = [], []
        for x, _, _ in loader:
            x = x.to(device, non_blocking=True, memory_format=torch.channels_last)
            with torch.autocast("cuda", dtype=torch.bfloat16, enabled=device == "cuda"):
                a, m, _ = model(x)
            preds += a.float().cpu().tolist(); p_un += torch.sigmoid(m.float()).cpu().tolist()
        out = frame.copy(); out["pred"] = preds; out["p_under"] = p_un
        return out

    def quick(frame):  # light metrics for per-epoch selection
        if not len(frame):
            return {"mae": float("nan"), "mptr18": None}
        o = predict(frame); a = o["age"].values
        mae = float(np.mean(np.abs(o["pred"].values - a)))
        minors = a < 18
        mptr = float(np.mean(o["p_under"].values[minors] < 0.5)) if minors.any() else None
        return {"mae": round(mae, 3), "mptr18": (round(mptr, 4) if mptr is not None else None)}

    def full_eval(frame):  # comprehensive benchmark eval
        o = predict(frame[frame["age"].notna()])
        a, pred, pu = o["age"].values, o["pred"].values, o["p_under"].values
        abs_err = np.abs(pred - a)
        minors18, minors21, adults = a < 18, a < 21, a >= 18
        res = {
            "n": int(len(o)),
            "mae": round(float(abs_err.mean()), 3),
            "mptr18": round(float(np.mean(pu[minors18] < 0.5)), 4) if minors18.any() else None,
            "mptr21": round(float(np.mean(pred[minors21] >= 21)), 4) if minors21.any() else None,
            "adult_block_rate": round(float(np.mean(pu[adults] >= BLOCK_P)), 4) if adults.any() else None,
        }
        o["abs_err"] = abs_err
        for col in ["skin_band", "dataset", "gender"]:
            if col in o:
                res[f"mae_by_{col}"] = {str(k): round(float(v), 3) for k, v in o.groupby(col)["abs_err"].mean().items()}
        o["age_band"] = o["age"].map(_band)
        res["mae_by_age_band"] = {str(k): round(float(v), 3) for k, v in o.groupby("age_band")["abs_err"].mean().items()}
        # dark-skin minor-pass-through (the headline fairness/safety number)
        dark = o["skin_band"].isin(["brown", "dark"]).values
        dm = minors18 & dark
        res["mptr18_dark_skin"] = round(float(np.mean(pu[dm] < 0.5)), 4) if dm.any() else None
        return res

    def latency(n=60):
        model.eval(); x = torch.randn(1, 3, 224, 224, device=device)
        for _ in range(10):
            with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16, enabled=device == "cuda"):
                model(x)
        if device == "cuda":
            torch.cuda.synchronize()
        ts = []
        for _ in range(n):
            t0 = time.perf_counter()
            with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16, enabled=device == "cuda"):
                model(x)
            if device == "cuda":
                torch.cuda.synchronize()
            ts.append((time.perf_counter() - t0) * 1000)
        ts = np.array(ts)
        return {"device": device, "p50_ms": round(float(np.percentile(ts, 50)), 2),
                "p95_ms": round(float(np.percentile(ts, 95)), 2)}

    # ---------------- resume ----------------
    start_epoch, best_score, gstep = 0, float("inf"), 0
    last_path = os.path.join(CKPT, "last.pt")
    if os.path.exists(last_path):
        ck = torch.load(last_path, map_location=device)
        model.load_state_dict(ck["model"]); opt.load_state_dict(ck["opt"]); sched.load_state_dict(ck["sched"])
        start_epoch, best_score, gstep = ck["epoch"] + 1, ck.get("best_score", float("inf")), ck.get("gstep", 0)
        print(f"resumed from epoch {start_epoch}")

    # ---------------- train ----------------
    training_log = []
    for ep in range(start_epoch, epochs):
        model.train(); tot = 0.0
        for x, age, minor in train_loader:
            x = x.to(device, non_blocking=True, memory_format=torch.channels_last)
            age = age.to(device, non_blocking=True); minor = minor.to(device, non_blocking=True)
            with torch.autocast("cuda", dtype=torch.bfloat16, enabled=device == "cuda"):
                pa, pm, logvar = model(x)
                age_loss = (0.5 * torch.exp(-logvar) * (pa - age) ** 2 + 0.5 * logvar).mean()
                loss = age_loss + bce(pm, minor)
            opt.zero_grad(); loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0)
            opt.step(); sched.step(); gstep += 1; tot += loss.item()
            if use_wandb and gstep % 20 == 0:
                wandb.log({"train/loss": loss.item(), "train/lr": sched.get_last_lr()[0]}, step=gstep)
        val = quick(val_df)
        score = (val["mae"] if not math.isnan(val["mae"]) else 99) + 5.0 * (val["mptr18"] or 0)
        training_log.append({"epoch": ep + 1, "train_loss": tot / max(1, len(train_loader)), **{f"val_{k}": v for k, v in val.items()}})
        if use_wandb:
            wandb.log({"epoch": ep + 1, "val/mae": val["mae"], "val/mptr18": val["mptr18"] or 0, "val/score": score}, step=gstep)
        print(f"epoch {ep+1}/{epochs} loss={tot/max(1,len(train_loader)):.4f} val={val} score={score:.3f}")
        torch.save({"model": model.state_dict(), "opt": opt.state_dict(), "sched": sched.state_dict(),
                    "epoch": ep, "best_score": best_score, "gstep": gstep, "backbone": backbone}, last_path)
        if score < best_score:
            best_score = score
            torch.save(model.state_dict(), os.path.join(CKPT, "best.pt"))
            print(f"  new best (score={score:.3f}) -> best.pt")
        ckpt_vol.commit()

    # ---------------- finalize from BEST ----------------
    best_file = os.path.join(CKPT, "best.pt")
    if os.path.exists(best_file):
        model.load_state_dict(torch.load(best_file, map_location=device))
    model.eval()
    metrics = {"backbone": backbone, "gpu": GPU, "epochs": epochs, "train_rows": len(train_df),
               "val": quick(val_df) if len(val_df) else None,
               "benchmark": full_eval(bench) if bench is not None and len(bench) else None,
               "latency": latency()}
    if use_wandb and metrics["benchmark"]:
        b = metrics["benchmark"]
        wandb.log({"eval/mae": b["mae"], "eval/mptr18": b["mptr18"] or 0, "eval/mptr18_dark": b.get("mptr18_dark_skin") or 0,
                   "eval/adult_block": b.get("adult_block_rate") or 0,
                   "eval/lat_p50": metrics["latency"]["p50_ms"], "eval/lat_p95": metrics["latency"]["p95_ms"]})
    print("final metrics:", json.dumps(metrics, indent=2))

    # exports + reports
    dummy = torch.randn(1, 3, 224, 224, device=device)
    torch.onnx.export(model, dummy, os.path.join(CKPT, "cnn_v0.onnx"), input_names=["input"],
                      output_names=["age", "minor_logit", "logvar"],
                      dynamic_axes={"input": {0: "batch"}}, opset_version=17)
    thr = {"block_p_under_18": BLOCK_P, "challenge_age": 21, "uncertainty": 0.28, "min_quality": 0.40,
           "mean": MEAN, "std": STD}
    json.dump(thr, open(os.path.join(CKPT, "thresholds_v0.json"), "w"), indent=2)
    json.dump(metrics, open(os.path.join(CKPT, "metrics_v0.json"), "w"), indent=2)
    with open(os.path.join(CKPT, "training_log.jsonl"), "w") as fh:
        for row in training_log:
            fh.write(json.dumps(row) + "\n")
    open(os.path.join(CKPT, "benchmark_age_report_v0.md"), "w").write(_report(metrics))
    open(os.path.join(CKPT, "latency_report_v0.md"), "w").write(
        f"# Latency v0\n\n- device: {metrics['latency']['device']}\n"
        f"- p50: {metrics['latency']['p50_ms']} ms\n- p95: {metrics['latency']['p95_ms']} ms\n")
    ckpt_vol.commit()
    _push_to_hf(backbone, epochs, metrics)
    if use_wandb:
        wandb.finish()
    return metrics


def _md_table(d):
    if not d:
        return "_n/a_"
    return "\n".join(f"| {k} | {v} |" for k, v in d.items())


def _report(m):
    b = m.get("benchmark") or {}
    return f"""# Kámárí CNN Age Benchmark Report (v0)

Backbone **{m['backbone']}** · GPU {m['gpu']} · {m['epochs']} epochs · n={b.get('n', 'n/a')}

## Headline safety
| metric | value |
|---|---|
| MAE | {b.get('mae', 'n/a')} |
| Minor-Pass-Through @18 | {b.get('mptr18', 'n/a')} |
| **Minor-Pass-Through @18 (dark skin)** | {b.get('mptr18_dark_skin', 'n/a')} |
| Minor-Pass-Through @21 | {b.get('mptr21', 'n/a')} |
| Adult-Block Rate | {b.get('adult_block_rate', 'n/a')} |
| Latency p50 / p95 (ms) | {m['latency']['p50_ms']} / {m['latency']['p95_ms']} |

## MAE by skin band
| skin_band | MAE |
|---|---|
{_md_table(b.get('mae_by_skin_band'))}

## MAE by age band
| age_band | MAE |
|---|---|
{_md_table(b.get('mae_by_age_band'))}

## MAE by dataset
| dataset | MAE |
|---|---|
{_md_table(b.get('mae_by_dataset'))}

## MAE by gender
| gender | MAE |
|---|---|
{_md_table(b.get('mae_by_gender'))}

> Estimate, not a legal age determination. Benchmark is held-out (no train leakage).
"""


def _push_to_hf(backbone, epochs, metrics):
    from huggingface_hub import HfApi
    token, ns = os.environ["HF_TOKEN"], os.environ.get("HF_NAMESPACE", "kamari")
    repo = f"{ns}/cnn-age-v0"
    api = HfApi(token=token)
    api.create_repo(repo, repo_type="model", private=True, exist_ok=True)
    b = metrics.get("benchmark") or {}
    card = f"""---
license: other
tags: [kamari, age-estimation, cnn, onnx, african, fairness]
---

# Kámárí CNN Age Model v0

Multi-head age-gating model (**{backbone}**) → exact-age regression, under-18 probability,
heteroscedastic uncertainty. Selected for safety (MAE + heavy Minor-Pass-Through penalty).

## Benchmark (Kámárí-Safe Open v0, held-out)
- MAE: **{b.get('mae', 'n/a')}** · MPTR@18: **{b.get('mptr18', 'n/a')}**
  (dark-skin **{b.get('mptr18_dark_skin', 'n/a')}**) · Adult-Block: {b.get('adult_block_rate', 'n/a')}
- Latency p50/p95: {metrics['latency']['p50_ms']}/{metrics['latency']['p95_ms']} ms · {epochs} epochs

Full breakdowns in `benchmark_age_report_v0.md` + `latency_report_v0.md`. Artifacts: `best.pt`,
`cnn_v0.onnx`, `thresholds_v0.json`, `metrics_v0.json`, `training_log.jsonl`. Input 224×224 RGB.
**Out of scope:** legal age determination, face search.
"""
    for f in ["cnn_v0.onnx", "best.pt", "thresholds_v0.json", "metrics_v0.json", "training_log.jsonl",
              "benchmark_age_report_v0.md", "latency_report_v0.md"]:
        p = os.path.join(CKPT, f)
        if os.path.exists(p):
            api.upload_file(path_or_fileobj=p, path_in_repo=f, repo_id=repo, repo_type="model")
    api.upload_file(path_or_fileobj=card.encode(), path_in_repo="README.md", repo_id=repo, repo_type="model")
    print("pushed ->", repo)


@app.local_entrypoint()
def main(epochs: int = 30):
    print(train.remote(epochs=epochs))
