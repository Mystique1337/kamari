"""Kámárí Gemma explanation layer — serving on Modal.

Loads base Gemma 4 + the LoRA adapter from `<HF_NAMESPACE>/gemma-explain-lora-v0`,
merges the adapter, and generates a strict-JSON explanation with a **manual greedy decode**
(KV-cached) — the multimodal Gemma 4 `model.generate` has a tensor-shape bug, so we avoid it.
Invalid output falls back to a deterministic safe template so the gateway always gets valid JSON.

Deploy:
    modal deploy services/modal_gemma/serve_gemma.py
    # -> set the printed URL as MODAL_GEMMA_ENDPOINT in the gateway

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
    .pip_install("torch", "torchvision", "transformers>=4.50", "peft>=0.12", "huggingface_hub",
                 "accelerate>=0.33", "pillow", "fastapi[standard]")
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
        kw = dict(torch_dtype=torch.bfloat16, device_map="auto",
                  attn_implementation="eager", token=token)
        try:
            base = AutoModelForCausalLM.from_pretrained(MODEL_ID, **kw)
        except Exception:  # Gemma 4 is multimodal
            from transformers import AutoModelForImageTextToText
            base = AutoModelForImageTextToText.from_pretrained(MODEL_ID, **kw)
        merged = PeftModel.from_pretrained(base, adapter, token=token)
        self.model = merged.merge_and_unload()
        self.model.eval()

    def _greedy(self, prompt: str, max_new: int = 256) -> str:
        """Manual KV-cached greedy decode — robust to Gemma 4's logits shape."""
        import torch
        enc = self.tok(prompt, return_tensors="pt").to(self.model.device)
        attn = enc["attention_mask"]
        cur, past, out_ids = enc["input_ids"], None, []
        with torch.no_grad():
            for _ in range(max_new):
                res = self.model(input_ids=cur, attention_mask=attn, past_key_values=past, use_cache=True)
                logits = res.logits
                while logits.dim() > 2:
                    logits = logits[:, -1, :] if logits.dim() == 3 else logits[:, 0]
                nxt = int(logits[0].argmax())
                if self.tok.eos_token_id is not None and nxt == self.tok.eos_token_id:
                    break
                out_ids.append(nxt)
                past = res.past_key_values
                cur = torch.tensor([[nxt]], device=self.model.device)
                attn = torch.cat([attn, torch.ones((1, 1), dtype=attn.dtype, device=attn.device)], dim=-1)
        return self.tok.decode(out_ids, skip_special_tokens=True)

    def _run(self, payload: dict) -> dict:
        import json
        cnn = payload.get("cnn_result", {})
        pol = payload.get("policy_context", {})
        language = payload.get("language", "en")
        prompt_in = json.dumps({**cnn, **pol, "language": language}, ensure_ascii=False)
        msgs = [{"role": "user", "content":
                 "Return a safe age-gating explanation as strict JSON matching the Kámárí schema.\n"
                 f"Input: {prompt_in}"}]
        prompt = self.tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
        text = self._greedy(prompt)
        return self._validate(text, pol, language)

    def _validate(self, text: str, pol: dict, language: str) -> dict:
        import json
        try:
            obj = json.loads(text[text.index("{"):text.rindex("}") + 1])
            assert obj["decision"] in VALID_DECISIONS
            obj.setdefault("language", language)
            obj["safety_note"] = SAFETY_NOTE
            return obj
        except Exception:
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
        return self._run(payload)
