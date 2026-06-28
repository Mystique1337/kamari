# Kámárí Data Notebook (run on Google Colab)

Use **`kamari_data_pipeline_v2.ipynb`** on Google Colab. It keeps the original single-notebook
flow from **`kamari_data_pipeline.ipynb`**, but expands the gather step to cover every dataset
named in the recommendations and writes African-focused benchmark/report outputs.

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

For full recommendation coverage, add approved dataset URLs or HF repos as Colab secrets when
the dataset is not directly open-downloadable: `APPA_REAL_URL`, `ADIENCE_URL`, `AGEDB_URL` or
`AGEDB_HF_REPO`, `FGNET_URL`, `AAF_URL` or `AAF_HF_REPO`, `FAGE_HF_REPO`,
`AXONDATA_URL` or `AXONDATA_HF_REPO`, `RFW_URL` or `RFW_HF_REPO`, `BFW_URL` or
`BFW_HF_REPO`, `CELEBA_SPOOF_URL` or `CELEBA_SPOOF_HF_REPO`, `CEFA_URL`,
`OULU_NPU_URL`, `CASIA_FACE_AFRICA_URL`, `BVC_UNN_URL`, and `NEFI_URL`.

The v2 notebook records request/agreement-only datasets as access gaps until approved sources
are supplied; it does not silently drop them.

Tracked source/download URLs live in `data/registry/dataset_sources.yaml`. Direct-download
defaults are already present in `.env.example`; request/agreement-only entries stay blank
until access is approved.

Kaggle datasets can be downloaded either through the Kaggle API credentials or through
`kagglehub` slugs in `.env.example`; v2 uses `kagglehub` for FAGE, Adience, AgeDB,
AxonData, LFW, and AgeDB-30.

## Hand-off
The final cell prints the HF dataset links. Training reads from `kamari-faces-v0`; nothing
else is needed to kick off CNN training on Modal.

The v2 notebook also writes `AFRICAN_TAILORING_REPORT.md`, `BENCHMARK_CARD.md`, and fixed
benchmark split manifests for African signal, Black subset, dark-skin, 13–21 boundary, and
low-quality-camera slices.
It also writes `pipeline_dataset_audit.csv/md`, which shows whether each planned dataset
downloaded, produced candidate manifest rows, and is ready for preprocessing/HF handoff.

## Adding a dataset
Write `data/adapters/<name>.py` exposing `iter_rows(root)` that yields `make_row(...)`
dicts, then register it in `data/adapters/__init__.py`. The notebook applies
alignment/quality/skin-band uniformly to every adapter.
