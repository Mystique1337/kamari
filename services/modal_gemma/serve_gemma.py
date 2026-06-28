"""Kámárí Gemma explanation layer — serving on Modal.

Loads base Gemma + the LoRA adapter from `<HF_NAMESPACE>/gemma-explain-lora-v0`,
generates a strict-JSON explanation, validates it, and (on failure) falls back to a
deterministic template so the gateway always gets schema-valid output.

Deploy:
    modal deploy services/modal_gemma/serve_gemma.py
    # -> set the URL as MODAL_GEMMA_ENDPOINT in the gateway

Request JSON (master plan §13.3):
    {"cnn_result": {...}, "policy_context": {"decision": "...", "reason_code": "...",
     "legal_threshold": 18, "challenge_threshold": 21}, "language": "en"}
"""
import os

import modal

GPU = os.environ.get("KAMARI_SERVE_GPU", "L4")  # 4B + adapter fits L4 (24GB); cheap to serve
MODEL_ID = os.environ.get("GEMMA_MODEL_ID", "google/gemma-4-E4B-it")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("torch", "transformers>=4.50", "peft>=0.12", "huggingface_hub",
                 "accelerate>=0.33", "fastapi[standard]")
)
app = modal.App("kamari-gemma-serve", image=image)
hf_secret = modal.Secret.from_name("kamari-hf")

VALID_DECISIONS = {"allow", "block", "secondary_check", "recapture"}
SAFETY_NOTE = "This is an estimate, not a legal age determination."


@app.cls(image=image, gpu=GPU, secrets=[hf_secret], min_containers=0)
class Gemma:
    @modal.enter()
    def load(self):
        import torch
        from peft import PeftModel
        from transformers import AutoModelForCausalLM, AutoTokenizer

        token, ns = os.environ["HF_TOKEN"], os.environ.get("HF_NAMESPACE", "kamari")
        adapter = f"{ns}/gemma-explain-lora-v0"
        self.tok = AutoTokenizer.from_pretrained(MODEL_ID, token=token)
        base = AutoModelForCausalLM.from_pretrained(
            MODEL_ID, torch_dtype=torch.bfloat16, device_map="auto",
            attn_implementation="eager", token=token)
        self.model = PeftModel.from_pretrained(base, adapter, token=token)
        self.model.eval()

    def _generate(self, payload: dict) -> dict:
        import json
        import torch

        cnn = payload.get("cnn_result", {})
        pol = payload.get("policy_context", {})
        language = payload.get("language", "en")
        prompt_in = json.dumps({**cnn, **pol, "language": language}, ensure_ascii=False)
        prompt = (f"<start_of_turn>user\nReturn a safe age-gating explanation as strict JSON "
                  f"matching the Kámárí schema.\nInput: {prompt_in}<end_of_turn>\n<start_of_turn>model\n")
        ids = self.tok(prompt, return_tensors="pt").to(self.model.device)
        with torch.no_grad():
            out = self.model.generate(**ids, max_new_tokens=256, do_sample=False)
        text = self.tok.decode(out[0][ids["input_ids"].shape[1]:], skip_special_tokens=True)
        return self._validate(text, pol, language)

    def _validate(self, text: str, pol: dict, language: str) -> dict:
        import json
        try:
            start, end = text.index("{"), text.rindex("}") + 1
            obj = json.loads(text[start:end])
            assert obj["decision"] in VALID_DECISIONS
            assert obj["reason_code"] == pol.get("reason_code", obj["reason_code"])
            obj.setdefault("language", language)
            obj["safety_note"] = SAFETY_NOTE  # never let the model weaken this
            return obj
        except Exception:
            # Deterministic fallback — the gateway must always get valid output.
            reason = pol.get("reason_code", "SECONDARY_CHECK_LOW_CONFIDENCE")
            return {
                "decision": pol.get("decision", "secondary_check"),
                "reason_code": reason,
                "user_message": "We need an additional age check before continuing.",
                "admin_summary": "Model output failed schema validation; used safe fallback.",
                "next_step": "request_id_or_guardian_flow",
                "language": language,
                "safety_note": SAFETY_NOTE,
            }

    @modal.fastapi_endpoint(method="POST", label="kamari-gemma-serve-endpoint")
    async def explain(self, payload: dict):
        return self._generate(payload)
