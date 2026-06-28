# Kámárí Data Notebook (run on Google Colab)

One standard notebook — **`kamari_data_pipeline.ipynb`** — takes the free/open datasets
from raw files to **published Hugging Face datasets**, so the Modal training scripts pull
the data straight from HF.

## What it does
**1. Gather** licence-cleared datasets → **2. Preprocess** (face-align, crop 224, quality +
ITA/skin band, build manifest) → **3. EDA** (distributions, 13–21 boundary, fairness,
quality report) → **4. Publish to Hugging Face**.

## Hugging Face outputs
| Repo | Visibility | Holds | Consumed by |
|---|---|---|---|
| `<ns>/kamari-faces-v0` | **private** | aligned crops + train/benchmark manifests | Modal CNN training |
| `<ns>/dataset-registry-v0` | private | manifests + registry + licences + EDA + card | provenance |
| `<ns>/kamari-safe-open-v0` | private | frozen benchmark manifest | benchmarking |

Raw face crops are pushed to a **private** repo only — never public.

## One-time Colab setup
1. **Push this repo to GitHub** (the notebook `git clone`s it).
2. Colab **🔑 Secrets** (toggle notebook access): `KAMARI_REPO_URL`, `HF_TOKEN` (write),
   `HF_NAMESPACE`, `KAGGLE_USERNAME`, `KAGGLE_KEY`, optional `FAGE_HF_REPO`.
3. Use a **GPU runtime** (Runtime → Change runtime type → GPU) for preprocessing.

The first cell auto-clones the repo, `pip install`s `requirements-data.txt`, and loads the
secrets. It also runs locally (falls back to `.env` — see `.env.example`).

## Hand-off
The final cell prints the HF dataset links. Training reads from `kamari-faces-v0`; nothing
else is needed to kick off CNN training on Modal.

## Adding a dataset
Write `data/adapters/<name>.py` exposing `iter_rows(root)` that yields `make_row(...)`
dicts, then register it in `data/adapters/__init__.py`. The notebook applies
alignment/quality/skin-band uniformly to every adapter.
