"""Kámárí Gemma explanation layer — best-practice QLoRA fine-tune on Modal (GPU).

Pulls SFT data from HF `<HF_NAMESPACE>/gemma-sft-v0`, QLoRA-fine-tunes Gemma 4B, runs a
comprehensive eval (JSON validity, schema compliance, policy/decision consistency,
language correctness), tracks in W&B, checkpoints every epoch (resumable), and uploads the
adapter + metrics + reports + card to `<HF_NAMESPACE>/gemma-explain-lora-v0`.

Gemma EXPLAINS decisions — it never estimates age and never invents decision codes.

Prereqs:
    python training/gemma/build_sft_dataset.py --n 6000
    huggingface-cli upload <ns>/gemma-sft-v0 training/gemma/sft_train.jsonl sft_train.jsonl --repo-type dataset
    huggingface-cli upload <ns>/gemma-sft-v0 training/gemma/sft_eval.jsonl  sft_eval.jsonl  --repo-type dataset
    modal secret create kamari-hf HF_TOKEN=... HF_NAMESPACE=... WANDB_API_KEY=... WANDB_PROJECT=kamari
Run:
    modal run services/modal_gemma/train_gemma.py --epochs 3
"""
import os

import modal

GPU = os.environ.get("KAMARI_GPU", "H200")  # user has H200
# Gemma 4 (effective-4B). Multimodal checkpoint used text-only. HF_TOKEN must accept the licence.
MODEL_ID = os.environ.get("GEMMA_MODEL_ID", "google/gemma-4-E4B-it")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "torch", "torchvision", "transformers>=4.50", "peft>=0.12", "trl>=0.11", "datasets>=2.20",
        "bitsandbytes>=0.43", "accelerate>=0.33", "huggingface_hub", "wandb", "pillow",
    )
    .env({"PYTORCH_CUDA_ALLOC_CONF": "expandable_segments:True"})
)
app = modal.App("kamari-gemma-train", image=image)
out_vol = modal.Volume.from_name("kamari-gemma", create_if_missing=True)
hf_secret = modal.Secret.from_name("kamari-hf")
OUT = "/out"

VALID_DECISIONS = {"allow", "block", "secondary_check", "recapture"}
VALID_REASONS = {
    "ALLOW", "BLOCK_LIKELY_MINOR", "SECONDARY_CHECK_NEAR_THRESHOLD",
    "SECONDARY_CHECK_LOW_CONFIDENCE", "RECAPTURE_LOW_QUALITY", "RECAPTURE_NO_FACE",
    "RECAPTURE_MULTIPLE_FACES", "ERROR_UNSUPPORTED_IMAGE",
}
VALID_NEXT = {"proceed", "request_id_or_guardian_flow", "retake_photo", "manual_review"}
REQUIRED_KEYS = {"decision", "reason_code", "user_message", "admin_summary", "next_step", "language", "safety_note"}


@app.function(gpu=GPU, cpu=16.0, memory=131072, timeout=60 * 60 * 12,
              volumes={OUT: out_vol}, secrets=[hf_secret])
