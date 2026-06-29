"""Kamari CNN age model - standalone CPU server for self-hosting (no Modal).

Loads the public `best.pt` from Hugging Face (`Shinzmann/cnn-age-v0`), detects and crops the
face with OpenCV, and returns raw age signals. Same response contract as the Modal endpoint, so
the gateway can point MODAL_AGE_ENDPOINT at this service.

Run:
    pip install -r requirements.txt
    uvicorn cnn_server:app --host 0.0.0.0 --port 8001
"""
import io
import os

import cv2
import numpy as np
import timm
import torch
import torch.nn as nn
from fastapi import FastAPI, File, UploadFile
from huggingface_hub import hf_hub_download
from PIL import Image

MEAN = [0.485, 0.456, 0.406]
STD = [0.229, 0.224, 0.225]
MODEL_VERSION = "cnn_v0.1.0"
BACKBONE = os.environ.get("CNN_BACKBONE", "tf_efficientnetv2_s")
HF_REPO = os.environ.get("CNN_HF_REPO", "Shinzmann/cnn-age-v0")


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


app = FastAPI(title="Kamari CNN (self-host)")
_model: AgeNet | None = None
_cascade = None


def _load():
    global _model, _cascade
    if _model is not None:
        return
    pt = hf_hub_download(HF_REPO, "best.pt", token=os.environ.get("HF_TOKEN") or None)
    m = AgeNet()
    m.load_state_dict(torch.load(pt, map_location="cpu"))
    m.eval()
    torch.set_num_threads(max(1, os.cpu_count() or 2))
    _model = m
    _cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")


@app.on_event("startup")
def _startup():
    _load()


@app.get("/health")
def health():
    return {"status": "ok", "model_version": MODEL_VERSION}


def _infer(image_bytes: bytes) -> dict:
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception:
        return {"estimated_age": 0.0, "p_under_18": 0.5, "uncertainty": 1.0,
                "face_quality": 0.0, "model_version": MODEL_VERSION}
    w, h = img.size
    gray = cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2GRAY)
    faces = _cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(48, 48))
    if len(faces) == 0:
        return {"estimated_age": 0.0, "p_under_18": 0.5, "uncertainty": 1.0,
                "face_quality": 0.0, "faces_detected": 0, "model_version": MODEL_VERSION}
    fx, fy, fw, fh = (int(v) for v in max(faces, key=lambda f: f[2] * f[3]))
    mx, my = int(fw * 0.3), int(fh * 0.3)
    x0, y0 = max(0, fx - mx), max(0, fy - my)
    x1, y1 = min(w, fx + fw + mx), min(h, fy + fh + my)
    face = img.crop((x0, y0, x1, y1)).resize((224, 224))
    arr = np.asarray(face, np.float32) / 255.0
    sharp = float(cv2.Laplacian(cv2.cvtColor(np.asarray(face), cv2.COLOR_RGB2GRAY), cv2.CV_64F).var())
    quality = float(np.clip(0.55 + sharp / 800.0, 0.0, 1.0))
    x = ((arr - MEAN) / STD).transpose(2, 0, 1)[None].astype(np.float32)
    with torch.no_grad():
        age, minor_logit, logvar = _model(torch.from_numpy(x))
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


@app.post("/estimate")
async def estimate(image: UploadFile = File(...)):
    return _infer(await image.read())
