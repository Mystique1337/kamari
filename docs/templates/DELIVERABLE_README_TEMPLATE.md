<!--
Kámárí STANDARD DELIVERABLE README / MODEL CARD / DATASET CARD TEMPLATE
Use this exact section order for every deliverable (dataset, CNN, Gemma, benchmark,
API, app). Fill every section; write "N/A" rather than deleting a heading. The HF
repo README for each artifact is generated from this template.
-->
---
# (HF card front-matter - keep for model/dataset repos)
license: other
tags: [kamari, age-estimation, african, fairness]
---

# Kámárí <Deliverable Name> <version>

> One-sentence description of what this is and who it's for.

## Summary
What it does, in 3-5 sentences. State the African-focused age-gating purpose.

## Intended use & out-of-scope
- Intended: …
- **Out of scope / do not use for**: legal age determination, 1:N face search, surveillance.

## Artifacts
| File | Description |
|---|---|
| … | … |

## How to use / load
```bash
# minimal runnable example (HF download, modal deploy, or app command)
```

## Data
Datasets used (link to registry + dataset card). State exact-age vs bracket usage and
the African-domain signal. Link manifest + benchmark run IDs.

## Training / build details
Backbone or base model, hyperparameters, hardware (Modal GPU), seed, commit hash.

## Evaluation
Headline metrics first. For age models: **Minor-Pass-Through Rate @18/@21**, then MAE
by age/skin/dataset/gender, latency p50/p95. For Gemma: JSON validity, schema
compliance, policy consistency. Include subgroup tables and the benchmark version.

## Limitations & ethics
Known biases, dark-skin/boundary performance, dataset gaps. Privacy posture
(no-store default, retention). "This is an estimate, not a legal determination."

## License & consent
Per-source licences (link `licenses.md`). Redistribution status of any images.

## Versioning & provenance
- Version: …  | Git commit: …  | HF repo: …  | Benchmark run ID: …
- Changelog:
  - `v0.1.0` - initial release.

## Citation / contact
…
