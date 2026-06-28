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
    .apt_install("libgl1", "libglib2.0-0")  # OpenCV runtime libs
    .pip_install("torch", "timm", "huggingface_hub", "pillow", "numpy",
                 "opencv-python-headless", "fastapi[standard]")
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

        # Face detector: the model trained on face crops, so we detect + crop the face
        # before inference (matches training) and base quality on the real face, not the
        # whole frame. This stops every photo from failing the quality gate.
        import cv2
        self.cv2 = cv2
        self.cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

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
        cv2 = self.cv2
        gray = cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2GRAY)
        faces = self.cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5,
                                              minSize=(48, 48))

        # No face found: ask for a recapture (quality 0) rather than guessing on a non-face.
        if len(faces) == 0:
            return {"estimated_age": 0.0, "p_under_18": 0.5, "uncertainty": 1.0,
                    "face_quality": 0.0, "faces_detected": 0, "model_version": MODEL_VERSION}

        # Use the largest face. Crop with a 30% margin (matches the training crops).
        fx, fy, fw, fh = (int(v) for v in max(faces, key=lambda f: f[2] * f[3]))
        mx, my = int(fw * 0.3), int(fh * 0.3)
        x0, y0 = max(0, fx - mx), max(0, fy - my)
        x1, y1 = min(w, fx + fw + mx), min(h, fy + fh + my)
        face = img.crop((x0, y0, x1, y1)).resize((224, 224))

        arr = np.asarray(face, np.float32) / 255.0
        # Quality from face sharpness (Laplacian variance), baselined so a detected face
        # comfortably passes the gate and only a genuinely blurry face is asked to retake.
        sharp = float(cv2.Laplacian(cv2.cvtColor(np.asarray(face), cv2.COLOR_RGB2GRAY),
                                    cv2.CV_64F).var())
        quality = float(np.clip(0.55 + sharp / 800.0, 0.0, 1.0))

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
            "faces_detected": int(len(faces)),
            "model_version": MODEL_VERSION,
        }

    @modal.fastapi_endpoint(method="POST", label="kamari-cnn-serve-endpoint")
    async def estimate(self, image: UploadFile = File(...)):
        return self._infer(await image.read())
