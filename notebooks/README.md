# Kámárí Data Notebooks (run on Google Colab)

Four notebooks take the free/open datasets from raw files to published Hugging Face
datasets. **Run them in order, in one Colab session** (Colab storage is ephemeral;
notebook 04 is the single step that persists everything to Hugging Face).

| # | Notebook | Does | Output |
|---|---|---|---|
| 01 | `01_data_gathering.ipynb` | Download licence-cleared datasets | `data/raw/*` |
| 02 | `02_cleaning_preprocessing.ipynb` | Face-align, crop 224, quality + ITA/skin band, build manifest | `data/manifests/*.parquet`, `data/processed/crops_224/*` |
| 03 | `03_eda.ipynb` | Distributions, 13–21 boundary, fairness, quality report | `data/cards/eda/*.png`, `data_quality_report.md` |
| 04 | `04_push_to_huggingface.ipynb` | **Single upload step** → HF | `dataset-registry-v0`, `kamari-safe-open-v0` |

## One-time Colab setup

1. **Push this repo to GitHub** (the notebooks `git clone` it on Colab).
2. In Colab, open the **🔑 Secrets** panel and add (toggle "Notebook access" on):
   - `KAMARI_REPO_URL` — your repo URL, e.g. `https://github.com/<you>/kamari.git`
   - `HF_TOKEN` — Hugging Face token with **write** access
   - `HF_NAMESPACE` — your HF user/org, e.g. `kamari`
   - `KAGGLE_USERNAME`, `KAGGLE_KEY` — for the UTKFace download
   - `FAGE_HF_REPO` *(optional)* — HF repo id for FAGE_v2
3. For notebook **02**, set a **GPU runtime** (Runtime → Change runtime type → GPU).

The first cell of every notebook auto-clones the repo, `pip install`s
`requirements-data.txt`, and loads the secrets. The same notebooks also run locally
(they fall back to a `.env` file — see `.env.example`).

## Hand-off
When notebook 04 finishes it prints two `https://huggingface.co/datasets/...` links.
Share those (plus any dataset notes) and the CNN + Gemma Modal trainings can start.

## Adding a dataset
Write `data/adapters/<name>.py` exposing `iter_rows(root)` that yields
`make_row(...)` dicts, then register it in `data/adapters/__init__.py`. Notebook 02
applies alignment/quality/skin-band uniformly to every adapter.
