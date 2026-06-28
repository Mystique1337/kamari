"""Hugging Face helpers: push manifests, datasets, models, and standard cards.

All Kámárí artifacts live under a single namespace (HF_NAMESPACE), e.g.:
    <ns>/dataset-registry-v0   <ns>/cnn-age-v0   <ns>/gemma-explain-lora-v0
    <ns>/kamari-safe-open-v0

Usage:
    from data.hf_utils import HF
    hf = HF()                              # reads HF_TOKEN / HF_NAMESPACE from env
    repo = hf.push_manifest(df, "dataset-registry-v0", split="train")
    hf.upload_file("DATASET_CARD.md", "dataset-registry-v0", "README.md", repo_type="dataset")
"""
from __future__ import annotations

import io
import os
from typing import Optional

import pandas as pd


class HF:
    def __init__(self, token: Optional[str] = None, namespace: Optional[str] = None):
        self.token = token or os.environ.get("HF_TOKEN")
        self.namespace = namespace or os.environ.get("HF_NAMESPACE", "kamari")
        if not self.token:
            raise RuntimeError("HF_TOKEN not set — add it to .env or the environment.")
        from huggingface_hub import HfApi
        self.api = HfApi(token=self.token)

    def repo_id(self, name: str) -> str:
        return name if "/" in name else f"{self.namespace}/{name}"

    def ensure_repo(self, name: str, repo_type: str = "dataset", private: bool = True):
        rid = self.repo_id(name)
        self.api.create_repo(rid, repo_type=repo_type, private=private,
                             exist_ok=True, token=self.token)
        return rid

    def push_manifest(self, df: pd.DataFrame, name: str, split: str = "train",
                      private: bool = True) -> str:
        """Upload a manifest DataFrame as parquet to a dataset repo."""
        rid = self.ensure_repo(name, "dataset", private)
        buf = io.BytesIO()
        df.to_parquet(buf, index=False)
        buf.seek(0)
        self.api.upload_file(
            path_or_fileobj=buf,
            path_in_repo=f"manifests/manifest_{split}_v0.parquet",
            repo_id=rid, repo_type="dataset", token=self.token,
            commit_message=f"Add {split} manifest ({len(df)} rows)",
        )
        return rid

    def upload_file(self, local_path: str, name: str, path_in_repo: str,
                    repo_type: str = "dataset", private: bool = True) -> str:
        rid = self.ensure_repo(name, repo_type, private)
        self.api.upload_file(path_or_fileobj=local_path, path_in_repo=path_in_repo,
                             repo_id=rid, repo_type=repo_type, token=self.token)
        return rid

    def upload_folder(self, folder: str, name: str, repo_type: str = "model",
                      path_in_repo: str = "", private: bool = True) -> str:
        rid = self.ensure_repo(name, repo_type, private)
        self.api.upload_folder(folder_path=folder, path_in_repo=path_in_repo,
                               repo_id=rid, repo_type=repo_type, token=self.token)
        return rid


def dataset_card(namespace: str, n_rows: int, datasets: list[str]) -> str:
    """Render a minimal, honest dataset card (no raw images, provenance only)."""
    used = ", ".join(datasets)
    return f"""---
license: other
tags: [kamari, age-estimation, african, fairness, face]
---

# Kámárí Dataset Registry v0

Provenance + manifest for the Kámárí age-gating system. **No raw face images are
redistributed here** unless a source licence explicitly allows it — this repo holds
manifests (paths, hashes, labels, licence/consent), dataset cards, and reports.

- Rows: **{n_rows}**
- Source datasets: {used}
- Namespace: `{namespace}`

## Manifest columns
See `manifest_*_v0.parquet`. Schema is fixed (see `data/manifest_schema.py`).

## Ethics & licensing
Per-source licences in `licenses.md`. Minor faces are never published. Use is
research-only unless a source permits otherwise.
"""
