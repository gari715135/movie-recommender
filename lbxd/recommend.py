from __future__ import annotations
import pandas as pd
from typing import Dict

from .similarity import pearson
from .config import LOGGER

__all__ = ["recommend_movies"]


def recommend_movies(
    friends_data: Dict[str, Dict],
    df_user: pd.DataFrame,
    *,
    rating_w: float = 5.0,
    like_w: float = 1.0,
    pop_w: float = 1.0,
    top_n: int | None = 50,
) -> pd.DataFrame:
    """Similarity-weighted movie recommendations."""
    me_r = df_user.set_index("id")["rating"].replace(-1, pd.NA)

    # similarity per friend
    sim = {
        friend: pearson(me_r, info["df_b"].set_index("id")["rating"].replace(-1, pd.NA))
        for friend, info in friends_data.items()
    }

    # unseen films
    seen = set(me_r.index)
    unseen = pd.concat(
        [info["df_b"][~info["df_b"]["id"].isin(seen)].assign(sim=sim[friend]) for friend, info in friends_data.items()]
    )
    if unseen.empty:
        return unseen

    # aggregate
    agg = (
        unseen.groupby(["id", "title", "link"])
        .apply(
            lambda g: pd.Series(
                {
                    "pred_rating": (
                        (g["rating"] * g["sim"]).sum() / g["sim"].sum() if g["sim"].sum() else g["rating"].mean()
                    ),
                    "like_sum": (g["liked"] * g["sim"]).sum(),
                    "num_friends": len(g),
                }
            )
        )
        .reset_index()
    )

    # scoring
    norm = lambda s: (s - s.min()) / (s.max() - s.min()) if s.nunique() > 1 else s / s.max()
    agg["score"] = (
        rating_w * agg["pred_rating"] / 5.0 + like_w * norm(agg["like_sum"]) + pop_w * norm(agg["num_friends"])
    )

    out = agg.sort_values("score", ascending=False)
    LOGGER.info("Generated %d recommendations", len(out))
    return out.head(top_n) if top_n else out
