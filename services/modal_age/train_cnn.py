"""Kámárí CNN age model — training on Modal (GPU).

Trains a small multi-head age model, exports ONNX, and pushes weights + a model card
to Hugging Face `<HF_NAMESPACE>/cnn-age-v0`.

Data (licence-safe): training crops are NOT public. Populate a private Modal Volume
`kamari-data` with the processed outputs from the Colab notebooks:

    modal volume create kamari-data
    modal volume put kamari-data data/manifests/manifest_train_v0.parquet manifest_train_v0.parquet
    modal volume put kamari-data data/manifests/manifest_benchmark_v0.parquet manifest_benchmark_v0.parquet
    modal volume put kamari-data data/processed/crops_224 crops_224

Secrets:
    modal secret create kamari-hf HF_TOKEN=... HF_NAMESPACE=...

Run:
    modal run services/modal_age/train_cnn.py --epochs 20
"""
import os

import modal

GPU = os.environ.get("KAMARI_GPU", "A100-80GB")  # set "H100" for fastest

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "torch", "torchvision", "timm", "onnx", "onnxruntime",
        "huggingface_hub", "pandas", "pyarrow", "pillow", "numpy", "scikit-learn",
    )
)
app = modal.App("kamari-cnn-train", image=image)
data_vol = modal.Volume.from_name("kamari-data", create_if_missing=True)
ckpt_vol = modal.Volume.from_name("kamari-cnn", create_if_missing=True)
hf_secret = modal.Secret.from_name("kamari-hf")

MEAN = [0.485, 0.456, 0.406]
STD = [0.229, 0.224, 0.225]


@app.function(gpu=GPU, timeout=60 * 60 * 8,
              volumes={"/data": data_vol, "/ckpt": ckpt_vol}, secrets=[hf_secret])
def train(epochs: int = 20, backbone: str = "mobilenetv3_large_100",
          lr: float = 3e-4, batch_size: int = 128):
    import json
    import numpy as np
    import pandas as pd
    import timm
    import torch
    import torch.nn as nn
    from PIL import Image
    from torch.utils.data import Dataset, DataLoader, WeightedRandomSampler

    device = "cuda" if torch.cuda.is_available() else "cpu"
    df = pd.read_parquet("/data/manifest_train_v0.parquet")
    df = df[df["age"].notna()].reset_index(drop=True)
    print(f"training rows: {len(df)}")

    class FaceAges(Dataset):
        def __init__(self, frame):
            self.f = frame.reset_index(drop=True)

        def __len__(self):
            return len(self.f)

        def __getitem__(self, i):
            r = self.f.iloc[i]
            p = r["path"] if os.path.isabs(r["path"]) else f"/data/{os.path.basename(r['path'])}"
            if not os.path.exists(p):
                p = f"/data/crops_224/{os.path.basename(r['path'])}"
            img = np.asarray(Image.open(p).convert("RGB").resize((224, 224)), np.float32) / 255.0
            img = (img - MEAN) / STD
            x = torch.from_numpy(img.transpose(2, 0, 1)).float()
            age = torch.tensor(float(r["age"]), dtype=torch.float32)
            minor = torch.tensor(1.0 if r["age"] < 18 else 0.0, dtype=torch.float32)
            return x, age, minor

    # Oversample the 13–21 boundary band — the safety-critical region.
    w = np.where((df["age"] >= 13) & (df["age"] <= 21), 3.0, 1.0)
    sampler = WeightedRandomSampler(torch.tensor(w, dtype=torch.double), len(df), replacement=True)
    loader = DataLoader(FaceAges(df), batch_size=batch_size, sampler=sampler, num_workers=8, drop_last=True)

    class AgeNet(nn.Module):
        def __init__(self):
            super().__init__()
            self.backbone = timm.create_model(backbone, pretrained=True, num_classes=0)
            d = self.backbone.num_features
            self.age = nn.Linear(d, 1)        # exact-age regression
            self.minor = nn.Linear(d, 1)      # under-18 logit
            self.logvar = nn.Linear(d, 1)     # heteroscedastic uncertainty

        def forward(self, x):
            f = self.backbone(x)
            return self.age(f).squeeze(1), self.minor(f).squeeze(1), self.logvar(f).squeeze(1)

    model = AgeNet().to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    bce = nn.BCEWithLogitsLoss()

    for ep in range(epochs):
        model.train()
        tot = 0.0
        for x, age, minor in loader:
            x, age, minor = x.to(device), age.to(device), minor.to(device)
            pred_age, pred_minor, logvar = model(x)
            # Gaussian NLL for age (uncertainty-aware) + BCE for the under-18 head.
            age_loss = (0.5 * torch.exp(-logvar) * (pred_age - age) ** 2 + 0.5 * logvar).mean()
            loss = age_loss + bce(pred_minor, minor)
            opt.zero_grad(); loss.backward(); opt.step()
            tot += loss.item()
        print(f"epoch {ep + 1}/{epochs}  loss={tot / len(loader):.4f}")

    os.makedirs("/ckpt", exist_ok=True)
    torch.save(model.state_dict(), "/ckpt/best.pt")

    # Export ONNX (single 224x224 RGB, pre-normalized by the server).
    model.eval()
    dummy = torch.randn(1, 3, 224, 224, device=device)
    onnx_path = "/ckpt/cnn_v0.onnx"
    torch.onnx.export(model, dummy, onnx_path, input_names=["input"],
                      output_names=["age", "minor_logit", "logvar"],
                      dynamic_axes={"input": {0: "batch"}}, opset_version=17)

    thresholds = {"block_p_under_18": 0.70, "challenge_age": 21, "uncertainty": 0.28,
                  "min_quality": 0.40, "mean": MEAN, "std": STD}
    with open("/ckpt/thresholds_v0.json", "w") as fh:
        json.dump(thresholds, fh, indent=2)
    ckpt_vol.commit()

    _push_to_hf(onnx_path, "/ckpt/best.pt", "/ckpt/thresholds_v0.json", backbone, epochs)
    return {"epochs": epochs, "rows": len(df), "onnx": onnx_path}


def _push_to_hf(onnx_path, pt_path, thr_path, backbone, epochs):
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

- Input: 224×224 RGB, normalized with ImageNet mean/std.
- Outputs: `age`, `minor_logit` (→ p_under_18 via sigmoid), `logvar` (→ uncertainty).
- Trained {epochs} epochs; 13–21 boundary oversampled 3×.

**Out of scope:** legal age determination, face search. This is an estimate.
See thresholds in `thresholds_v0.json`. Benchmark: Kámárí-Safe Open v0.
"""
    for local, name in [(onnx_path, "cnn_v0.onnx"), (pt_path, "best.pt"),
                        (thr_path, "thresholds_v0.json")]:
        api.upload_file(path_or_fileobj=local, path_in_repo=name, repo_id=repo, repo_type="model")
    api.upload_file(path_or_fileobj=card.encode(), path_in_repo="README.md",
                    repo_id=repo, repo_type="model")
    print("pushed ->", repo)


@app.local_entrypoint()
def main(epochs: int = 20):
    print(train.remote(epochs=epochs))
