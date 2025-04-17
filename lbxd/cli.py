"""Command-line interface:  python -m lbxd.cli <username>"""
from __future__ import annotations
import argparse
import pathlib
from lbxd import list_friends, recommend_movies
from lbxd.scraper import scrape_friends   # keeps threading & logging intact

def _args(argv=None):
    p = argparse.ArgumentParser(description="Letterboxd friend recommender")
    p.add_argument("username")
    p.add_argument("--mode", choices=["mutual", "following", "followers"], default="mutual")
    p.add_argument("--top", type=int, default=25)
    p.add_argument("-o", "--out", type=pathlib.Path, default=pathlib.Path("recommendations.csv"))
    return p.parse_args(argv)

def main(argv=None):
    a = _args(argv)
    friends = list_friends(a.username, a.mode)
    df_friends, friends_data, df_me = scrape_friends(a.username, friends)
    recs = recommend_movies(friends_data, df_me, top_n=a.top)
    recs.to_csv(a.out, index=False)
    print(f"Wrote {len(recs)} rows → {a.out.resolve()}")

if __name__ == "__main__":
    main()