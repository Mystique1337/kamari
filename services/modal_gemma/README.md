# Kámárí Gemma Explanation Layer (Modal)

Turns CNN + policy signals into safe, multilingual, **strict-JSON** explanations.
Gemma explains decisions - it never estimates age and never invents decision codes.

## Model - `Shinzmann/gemma-explain-lora-v0`
- Adapter: https://huggingface.co/Shinzmann/gemma-explain-lora-v0
- Base: **`google/gemma-4-E4B-it`** (Gemma 4, effective-4B) · QLoRA (4-bit, `target_modules=all-linear`)
- SFT data: https://huggingface.co/datasets/Shinzmann/gemma-sft-v0 (balanced 8k: 7,200 train / 800 eval)
- Eval (in `gemma_eval_report.md`): JSON validity, schema compliance, policy & decision
  consistency vs the rule engine, language correctness, invented-code rate.

## Artifacts (code)
| File | Role |
|---|---|
| `train_gemma.py` | Modal QLoRA fine-tune → eval → push adapter `gemma-explain-lora-v0` |
| `serve_gemma.py` | Modal serving (GPU): base + adapter → validated JSON endpoint |
| `../../training/gemma/build_sft_dataset.py` | Builds the **balanced** SFT set from the policy engine |
| `../../training/gemma/output_schema.json` | The strict output schema |

## Train
QLoRA (r=32, all-linear), cosine+warmup, NEFTune, grad-checkpointing, **no packing**
(clean per-sample, low memory), best-by-eval-loss, resumable. Reads SFT from HF, tracks in **W&B**.
```bash
python training/gemma/build_sft_dataset.py --n 8000
huggingface-cli upload Shinzmann/gemma-sft-v0 training/gemma/sft_train.jsonl sft_train.jsonl --repo-type dataset
huggingface-cli upload Shinzmann/gemma-sft-v0 training/gemma/sft_eval.jsonl  sft_eval.jsonl  --repo-type dataset
# HF_TOKEN must have accepted the Gemma 4 licence. GPU defaults to H200.
modal run --detach services/modal_gemma/train_gemma.py --epochs 3
```

## Serve
**Fast GPU (recommended for the live API)** - per-request latency matters:
```bash
modal deploy services/modal_gemma/serve_gemma.py   # -> set URL as MODAL_GEMMA_ENDPOINT
```
**CPU option (cost/offline/edge):** a 4B model on CPU is ~seconds/response. For acceptable
CPU speed, merge the adapter into the base and convert to **q4 GGUF** (llama.cpp); Google ships
`gemma-4-E4B-it-qat-q4_0-gguf` as the QAT base. (Not wired yet - ask and I'll add the
merge→GGUF→serve path.)

## Contract
Input: `{ "cnn_result": {...}, "policy_context": {"decision","reason_code",...}, "language": "en" }`
Output: schema-valid `{ decision, reason_code, user_message, admin_summary, next_step, language, safety_note }`.
Invalid generations fall back to a deterministic safe template, so the gateway always
receives valid JSON. Non-English strings require native-speaker review before release.
