"""Dataset adapters: each turns one raw dataset into canonical manifest rows.

Add a new dataset by writing `adapters/<name>.py` exposing:

    def iter_rows(root: str) -> Iterator[dict]: ...   # yields make_row(...) dicts

Keep adapters pure (parse labels -> rows). Face alignment, ITA, and quality are
applied later in notebook 02 so every dataset is processed identically.
"""
from . import utkface, fairface  # noqa: F401

REGISTERED = {
    "UTKFace": utkface,
    "FairFace": fairface,
}
