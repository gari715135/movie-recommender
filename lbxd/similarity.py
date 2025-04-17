from __future__ import annotations
import numpy as np
import pandas as pd
from typing import Dict

from .config import LOGGER

__all__ = ["pearson", "friend_similarity"]


def pearson(x: pd.Series, y: pd.Series) -> float:
    """Non-negative Pearson r on common IDs (returns 0 when undefined)."""
    x, y = x.align(y, join="inner")
    mask = (~x.isna()) & (~y.isna())
    if mask.sum() < 3:
        return 0.0
    x, y = x[mask], y[mask]
    if x.nunique() == 1 or y.nunique() == 1:
        return 0.0
    with np.errstate(divide="ignore", invalid="ignore"):
        r = np.corrcoef(x, y)[0, 1]
    return max(0.0, float(r)) if not np.isnan(r) else 0.0


def friend_similarity(df_me: pd.DataFrame, friends_data: Dict[str, Dict]) -> pd.DataFrame:
    """Return DataFrame <username, similarity> sorted descending."""
    me_r = df_me.set_index("id")["rating"].replace(-1, pd.NA)
    rows = []
    for friend, info in friends_data.items():
        fr_r = info["df_b"].set_index("id")["rating"].replace(-1, pd.NA)
        rows.append({"username": friend, "similarity": pearson(me_r, fr_r)})
    out = pd.DataFrame(rows).sort_values("similarity", ascending=False).reset_index(drop=True)
    LOGGER.info("Computed similarity for %d friends", len(out))
    return out
