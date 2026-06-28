---
license: other
task_categories:
  - image-classification
language:
  - en
tags:
  - age-estimation
  - fairness
  - benchmark
  - africa
pretty_name: Kámárí-Safe Open v0
---

# Kámárí-Safe Open v0 (benchmark)

A frozen, leakage-free benchmark for African-tailored age verification. It holds **manifests and
split tables, not raw images** (paths, hashes, labels, skin band, quality). Use it to measure age
accuracy and, more importantly, child-safety.

## Headline metric
**Minor-Pass-Through Rate (MPTR)** is the headline: the fraction of true minors a model passes as
adults, reported overall, at 21, and for dark + brown skin. Report MPTR alongside MAE; a low MAE with
a high MPTR is not safe.

## Splits
`general`, `african_signal`, `black_subset`, `dark_skin`, `boundary_13_21`, `low_quality_camera`.
These let you read fairness and the critical 13 to 21 boundary directly.

## Build
Open, license-checked sources, auto label-quality gate, MTCNN crops, ITA skin banding, and a holdout
keyed by subject id so train and benchmark are disjoint by both image and subject. Full method:
https://github.com/Mystique1337/kamari/blob/main/docs/methodology.md

## Reference result (Kámárí CNN v0, n=8,322)
MAE 6.03; MPTR@18 0.317 (dark + brown 0.383); MPTR@21 0.27; adult-block 0.01.

## License and ethics
Per-source licenses apply (see `registry/licenses.md`); this repo redistributes manifests, not
pixels. Minor faces are never published. For research and safety evaluation. Not for 1:N face search
or legal age determination.
