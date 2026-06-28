"""Kámárí Gemma explanation layer — QLoRA fine-tune on Modal (GPU).

Pulls the strict-JSON SFT dataset from Hugging Face `<HF_NAMESPACE>/gemma-sft-v0`,
fine-tunes Gemma with QLoRA, tracks training in Weights & Biases, and uploads the
**LoRA adapter + metrics + training log + card** to `<HF_NAMESPACE>/gemma-explain-lora-v0`.

Gemma EXPLAINS decisions — it never estimates age and never invents decision codes.

Prereqs:
    python training/gemma/build_sft_dataset.py --n 4000
    huggingface-cli upload <ns>/gemma-sft-v0 training/gemma/sft_train.jsonl sft_train.jsonl --repo-type dataset
    huggingface-cli upload <ns>/gemma-sft-v0 training/gemma/sft_eval.jsonl  sft_eval.jsonl  --repo-type dataset
    modal secret create kamari-hf HF_TOKEN=... HF_NAMESPACE=... WANDB_API_KEY=... WANDB_PROJECT=kamari

Run:
    modal run services/modal_gemma/train_gemma.py --epochs 3
"""
import os

import modal

GPU = os.environ.get("KAMARI_GPU", "A100-80GB")  # "H100" for the 12B variant
MODEL_ID = os.environ.get("GEMMA_MODEL_ID", "google/gemma-2-2b-it")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "torch", "transformers>=4.44", "peft>=0.12", "trl>=0.9", "datasets>=2.20",
        "bitsandbytes>=0.43", "accelerate>=0.33", "huggingface_hub", "wandb",
    )
)
app = modal.App("kamari-gemma-train", image=image)
out_vol = modal.Volume.from_name("kamari-gemma", create_if_missing=True)
hf_secret = modal.Secret.from_name("kamari-hf")


def _format(example) -> str:
    import json
    inp = json.dumps(example["input"], ensure_ascii=False)
    out = json.dumps(example["output"], ensure_ascii=False)
    return (f"<start_of_turn>user\n{example['instruction']}\nInput: {inp}<end_of_turn>\n"
            f"<start_of_turn>model\n{out}<end_of_turn>")


@app.function(gpu=GPU, timeout=60 * 60 * 6, volumes={"/out": out_vol}, secrets=[hf_secret])
def train(epochs: int = 3, lr: float = 2e-4, rank: int = 16):
    import json
    import torch
    from datasets import load_dataset
    from huggingface_hub import snapshot_download
    from peft import LoraConfig
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    from trl import SFTConfig, SFTTrainer

    token, ns = os.environ["HF_TOKEN"], os.environ.get("HF_NAMESPACE", "kamari")
    use_wandb = bool(os.environ.get("WANDB_API_KEY"))
    if use_wandb:
        os.environ.setdefault("WANDB_PROJECT", os.environ.get("WANDB_PROJECT", "kamari"))

    # --- Pull SFT data from HF ---
    sft_dir = snapshot_download(f"{ns}/gemma-sft-v0", repo_type="dataset", token=token)
    ds = load_dataset("json", data_files={
        "train": os.path.join(sft_dir, "sft_train.jsonl"),
        "eval": os.path.join(sft_dir, "sft_eval.jsonl"),
    })

    tok = AutoTokenizer.from_pretrained(MODEL_ID, token=token)
    bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                             bnb_4bit_compute_dtype=torch.bfloat16)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID, quantization_config=bnb, device_map="auto",
        torch_dtype=torch.bfloat16, token=token)

    lora = LoraConfig(r=rank, lora_alpha=rank * 2, lora_dropout=0.05, bias="none",
                      task_type="CAUSAL_LM",
                      target_modules=["q_proj", "k_proj", "v_proj", "o_proj"])
    cfg = SFTConfig(output_dir="/out/adapter", num_train_epochs=epochs,
                    per_device_train_batch_size=8, gradient_accumulation_steps=2,
                    learning_rate=lr, bf16=True, logging_steps=20,
                    eval_strategy="epoch", save_strategy="epoch",
                    run_name=f"gemma-lora-{rank}",
                    report_to=["wandb"] if use_wandb else [])
    trainer = SFTTrainer(model=model, args=cfg, train_dataset=ds["train"],
                         eval_dataset=ds["eval"], peft_config=lora,
                         formatting_func=lambda b: [_format(x) for x in _batch(b)])
    trainer.train()
    trainer.save_model("/out/adapter")
    tok.save_pretrained("/out/adapter")

    # Persist full metric history alongside the adapter.
    metrics = {"base": MODEL_ID, "epochs": epochs, "rank": rank,
               "log_history": trainer.state.log_history}
    json.dump(metrics, open("/out/adapter/metrics_v0.json", "w"), indent=2)
    out_vol.commit()

    _push_adapter("/out/adapter", epochs, metrics)
    return {"epochs": epochs, "base": MODEL_ID,
            "final": trainer.state.log_history[-1] if trainer.state.log_history else {}}


def _batch(b):
    keys = list(b.keys())
    return [{k: b[k][i] for k in keys} for i in range(len(b[keys[0]]))]


def _push_adapter(adapter_dir, epochs, metrics):
    from huggingface_hub import HfApi
    token, ns = os.environ["HF_TOKEN"], os.environ.get("HF_NAMESPACE", "kamari")
    repo = f"{ns}/gemma-explain-lora-v0"
    api = HfApi(token=token)
    api.create_repo(repo, repo_type="model", private=True, exist_ok=True)
    final = metrics["log_history"][-1] if metrics.get("log_history") else {}
    card = f"""---
license: gemma
tags: [kamari, gemma, lora, age-gating, explanation, multilingual]
base_model: {MODEL_ID}
---

# Kámárí Gemma Explanation LoRA v0

LoRA adapter that turns CNN + policy signals into safe, multilingual, strict-JSON
age-gating explanations (en, sw, yo, ha, am, fr, ar). Base: `{MODEL_ID}`. {epochs} epochs.

- Final eval loss: **{final.get('eval_loss', 'n/a')}**
- Output conforms to `training/gemma/output_schema.json`. Full metrics in `metrics_v0.json`.

Gemma explains — it never estimates age and never invents decision codes. Non-English
strings need native-speaker review before release.
"""
    api.upload_folder(folder_path=adapter_dir, repo_id=repo, repo_type="model")
    api.upload_file(path_or_fileobj=card.encode(), path_in_repo="README.md",
                    repo_id=repo, repo_type="model")
    print("pushed ->", repo)


@app.local_entrypoint()
def main(epochs: int = 3):
    print(train.remote(epochs=epochs))
