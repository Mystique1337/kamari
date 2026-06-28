"""Kámárí Gemma explanation layer — QLoRA fine-tune on Modal (GPU).

Fine-tunes Gemma on the strict-JSON SFT dataset (built by
`training/gemma/build_sft_dataset.py`) and pushes the LoRA adapter + card to
Hugging Face `<HF_NAMESPACE>/gemma-explain-lora-v0`.

Gemma EXPLAINS decisions — it never estimates age and never invents decision codes.

Prereqs:
    python training/gemma/build_sft_dataset.py --n 4000   # creates sft_train.jsonl/sft_eval.jsonl
    modal volume put kamari-data training/gemma/sft_train.jsonl sft_train.jsonl
    modal volume put kamari-data training/gemma/sft_eval.jsonl  sft_eval.jsonl
    modal secret create kamari-hf HF_TOKEN=... HF_NAMESPACE=...   # HF_TOKEN must accept Gemma licence

Run:
    modal run services/modal_gemma/train_gemma.py --epochs 3
"""
import os

import modal

GPU = os.environ.get("KAMARI_GPU", "A100-80GB")  # "H100" for the 12B variant
# Set to the Gemma you have access to (e.g. a Gemma 4 id once available).
MODEL_ID = os.environ.get("GEMMA_MODEL_ID", "google/gemma-2-2b-it")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "torch", "transformers>=4.44", "peft>=0.12", "trl>=0.9", "datasets>=2.20",
        "bitsandbytes>=0.43", "accelerate>=0.33", "huggingface_hub",
    )
)
app = modal.App("kamari-gemma-train", image=image)
data_vol = modal.Volume.from_name("kamari-data", create_if_missing=True)
out_vol = modal.Volume.from_name("kamari-gemma", create_if_missing=True)
hf_secret = modal.Secret.from_name("kamari-hf")


def _format(example) -> str:
    import json
    inp = json.dumps(example["input"], ensure_ascii=False)
    out = json.dumps(example["output"], ensure_ascii=False)
    return (f"<start_of_turn>user\n{example['instruction']}\nInput: {inp}<end_of_turn>\n"
            f"<start_of_turn>model\n{out}<end_of_turn>")


@app.function(gpu=GPU, timeout=60 * 60 * 6,
              volumes={"/data": data_vol, "/out": out_vol}, secrets=[hf_secret])
def train(epochs: int = 3, lr: float = 2e-4, rank: int = 16):
    import torch
    from datasets import load_dataset
    from peft import LoraConfig
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    from trl import SFTConfig, SFTTrainer

    token = os.environ["HF_TOKEN"]
    tok = AutoTokenizer.from_pretrained(MODEL_ID, token=token)
    bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                             bnb_4bit_compute_dtype=torch.bfloat16)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID, quantization_config=bnb, device_map="auto",
        torch_dtype=torch.bfloat16, token=token)

    ds = load_dataset("json", data_files={"train": "/data/sft_train.jsonl",
                                          "eval": "/data/sft_eval.jsonl"})
    lora = LoraConfig(r=rank, lora_alpha=rank * 2, lora_dropout=0.05, bias="none",
                      task_type="CAUSAL_LM",
                      target_modules=["q_proj", "k_proj", "v_proj", "o_proj"])
    cfg = SFTConfig(output_dir="/out/adapter", num_train_epochs=epochs,
                    per_device_train_batch_size=8, gradient_accumulation_steps=2,
                    learning_rate=lr, bf16=True, logging_steps=20,
                    save_strategy="epoch", report_to=[])
    trainer = SFTTrainer(model=model, args=cfg, train_dataset=ds["train"],
                         eval_dataset=ds["eval"], peft_config=lora,
                         formatting_func=lambda b: [_format(x) for x in _batch(b)])
    trainer.train()
    trainer.save_model("/out/adapter")
    tok.save_pretrained("/out/adapter")
    out_vol.commit()
    _push_adapter("/out/adapter", epochs)
    return {"epochs": epochs, "base": MODEL_ID}


def _batch(b):
    # SFTTrainer passes a batched dict; re-zip into per-example dicts.
    keys = list(b.keys())
    return [{k: b[k][i] for k in keys} for i in range(len(b[keys[0]]))]


def _push_adapter(adapter_dir, epochs):
    from huggingface_hub import HfApi
    token, ns = os.environ["HF_TOKEN"], os.environ.get("HF_NAMESPACE", "kamari")
    repo = f"{ns}/gemma-explain-lora-v0"
    api = HfApi(token=token)
    api.create_repo(repo, repo_type="model", private=True, exist_ok=True)
    card = f"""---
license: gemma
tags: [kamari, gemma, lora, age-gating, explanation, multilingual]
base_model: {MODEL_ID}
---

# Kámárí Gemma Explanation LoRA v0

LoRA adapter that turns CNN + policy signals into safe, multilingual, strict-JSON
age-gating explanations (en, sw, yo, ha, am, fr, ar). Base: `{MODEL_ID}`. {epochs} epochs.

Output conforms to `training/gemma/output_schema.json`. Gemma explains — it never
estimates age and never invents decision codes. Non-English strings need native review.
"""
    api.upload_folder(folder_path=adapter_dir, repo_id=repo, repo_type="model")
    api.upload_file(path_or_fileobj=card.encode(), path_in_repo="README.md",
                    repo_id=repo, repo_type="model")
    print("pushed ->", repo)


@app.local_entrypoint()
def main(epochs: int = 3):
    print(train.remote(epochs=epochs))
