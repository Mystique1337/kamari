"""FairFace adapter.

FairFace ships CSVs (fairface_label_train.csv / _val.csv) with columns:
  file, age (bracket e.g. "10-19"), gender, race, service_test
CC BY 4.0. Bracketed ages -> fairness/age-band EVAL only (never exact 18-truth).
The Black subset is the key fairness benchmark slice.
"""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterator

from ..manifest_schema import make_row

# Bracket midpoints (advisory only; age_exact stays False).
_BRACKET_MID = {
    "0-2": 1, "3-9": 6, "10-19": 15, "20-29": 25, "30-39": 35,
    "40-49": 45, "50-59": 55, "60-69": 65, "more than 70": 75,
}
_RACE_MAP = {
    "Black": "black", "White": "white", "East Asian": "asian",
    "Southeast Asian": "asian", "Indian": "indian", "Latino_Hispanic": "latino",
    "Middle Eastern": "middle_eastern",
}


def iter_rows(root: str) -> Iterator[dict]:
    root_p = Path(root)
    for csv_name, split in [("fairface_label_train.csv", "train"),
                            ("fairface_label_val.csv", "benchmark")]:
        csv_path = root_p / csv_name
        if not csv_path.exists():
            continue
        with open(csv_path, newline="") as fh:
            for r in csv.DictReader(fh):
                bracket = r.get("age", "").strip()
                mid = _BRACKET_MID.get(bracket)
                race = _RACE_MAP.get(r.get("race", "").strip(), "unknown")
                yield make_row(
                    image_id=f"fairface/{r['file']}",
                    path=str(root_p / r["file"]),
                    dataset="FairFace",
                    split=split,
                    age=mid,
                    age_exact=False,
                    age_band=bracket or None,
                    gender="m" if r.get("gender") == "Male" else "f",
                    race_hint=race,
                    license="CC-BY-4.0",
                    consent_basis="balanced race/gender/age brackets",
                    source_url="https://github.com/joojs/fairface",
                    usable_for_age=True,
                    train_ok=False,    # brackets: auxiliary/eval, not exact training
                    eval_ok=True,
                )
