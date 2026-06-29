---
license: other
task_categories:
  - image-classification
language:
  - en
tags:
  - age-estimation
  - fairness
  - provenance
  - africa
  - dataset-registry
pretty_name: Kámárí Dataset Registry v0
---

# Kámárí Dataset Registry (v0)

Provenance for the Kámárí datasets used to train the age model and build the
[Kámárí-Safe Open benchmark](https://huggingface.co/datasets/Shinzmann/kamari-safe-open-v0). It holds
**manifests** (paths, hashes, labels, skin-tone band, quality), the dataset **source and licence
registry**, **EDA reports**, and the **data-quality report**. No raw images are redistributed.

Built from open, license-checked face datasets with an auto label-quality gate, MTCNN face crops, and
ITA skin-tone banding. v0 composition: 825,129 candidate rows, 480,828 kept, 24,753 exact-age
training rows, 10,182 African-signal rows.

## Links
- Code (Apache-2.0): https://github.com/Mystique1337/kamari
- Methodology: https://github.com/Mystique1337/kamari/blob/main/docs/methodology.md
- Live demo: https://kamari.shinzii.tech

For research and safety evaluation. Not for 1:N face search or legal age determination.
