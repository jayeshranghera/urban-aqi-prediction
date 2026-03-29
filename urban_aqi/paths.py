"""Repository root resolution (works from project root or notebooks/)."""

from __future__ import annotations

from pathlib import Path


def project_root() -> Path:
    here = Path.cwd().resolve()
    if (here / "data").is_dir() and (here / "urban_aqi").is_dir():
        return here
    parent = here.parent
    if (parent / "data").is_dir() and (parent / "urban_aqi").is_dir():
        return parent
    return here
