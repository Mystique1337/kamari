"""Kámárí CNN age model — training on Modal (GPU).

Pulls the dataset from Hugging Face `<HF_NAMESPACE>/kamari-faces-v0` (built by the data
notebook), trains a small multi-head age model, evaluates on the frozen benchmark, tracks
everything in Weights & Biases, then uploads **weights + ONNX + thresholds + metrics +
training log + model card** to `<HF_NAMESPACE>/cnn-age-v0`.

Secrets (W&B optional — include WANDB_API_KEY in the same secret to enable tracking):
    modal secret create kamari-hf HF_TOKEN=... HF_NAMESPACE=... WANDB_API_KEY=... WANDB_PROJECT=kamari

Run:
    modal run services/modal_age/train_cnn.py --epochs 20
"""
import os

import modal

GPU = os.environ.get("KAMARI_GPU", "A100-80GB")  # "H100" for fastest

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


@app.function(gpu=GPU, timeout=60 * 60 * 8, volumes={"/ckpt": ckpt_vol}, secrets=[hf_secret])
def train(epochs: int = 20, backbone: str = "mobilenetv3_large_100",
          lr: float = 3e-4, batch_size: int = 128):
    import json
    import numpy as np
    import pandas as pd
    import timm
    import torch
    import torch.nn as nn
    from huggingface_hub import snapshot_download
    from PIL import Image
    from torch.utils.data import Dataset, DataLoader, WeightedRandomSampler

    token, ns = os.environ["HF_TOKEN"], os.environ.get("HF_NAMESPACE", "kamari")
    device = "cuda" if torch.cuda.is_available() else "cpu"

    # --- Pull dataset from HF ---
    data_dir = snapshot_download(f"{ns}/kamari-faces-v0", repo_type="dataset", token=token)
    df = pd.read_parquet(os.path.join(data_dir, "manifests", "manifest_train_v0.parquet"))
    df = df[df["age"].notna()].reset_index(drop=True)
    bench_path = os.path.join(data_dir, "manifests", "manifest_benchmark_v0.parquet")
    bench = pd.read_parquet(bench_path) if os.path.exists(bench_path) else None
    print(f"train rows: {len(df)} | benchmark rows: {0 if bench is None else len(bench)}")

    # --- W&B (optional) ---
    use_wandb = bool(os.environ.get("WANDB_API_KEY"))
    if use_wandb:
        import wandb
        wandb.init(project=os.environ.get("WANDB_PROJECT", "kamari"),
                   name=f"cnn-{backbone}",
                   config={"epochs": epochs, "lr": lr, "batch_size": batch_size,
                           "backbone": backbone, "train_rows": len(df)})

    def load_img(rel):
        p = os.path.join(data_dir, rel)
        img = np.asarray(Image.open(p).convert("RGB").resize((224, 224)), np.float32) / 255.0
        return ((img - MEAN) / STD).transpose(2, 0, 1)

    class FaceAges(Dataset):
        def __init__(self, frame):
            self.f = frame.reset_index(drop=True)

        def __len__(self):
            return len(self.f)

        def __getitem__(self, i):
            r = self.f.iloc[i]
            x = torch.from_numpy(load_img(r["path"])).float()
            return x, torch.tensor(float(r["age"])), torch.tensor(1.0 if r["age"] < 18 else 0.0)

    w = np.where((df["age"] >= 13) & (df["age"] <= 21), 3.0, 1.0)  # oversample boundary
    sampler = WeightedRandomSampler(torch.tensor(w, dtype=torch.double), len(df), replacement=True)
    loader = DataLoader(FaceAges(df), batch_size=batch_size, sampler=sampler, num_workers=8, drop_last=True)

    class AgeNet(nn.Module):
        def __init__(self):
            super().__init__()
            self.backbone = timm.create_model(backbone, pretrained=True, num_classes=0)
            d = self.backbone.num_features
            self.age = nn.Linear(d, 1)
            self.minor = nn.Linear(d, 1)
            self.logvar = nn.Linear(d, 1)

        def forward(self, x):
            f = self.backbone(x)
            return self.age(f).squeeze(1), self.minor(f).squeeze(1), self.logvar(f).squeeze(1)

    model = AgeNet().to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    bce = nn.BCEWithLogitsLoss()

    training_log = []
    for ep in range(epochs):
        model.train(); tot = 0.0
        for x, age, minor in loader:
            x, age, minor = x.to(device), age.to(device), minor.to(device)
            pred_age, pred_minor, logvar = model(x)
            age_loss = (0.5 * torch.exp(-logvar) * (pred_age - age) ** 2 + 0.5 * logvar).mean()
            loss = age_loss + bce(pred_minor, minor)
            opt.zero_grad(); loss.backward(); opt.step()
            tot += loss.item()
        epoch_loss = tot / len(loader)
        training_log.append({"epoch": ep + 1, "loss": epoch_loss})
        if use_wandb:
            wandb.log({"epoch": ep + 1, "train_loss": epoch_loss})
        print(f"epoch {ep + 1}/{epochs}  loss={epoch_loss:.4f}")

    # --- Eval on the frozen benchmark ---
    metrics = {"backbone": backbone, "epochs": epochs, "train_rows": len(df)}
    if bench is not None and len(bench):
        model.eval()
        ages, preds, p_unders, minors = [], [], [], []
        with torch.no_grad():
            for _, r in bench[bench["age"].notna()].iterrows():
                try:
                    x = torch.from_numpy(load_img(r["path"])).float()[None].to(device)
                except Exception:
                    continue
                a, m, _ = model(x)
                ages.append(float(r["age"])); preds.append(float(a[0]))
                p_unders.append(1 / (1 + np.exp(-float(m[0])))); minors.append(r["age"] < 18)
        if ages:
            ages, preds = np.array(ages), np.array(preds)
            p_unders, minors = np.array(p_unders), np.array(minors)
            mae = float(np.mean(np.abs(preds - ages)))
            # Minor-Pass-Through Rate @18: true minors predicted as adult (p_under < 0.5)
            mptr = float(np.mean(p_unders[minors] < 0.5)) if minors.any() else None
            metrics.update({"mae": round(mae, 3), "minor_pass_through_rate_18": mptr,
                            "benchmark_rows": int(len(ages))})
            if use_wandb:
                wandb.log({"eval/mae": mae, "eval/minor_pass_through_rate_18": mptr})
    print("metrics:", metrics)

    # --- Save artifacts ---
    os.makedirs("/ckpt", exist_ok=True)
    torch.save(model.state_dict(), "/ckpt/best.pt")
    model.eval()
    dummy = torch.randn(1, 3, 224, 224, device=device)
    torch.onnx.export(model, dummy, "/ckpt/cnn_v0.onnx", input_names=["input"],
                      output_names=["age", "minor_logit", "logvar"],
                      dynamic_axes={"input": {0: "batch"}}, opset_version=17)
    thresholds = {"block_p_under_18": 0.70, "challenge_age": 21, "uncertainty": 0.28,
                  "min_quality": 0.40, "mean": MEAN, "std": STD}
    json.dump(thresholds, open("/ckpt/thresholds_v0.json", "w"), indent=2)
    json.dump(metrics, open("/ckpt/metrics_v0.json", "w"), indent=2)
    with open("/ckpt/training_log.jsonl", "w") as fh:
        for row in training_log:
            fh.write(json.dumps(row) + "\n")
    ckpt_vol.commit()

    _push_to_hf(backbone, epochs, metrics)
    if use_wandb:
        wandb.finish()
    return metrics


