"""Kámárí CNN age model — serving on Modal.

Loads the licence-clean ONNX from Hugging Face `<HF_NAMESPACE>/cnn-age-v0` and exposes
a JSON endpoint the FastAPI gateway calls. Returns raw signals only; the policy/decision
engine lives in the gateway.

Deploy:
    modal deploy services/modal_age/serve_cnn.py
    # -> https://<ns>--kamari-cnn-serve-endpoint.modal.run  (set as MODAL_AGE_ENDPOINT)

Test:
    curl -F image=@selfie.jpg https://.../estimate
"""
import os

import modal

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("onnxruntime", "huggingface_hub", "pillow", "numpy", "fastapi[standard]")
)
app = modal.App("kamari-cnn-serve", image=image)
hf_secret = modal.Secret.from_name("kamari-hf")

MEAN = [0.485, 0.456, 0.406]
STD = [0.229, 0.224, 0.225]
MODEL_VERSION = "cnn_v0.1.0"


@app.cls(image=image, secrets=[hf_secret], min_containers=0)
class CNN:
    @modal.enter()
    def load(self):
        import json
        import numpy as np  # noqa: F401
        import onnxruntime as ort
        from huggingface_hub import hf_hub_download

        ns = os.environ.get("HF_NAMESPACE", "kamari")
        repo = f"{ns}/cnn-age-v0"
        onnx_path = hf_hub_download(repo, "cnn_v0.onnx", token=os.environ["HF_TOKEN"])
        try:
            thr_path = hf_hub_download(repo, "thresholds_v0.json", token=os.environ["HF_TOKEN"])
            self.thresholds = json.load(open(thr_path))
        except Exception:
            self.thresholds = {}
        self.sess = ort.InferenceSession(onnx_path, providers=["CPUExecutionProvider"])

    def _infer(self, image_bytes: bytes) -> dict:
        import io
        import numpy as np
        from PIL import Image

        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        # The app frames the face in a centre circle; centre-crop then resize 224.
        w, h = img.size
        s = min(w, h)
        img = img.crop(((w - s) // 2, (h - s) // 2, (w + s) // 2, (h + s) // 2)).resize((224, 224))
        arr = np.asarray(img, np.float32) / 255.0
        gray = arr.mean(2)
        quality = float(np.clip(np.var(np.gradient(gray)) * 50, 0, 1))  # cheap sharpness proxy
        x = ((arr - MEAN) / STD).transpose(2, 0, 1)[None].astype(np.float32)
        age, minor_logit, logvar = self.sess.run(None, {"input": x})
        p_under = 1.0 / (1.0 + np.exp(-float(minor_logit[0])))
        uncertainty = float(np.clip(np.exp(0.5 * float(logvar[0])) / 10.0, 0, 1))
        return {
            "estimated_age": round(float(age[0]), 1),
            "p_under_18": round(p_under, 3),
            "uncertainty": round(uncertainty, 3),
            "face_quality": round(quality, 3),
            "model_version": MODEL_VERSION,
        }

    @modal.fastapi_endpoint(method="POST", label="kamari-cnn-serve-endpoint")
    async def estimate(self, request):
        form = await request.form()
        upload = form.get("image")
        if upload is None:
            return {"error": "no image"}
        return self._infer(await upload.read())
