# lbxd/__init__.py
from .scraper import scrape_films, list_friends, scrape_friends   # ← add this
from .similarity import friend_similarity
from .recommend import recommend_movies

__all__ = [
    "scrape_films",
    "list_friends",
    "scrape_friends",        # ← new
    "friend_similarity",
    "recommend_movies",
]