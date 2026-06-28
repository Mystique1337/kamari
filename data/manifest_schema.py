"""Canonical Kámárí manifest schema (master plan §6.3).

Every image — from every dataset — becomes exactly one manifest row with these
columns. We never train from loose folders; the manifest is the single source of truth
for what is trainable, evaluable, and redistributable.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
from typing import Optional

import pandas as pd

# Order matters: this is the on-disk column order for the parquet manifests.
MANIFEST_COLUMNS: list[str] = [
    "image_id",
    "path",
    "dataset",
    "split",                 # train | val | test | benchmark
    "subject_id",
    "age",                   # float; may be apparent age
    "age_exact",             # bool: is `age` an exact chronological label?
    "age_band",              # e.g. "13-15", "16-17", "18-20"
    "is_minor",              # bool: age < 18
    "gender",                # m | f | unknown
    "race_hint",             # dataset-provided, coarse; advisory only
    "country",               # ISO-2 where known, else ""
    "skin_ita",              # Individual Typology Angle (float degrees)
    "skin_band",             # very_light | light | intermediate | tan | brown | dark
    "face_quality",          # 0..1
    "bbox",                  # "x,y,w,h" in original image pixels
    "license",               # short licence id; see registry/licenses.md
    "consent_basis",
    "source_url",
    "source_hash",           # sha256 of the source image bytes
    "usable_for_age",
    "usable_for_verification",
    "usable_for_liveness",
    "train_ok",
    "eval_ok",
    "synthetic",
    "created_at",
]

# ITA -> skin band thresholds (degrees). Chardon/Del Bino scale, descending ITA.
_ITA_BANDS = [
    (55.0, "very_light"),
    (41.0, "light"),
    (28.0, "intermediate"),
    (10.0, "tan"),
    (-30.0, "brown"),
    (-90.0, "dark"),
]


def age_to_band(age: Optional[float]) -> str:
    if age is None or pd.isna(age):
        return "unknown"
    a = int(age)
    bounds = [(0, 12), (13, 15), (16, 17), (18, 20), (21, 25), (26, 35),
              (36, 50), (51, 70), (71, 120)]
    for lo, hi in bounds:
        if lo <= a <= hi:
            return f"{lo}-{hi}"
    return "unknown"


def ita_to_band(ita: Optional[float]) -> str:
    if ita is None or pd.isna(ita):
        return "unknown"
    for thresh, name in _ITA_BANDS:
        if ita >= thresh:
            return name
    return "dark"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def now_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat()


def empty_manifest() -> pd.DataFrame:
    """An empty DataFrame with the exact manifest columns."""
    return pd.DataFrame({c: pd.Series(dtype="object") for c in MANIFEST_COLUMNS})


def make_row(**kwargs) -> dict:
    """Build a single manifest row, filling derived + default fields.

    Pass at least: image_id, path, dataset, age (if known), license, consent_basis.
    Derived automatically: age_band, is_minor, skin_band, created_at.
    """
    row = {c: kwargs.get(c) for c in MANIFEST_COLUMNS}
    age = kwargs.get("age")
    if row.get("age_band") is None:
        row["age_band"] = age_to_band(age)
    if row.get("is_minor") is None and age is not None and not pd.isna(age):
        row["is_minor"] = bool(age < 18)
    if row.get("skin_band") is None:
        row["skin_band"] = ita_to_band(kwargs.get("skin_ita"))
    row["created_at"] = kwargs.get("created_at") or now_iso()
    # Sensible boolean defaults
    for b, default in [("age_exact", False), ("synthetic", False),
                       ("usable_for_age", False), ("usable_for_verification", False),
                       ("usable_for_liveness", False), ("train_ok", False),
                       ("eval_ok", False)]:
        if row.get(b) is None:
            row[b] = default
    return row


def validate(df: pd.DataFrame) -> list[str]:
    """Return a list of human-readable problems; empty list means valid."""
    problems: list[str] = []
    missing = [c for c in MANIFEST_COLUMNS if c not in df.columns]
    if missing:
        problems.append(f"missing columns: {missing}")
    if "image_id" in df and df["image_id"].duplicated().any():
        n = int(df["image_id"].duplicated().sum())
        problems.append(f"{n} duplicate image_id values")
    if "age" in df:
        bad = df[(df["age"].notna()) & ((df["age"] < 0) | (df["age"] > 120))]
        if len(bad):
            problems.append(f"{len(bad)} rows with age outside [0,120]")
    if "is_minor" in df and "age" in df:
        mism = df[(df["age"].notna()) & (df["is_minor"] != (df["age"] < 18))]
        if len(mism):
            problems.append(f"{len(mism)} rows where is_minor disagrees with age")
    return problems
