from __future__ import annotations
import concurrent.futures as cf
from typing import Dict, List

import pandas as pd
from bs4 import BeautifulSoup

from .similarity import pearson 
from .config import LOGGER, DOMAIN, MAX_WORKERS
from .network import get_html

__all__ = ["scrape_films", "list_friends"]

# ───────────────────── helpers ──────────────────────
def _transform_rating(raw: str) -> float:
    raw = (raw or "").strip()
    full, half = raw.count("★"), "½" in raw
    rating = full + (0.5 if half else 0.0)
    return rating if 0.0 <= rating <= 5.0 else -1.0

def _parse_film_page(html: str, store: Dict[str, List]):
    soup = BeautifulSoup(html, "lxml")
    for li in soup.select("ul.poster-list > li"):
        link = li.div["data-target-link"]
        store["id"].append(link.strip("/").split("/")[-1])
        store["title"].append(li.img["alt"])
        rating_raw = li.select_one("p.poster-viewingdata")
        store["rating"].append(_transform_rating(rating_raw.get_text(strip=True) if rating_raw else ""))
        store["liked"].append(li.select_one("span.like") is not None)
        store["link"].append(link)

# ───────────────────── scrape_films ─────────────────
def scrape_films(username: str) -> pd.DataFrame:
    """Return every film logged by *username*."""
    url0 = f"{DOMAIN}/{username}/films/"
    html0 = get_html(url0)
    soup0 = BeautifulSoup(html0, "lxml")

    pages = soup0.select("li.paginate-page")
    total = int(pages[-1].text) if pages else 1
    LOGGER.info("%s - scraping %d film page(s)", username, total)

    store = {k: [] for k in ["id", "title", "rating", "liked", "link"]}
    _parse_film_page(html0, store)

    # fetch remaining pages in parallel
    urls = [f"{DOMAIN}/{username}/films/page/{n}/" for n in range(2, total + 1)]
    with cf.ThreadPoolExecutor(MAX_WORKERS) as pool:
        for html in pool.map(get_html, urls):
            _parse_film_page(html, store)

    return pd.DataFrame(store)

def scrape_friends(
    username: str,
    friends: list[str],
    max_workers: int = MAX_WORKERS,
) -> tuple[pd.DataFrame, dict, pd.DataFrame]:
    """
    Concurrently scrape every friend in *friends*.

    Returns
    -------
    df_friends   : DataFrame <username, total_index>  (friend-level scores)
    friends_data : dict  friend → {"df_b": DataFrame, "index": float}
    df_me        : your own film DataFrame
    """
    LOGGER.info("Scraping %d friends of %s", len(friends), username)

    # your own films
    df_me = scrape_films(username)

    def _fetch(friend: str):
        df_b = scrape_films(friend)
        idx = pearson(
            df_me.set_index("id")["rating"], df_b.set_index("id")["rating"]
        )
        return friend, df_b, idx

    friends_data: dict = {}
    with cf.ThreadPoolExecutor(max_workers) as pool:
        for friend, df_b, idx in pool.map(_fetch, friends):
            friends_data[friend] = {"df_b": df_b, "index": idx}

    df_friends = pd.DataFrame(
        {"username": k, "total_index": v["index"]} for k, v in friends_data.items()
    )
    return df_friends, friends_data, df_me

def _friends_page(username: str, path: str) -> List[str]:
    res, url = [], f"{DOMAIN}/{username}/{path}/"
    while True:
        soup = BeautifulSoup(get_html(url), "lxml")
        res += [a["href"].strip("/") for a in soup.select("a.avatar")]
        nxt = soup.select_one("a.next")
        if not nxt:
            break
        url = DOMAIN + nxt["href"]
    return res

def list_friends(username: str, mode: str = "mutual") -> List[str]:
    """Return `<following | followers | mutual>` friends."""
    if mode not in {"following", "followers", "mutual"}:
        raise ValueError("mode must be following / followers / mutual")
    if mode == "mutual":
        f1, f2 = set(_friends_page(username, "following")), set(_friends_page(username, "followers"))
        return sorted(f1 & f2)
    return sorted(_friends_page(username, mode))