def train(epochs: int = 3, lr: float = 2e-4, rank: int = 32):
    import json
    import torch
    from datasets import load_dataset
    from huggingface_hub import snapshot_download
    from peft import LoraConfig
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    from transformers.trainer_utils import get_last_checkpoint
    from trl import SFTConfig, SFTTrainer

    token, ns = os.environ["HF_TOKEN"], os.environ.get("HF_NAMESPACE", "kamari")
    use_wandb = bool(os.environ.get("WANDB_API_KEY"))
    if use_wandb:
        os.environ.setdefault("WANDB_PROJECT", os.environ.get("WANDB_PROJECT", "kamari"))

    sft_dir = snapshot_download(f"{ns}/gemma-sft-v0", repo_type="dataset", token=token)
    ds = load_dataset("json", data_files={
        "train": os.path.join(sft_dir, "sft_train.jsonl"),
        "eval": os.path.join(sft_dir, "sft_eval.jsonl"),
    })

    tok = AutoTokenizer.from_pretrained(MODEL_ID, token=token)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                             bnb_4bit_compute_dtype=torch.bfloat16, bnb_4bit_use_double_quant=True)
    _load_kw = dict(quantization_config=bnb, device_map="auto", torch_dtype=torch.bfloat16,
                    attn_implementation="eager", token=token)
    try:
        model = AutoModelForCausalLM.from_pretrained(MODEL_ID, **_load_kw)
    except Exception as e:  # Gemma 4 / E4B are multimodal -> generic loader, train text-only
        print("AutoModelForCausalLM failed; loading via AutoModelForImageTextToText:", e)
        from transformers import AutoModelForImageTextToText
        model = AutoModelForImageTextToText.from_pretrained(MODEL_ID, **_load_kw)

    def to_text(ex, with_answer=True):
        user = f"{ex['instruction']}\nInput: {json.dumps(ex['input'], ensure_ascii=False)}"
        msgs = [{"role": "user", "content": user}]
        if with_answer:
            msgs.append({"role": "assistant", "content": json.dumps(ex["output"], ensure_ascii=False)})
        return tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=not with_answer)

    def formatting(example):  # TRL 1.x passes ONE example and expects ONE string back
        return to_text(example)

    # Gemma 4 wraps projections in Gemma4ClippableLinear; "all-linear" targets the real
    # inner nn.Linear/Linear4bit layers (named targets would hit the unsupported wrapper).
    lora = LoraConfig(r=rank, lora_alpha=rank * 2, lora_dropout=0.05, bias="none",
                      task_type="CAUSAL_LM", target_modules="all-linear")
    cfg = SFTConfig(
        output_dir=OUT + "/adapter", num_train_epochs=epochs,
        per_device_train_batch_size=8, gradient_accumulation_steps=4,
        learning_rate=lr, lr_scheduler_type="cosine", warmup_ratio=0.03, weight_decay=0.01,
        bf16=True, tf32=True, gradient_checkpointing=True,
        gradient_checkpointing_kwargs={"use_reentrant": False},
        dataloader_num_workers=8, dataloader_pin_memory=True,
        packing=False, neftune_noise_alpha=5, max_length=512,  # no packing (clean + low mem); short JSON
        logging_steps=20, eval_strategy="epoch", save_strategy="epoch", save_total_limit=2,
        load_best_model_at_end=True, metric_for_best_model="eval_loss", greater_is_better=False,
        run_name=f"gemma4b-lora-r{rank}", report_to=["wandb"] if use_wandb else [],
    )
    trainer = SFTTrainer(model=model, args=cfg, train_dataset=ds["train"],
                         eval_dataset=ds["eval"], peft_config=lora, formatting_func=formatting,
                         processing_class=tok)  # force text tokenizer; skip multimodal processor
    resume = get_last_checkpoint(cfg.output_dir) if os.path.isdir(cfg.output_dir) else None
    trainer.train(resume_from_checkpoint=resume)
    trainer.save_model(OUT + "/adapter")
    tok.save_pretrained(OUT + "/adapter")
    out_vol.commit()

    # ---------------- comprehensive eval (non-fatal: never lose the trained adapter) ----------------
    try:
        eval_metrics = _evaluate(trainer.model, tok, ds["eval"], to_text)
    except Exception as e:
        print("post-train eval failed; pushing adapter anyway:", e)
        eval_metrics = {"error": str(e), "total": 0, "json_validity": None, "schema_compliance": None,
                        "policy_consistency": None, "decision_consistency": None,
                        "language_correctness": None, "invented_code_rate": None}
    metrics = {"base": MODEL_ID, "gpu": GPU, "epochs": epochs, "rank": rank,
               "final_loss": (trainer.state.log_history[-1] if trainer.state.log_history else {}),
               "eval": eval_metrics}
    if use_wandb:
        import wandb
        wandb.log({f"gemma_eval/{k}": v for k, v in eval_metrics.items() if isinstance(v, (int, float))})
    json.dump(metrics, open(OUT + "/adapter/metrics_v0.json", "w"), indent=2)
    open(OUT + "/adapter/gemma_eval_report.md", "w").write(_report(metrics))
    out_vol.commit()
    _push_adapter(OUT + "/adapter", epochs, metrics)
    return {"eval": eval_metrics}


def _greedy_decode(model, tok, prompt, max_new=256):
    """Manual KV-cached greedy decode — robust to Gemma 4's multimodal logits shape."""
    import torch
    enc = tok(prompt, return_tensors="pt").to(model.device)
    attn, cur, past, out_ids = enc["attention_mask"], enc["input_ids"], None, []
    with torch.no_grad():
        for _ in range(max_new):
            res = model(input_ids=cur, attention_mask=attn, past_key_values=past, use_cache=True)
            logits = res.logits
            while logits.dim() > 2:
                logits = logits[:, -1, :] if logits.dim() == 3 else logits[:, 0]
            nxt = int(logits[0].argmax())
            if tok.eos_token_id is not None and nxt == tok.eos_token_id:
                break
            out_ids.append(nxt)
            past = res.past_key_values
            cur = torch.tensor([[nxt]], device=model.device)
            attn = torch.cat([attn, torch.ones((1, 1), dtype=attn.dtype, device=attn.device)], dim=-1)
    return tok.decode(out_ids, skip_special_tokens=True)


