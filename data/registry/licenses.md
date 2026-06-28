# Kámárí dataset licences & consent notes

This file records, per dataset, the licence/consent basis we rely on and any
redistribution limits. It is the source of truth referenced by every manifest row's
`license` and `consent_basis` fields, by `license_report.md`, and by dataset cards.

> Rule: **we never redistribute raw images unless the licence explicitly allows it.**
> Manifests store paths/hashes/labels, not pixels, by default. Crops are published to
> Hugging Face only for datasets whose licence permits redistribution.

| Dataset | Licence | Redistribute raw? | Commercial use? | Notes |
|---|---|---|---|---|
| UTKFace | Non-commercial research | No | No | Research/pretraining only |
| APPA-REAL | Research | Check | No | Real+apparent age |
| AgeDB | Research (request) | No | No | Request access first |
| FG-NET | Research | No | No | Small aging set |
| All-Age-Faces | Research | No | No | Asian-heavy, pretrain only |
| IMDB-WIKI | Non-commercial research | No | No | Noisy; clean before use |
| AxonData-10-30 | CC-BY-NC (verify) | Verify | No | Verify exact terms on HF |
| FAGE_v2 | Research (verify) | Verify | No | African public figures |
| FairFace | CC BY 4.0 | Yes (with attribution) | Yes | Brackets only |
| LFW | Research | Yes | Check | Public benchmark |
| RFW | Research (request) | No | No | African fairness subset |
| BFW | Research (request) | No | No | Subgroup benchmark |
| CelebA-Spoof | Research | No | No | Anti-spoof |
| CASIA-Face-Africa | Research/edu, no redistribution | No | No | Agreement-only |
| BVC-UNN | Free after request | No | No | Agreement-only |
| NEFI | Verify | No | No | Agreement-only |
| MS-Celeb-1M | Withdrawn | No | No | EXCLUDED |

Action items before v0 freeze:
- [ ] Confirm APPA-REAL and FAGE_v2 redistribution terms.
- [ ] Record AxonData exact CC-BY-NC variant and consent statement.
- [ ] Keep request/approval emails for AgeDB, RFW, BFW, CelebA-Spoof on file.
