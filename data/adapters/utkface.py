"""UTKFace adapter.

UTKFace filenames encode labels: [age]_[gender]_[race]_[datetime].jpg
  gender: 0 male, 1 female
  race:   0 White, 1 Black, 2 Asian, 3 Indian, 4 Others
Exact age -> age regression + under-18. Non-commercial research only.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Iterator

from ..manifest_schema import make_row, sha256_bytes

_GENDER = {"0": "m", "1": "f"}
_RACE = {"0": "white", "1": "black", "2": "asian", "3": "indian", "4": "other"}


def iter_rows(root: str) -> Iterator[dict]:
    root_p = Path(root)
    for fp in root_p.rglob("*.jpg"):
        parts = fp.stem.split("_")
        if len(parts) < 3:
            continue
        try:
            age = float(parts[0])
        except ValueError:
            continue
        gender = _GENDER.get(parts[1], "unknown")
        race = _RACE.get(parts[2], "unknown")
        try:
            source_hash = sha256_bytes(fp.read_bytes())
        except OSError:
            source_hash = None
        yield make_row(
            image_id=f"utkface/{fp.stem}",
            path=str(fp.relative_to(root_p.parent)) if root_p.parent in fp.parents else str(fp),
            dataset="UTKFace",
            split="train",
            age=age,
            age_exact=True,
            gender=gender,
            race_hint=race,
            license="non-commercial-research",
            consent_basis="public web faces, research use",
            source_url="https://susanqq.github.io/UTKFace/",
            source_hash=source_hash,
            usable_for_age=True,
            train_ok=True,
            eval_ok=False,
        )