def _push_to_hf(backbone, epochs, metrics):
    from huggingface_hub import HfApi
    token, ns = os.environ["HF_TOKEN"], os.environ.get("HF_NAMESPACE", "kamari")
    repo = f"{ns}/cnn-age-v0"
    api = HfApi(token=token)
    api.create_repo(repo, repo_type="model", private=True, exist_ok=True)
    card = f"""---
license: other
tags: [kamari, age-estimation, cnn, onnx, african, fairness]
---

# Kámárí CNN Age Model v0

Small multi-head age-gating model ({backbone}) → exact-age regression, under-18
probability, and heteroscedastic uncertainty. Exported to ONNX for serving.

## Evaluation (Kámárí-Safe Open v0)
- MAE: **{metrics.get('mae', 'n/a')}**
- Minor-Pass-Through Rate @18: **{metrics.get('minor_pass_through_rate_18', 'n/a')}**
- Benchmark rows: {metrics.get('benchmark_rows', 'n/a')} · epochs: {epochs}

Artifacts: `best.pt`, `cnn_v0.onnx`, `thresholds_v0.json`, `metrics_v0.json`,
`training_log.jsonl`. Input 224×224 RGB (ImageNet norm). 13–21 boundary oversampled 3×.
**Out of scope:** legal age determination, face search. This is an estimate.
"""
    for f in ["cnn_v0.onnx", "best.pt", "thresholds_v0.json", "metrics_v0.json", "training_log.jsonl"]:
        api.upload_file(path_or_fileobj=f"/ckpt/{f}", path_in_repo=f, repo_id=repo, repo_type="model")
    api.upload_file(path_or_fileobj=card.encode(), path_in_repo="README.md", repo_id=repo, repo_type="model")
    print("pushed ->", repo)


@app.local_entrypoint()
def main(epochs: int = 20):
    print(train.remote(epochs=epochs))