def _evaluate(model, tok, eval_ds, to_text, n=200):
    """JSON validity, schema compliance, policy/decision consistency, language correctness."""
    import json
    import torch
    model.eval()
    n = min(n, len(eval_ds))
    stats = dict(total=n, json_valid=0, schema_ok=0, reason_match=0, decision_match=0,
                 lang_ok=0, no_invented_codes=0)
    for i in range(n):
        try:
            ex = eval_ds[i]
            prompt = to_text(ex, with_answer=False)
            text = _greedy_decode(model, tok, prompt)
            gold = ex["output"]
            obj = json.loads(text[text.index("{"):text.rindex("}") + 1])
            stats["json_valid"] += 1
            if REQUIRED_KEYS.issubset(obj) and obj.get("decision") in VALID_DECISIONS \
                    and obj.get("next_step") in VALID_NEXT and obj.get("reason_code") in VALID_REASONS:
                stats["schema_ok"] += 1
            if obj.get("reason_code") in VALID_REASONS:
                stats["no_invented_codes"] += 1
            if obj.get("reason_code") == gold.get("reason_code"):
                stats["reason_match"] += 1
            if obj.get("decision") == gold.get("decision"):
                stats["decision_match"] += 1
            if str(obj.get("language")) == str(ex["input"].get("language")):
                stats["lang_ok"] += 1
        except Exception:
            continue
    t = max(1, stats["total"])
    return {**stats,
            "json_validity": round(stats["json_valid"] / t, 4),
            "schema_compliance": round(stats["schema_ok"] / t, 4),
            "policy_consistency": round(stats["reason_match"] / t, 4),
            "decision_consistency": round(stats["decision_match"] / t, 4),
            "language_correctness": round(stats["lang_ok"] / t, 4),
            "invented_code_rate": round(1 - stats["no_invented_codes"] / t, 4)}


def _report(m):
    e = m["eval"]
    return f"""# Kámárí Gemma Explanation — Eval Report (v0)

Base **{m['base']}** · GPU {m['gpu']} · {m['epochs']} epochs · LoRA r={m['rank']} · n={e['total']}

| metric | value |
|---|---|
| JSON validity | {e['json_validity']} |
| Schema compliance | {e['schema_compliance']} |
| Policy consistency (reason_code) | {e['policy_consistency']} |
| Decision consistency | {e['decision_consistency']} |
| Language correctness | {e['language_correctness']} |
| Invented-code rate (lower better) | {e['invented_code_rate']} |

Gemma explains decisions only; it never estimates age and chooses reason codes from the
fixed list. Non-English strings still need native-speaker review before release.
"""


def _push_adapter(adapter_dir, epochs, metrics):
    from huggingface_hub import HfApi
    token, ns = os.environ["HF_TOKEN"], os.environ.get("HF_NAMESPACE", "kamari")
    repo = f"{ns}/gemma-explain-lora-v0"
    api = HfApi(token=token)
    api.create_repo(repo, repo_type="model", private=True, exist_ok=True)
    e = metrics["eval"]
    card = f"""---
license: gemma
tags: [kamari, gemma, lora, age-gating, explanation, multilingual]
base_model: {MODEL_ID}
---

# Kámárí Gemma Explanation LoRA v0

LoRA adapter turning CNN + policy signals into safe, multilingual, strict-JSON age-gating
explanations (en, sw, yo, ha, am, fr, ar). Base: `{MODEL_ID}`. {epochs} epochs.

## Eval
- JSON validity **{e['json_validity']}** · schema compliance **{e['schema_compliance']}**
- policy consistency **{e['policy_consistency']}** · decision consistency **{e['decision_consistency']}**
- language correctness **{e['language_correctness']}** · invented-code rate **{e['invented_code_rate']}**

Full report in `gemma_eval_report.md`; metrics in `metrics_v0.json`. Gemma explains — it never
estimates age and never invents decision codes.
"""
    api.upload_folder(folder_path=adapter_dir, repo_id=repo, repo_type="model")
    api.upload_file(path_or_fileobj=card.encode(), path_in_repo="README.md", repo_id=repo, repo_type="model")
    print("pushed ->", repo)


@app.local_entrypoint()
def main(epochs: int = 3):
    print(train.remote(epochs=epochs))
