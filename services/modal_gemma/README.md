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
```bash
python training/gemma/build_sft_dataset.py --n 4000
modal volume put kamari-data training/gemma/sft_train.jsonl sft_train.jsonl
modal volume put kamari-data training/gemma/sft_eval.jsonl  sft_eval.jsonl
# HF_TOKEN must have accepted the Gemma licence; set GEMMA_MODEL_ID for your variant
modal run services/modal_gemma/train_gemma.py --epochs 3
```

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
