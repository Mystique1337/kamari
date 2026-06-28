# Kámárí Gemma Explanation Layer (Modal)

Turns CNN + policy signals into safe, multilingual, **strict-JSON** explanations.
Gemma explains decisions — it never estimates age and never invents decision codes.

## Artifacts
| File | Role |
|---|---|
| `train_gemma.py` | Modal QLoRA fine-tune → push adapter `gemma-explain-lora-v0` |
| `serve_gemma.py` | Modal serving: base + adapter → validated JSON endpoint |
| `../../training/gemma/build_sft_dataset.py` | Builds SFT data from the policy engine |
| `../../training/gemma/output_schema.json` | The strict output schema |

## Train
Base **`google/gemma-3-4b-it`** (4B), QLoRA (r=32, all linear modules), cosine+warmup,
packing, NEFTune, grad-checkpointing, best-by-eval-loss, **resumable** (epoch checkpoints on
the `kamari-gemma` Volume). Reads SFT from HF `gemma-sft-v0`, tracks in **W&B**, and uploads
the **adapter + `metrics_v0.json` + `gemma_eval_report.md` + card** back to HF.
```bash
python training/gemma/build_sft_dataset.py --n 6000
huggingface-cli upload <ns>/gemma-sft-v0 training/gemma/sft_train.jsonl sft_train.jsonl --repo-type dataset
huggingface-cli upload <ns>/gemma-sft-v0 training/gemma/sft_eval.jsonl  sft_eval.jsonl  --repo-type dataset
# HF_TOKEN must accept the Gemma licence. GPU defaults to H200 (KAMARI_GPU to change).
modal secret create kamari-hf HF_TOKEN=... HF_NAMESPACE=... WANDB_API_KEY=... WANDB_PROJECT=kamari
modal run services/modal_gemma/train_gemma.py --epochs 3
```
**Eval** (logged + `gemma_eval_report.md`): JSON validity, schema compliance, policy &
decision consistency vs the rule engine, language correctness, invented-code rate.

## Serve
```bash
modal deploy services/modal_gemma/serve_gemma.py
# -> set the printed URL as MODAL_GEMMA_ENDPOINT in apps/api
```

## Contract
Input: `{ "cnn_result": {...}, "policy_context": {"decision","reason_code",...}, "language": "en" }`
Output: schema-valid `{ decision, reason_code, user_message, admin_summary, next_step, language, safety_note }`.
Invalid generations fall back to a deterministic safe template, so the gateway always
receives valid JSON. Non-English strings require native-speaker review before release.
