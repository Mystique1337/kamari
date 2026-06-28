"""Kámárí CNN age model - serving on Modal (CPU).

Loads the trained PyTorch checkpoint (`best.pt`) from `<HF_NAMESPACE>/cnn-age-v0` and runs
CPU inference. (The ONNX export shipped weights as an external sidecar that doesn't survive
the HF download, so we serve the complete `best.pt` directly - still fast on CPU.)

Returns raw signals only; the policy/decision engine lives in the gateway.

Deploy:
    modal deploy services/modal_age/serve_cnn.py
    # -> https://<ns>--kamari-cnn-serve-endpoint.modal.run  (set as MODAL_AGE_ENDPOINT)
Test:
    curl -F image=@selfie.jpg https://.../estimate
"""
import os

import modal
from fastapi import File, UploadFile

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("torch", "timm", "huggingface_hub", "pillow", "numpy", "fastapi[standard]")
)
app = modal.App("kamari-cnn-serve", image=image)
hf_secret = modal.Secret.from_name("kamari-hf")

MEAN = [0.485, 0.456, 0.406]
STD = [0.229, 0.224, 0.225]
MODEL_VERSION = "cnn_v0.1.0"
BACKBONE = os.environ.get("CNN_BACKBONE", "tf_efficientnetv2_s")


# Always-on: keep one warm container so age checks never pay a cold start.
# Override with KAMARI_CNN_MIN_CONTAINERS=0 to let it scale to zero and save cost.
MIN_CONTAINERS = int(os.environ.get("KAMARI_CNN_MIN_CONTAINERS", "1"))


@app.cls(image=image, cpu=2.0, secrets=[hf_secret],
         min_containers=MIN_CONTAINERS, scaledown_window=300)
class CNN:
    @modal.enter()
    def load(self):
        import torch
        import torch.nn as nn
        import timm
        from huggingface_hub import hf_hub_download

        class AgeNet(nn.Module):
            def __init__(self):
                super().__init__()
                self.backbone = timm.create_model(BACKBONE, pretrained=False, num_classes=0)
                d = self.backbone.num_features
                self.age = nn.Linear(d, 1)
                self.minor = nn.Linear(d, 1)
                self.logvar = nn.Linear(d, 1)

            def forward(self, x):
                f = self.backbone(x)
                return self.age(f).squeeze(1), self.minor(f).squeeze(1), self.logvar(f).squeeze(1)

        ns = os.environ.get("HF_NAMESPACE", "kamari")
        pt = hf_hub_download(f"{ns}/cnn-age-v0", "best.pt", token=os.environ["HF_TOKEN"])
        model = AgeNet()
        model.load_state_dict(torch.load(pt, map_location="cpu"))
        model.eval()
        torch.set_num_threads(max(1, os.cpu_count() or 2))
        self.torch = torch
        self.model = model

    def _infer(self, image_bytes: bytes) -> dict:
        import io
        import numpy as np
        from PIL import Image

        # Undecodable / corrupt upload: return a graceful low-quality signal so the
        # gateway policy asks for a recapture, rather than throwing a 500.
        try:
            img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        except Exception:
            return {"estimated_age": 0.0, "p_under_18": 0.5, "uncertainty": 1.0,
                    "face_quality": 0.0, "model_version": MODEL_VERSION}
        w, h = img.size
        s = min(w, h)
        img = img.crop(((w - s) // 2, (h - s) // 2, (w + s) // 2, (h + s) // 2)).resize((224, 224))
        arr = np.asarray(img, np.float32) / 255.0
        quality = float(np.clip(np.var(np.gradient(arr.mean(2))) * 50, 0, 1))
        x = ((arr - MEAN) / STD).transpose(2, 0, 1)[None].astype(np.float32)
        with self.torch.no_grad():
            age, minor_logit, logvar = self.model(self.torch.from_numpy(x))
        p_under = 1.0 / (1.0 + float(np.exp(-float(minor_logit[0]))))
        uncertainty = float(np.clip(float(np.exp(0.5 * float(logvar[0]))) / 10.0, 0, 1))
        return {
            "estimated_age": round(float(age[0]), 1),
            "p_under_18": round(p_under, 3),
            "uncertainty": round(uncertainty, 3),
            "face_quality": round(quality, 3),
            "model_version": MODEL_VERSION,
        }

    @modal.fastapi_endpoint(method="POST", label="kamari-cnn-serve-endpoint")
    async def estimate(self, image: UploadFile = File(...)):
        return self._infer(await image.read())
