# 🎬 Letterboxd Friend-Based Recommender

A one-stop **Streamlit web app** + **modular Python library** that scrapes your Letterboxd profile and your friends' film logs, measures how closely their tastes match yours, and serves up personalised movie recommendations.

---

## ✨ Features

* **One-click web UI** - no command line needed, powered by Streamlit.
* **Parallel scraping** with respectful back-off & retry logic.
* **Similarity-aware rankings** - Pearson-based friend matching + weighted recommendation engine.
* **Downloadable CSV** of recs for offline use.
* Clean, testable package (`lbxd/`) with typed sub-modules and docstrings.
* MIT-licensed & deployment-ready (Streamlit Cloud / HuggingFace Spaces).

---

## 📂 Project structure

```text
movie-recommender/
│
├── lbxd/               # modular package
│   ├── config.py       # constants & logging
│   ├── network.py      # HTTP session helpers
│   ├── scraper.py      # scrape_films(), list_friends(), scrape_friends()
│   ├── similarity.py   # pearson(), friend_similarity()
│   └── recommend.py    # recommend_movies()
│
├── app.py              # Streamlit front-end
├── requirements.txt    # pip deps
├── README.md           # you are here
└── LICENSE             # MIT
```

---

## 🚀 Quick start

```bash
# clone & install deps
$ git clone https://github.com/gari715135/movie-recommender.git
$ cd movie-recommender
$ python -m venv .venv && source .venv/bin/activate
$ pip install -r requirements.txt

# run the web app (opens in browser)
$ streamlit run app.py
```

1. Enter your Letterboxd username.
2. Choose **mutual**, **following**, or **followers** list.
3. Hit **Generate** - you'll see:
   * **Closest-match friends** table with similarity scores.
   * **Recommended movies** (title, predicted rating, #friends, composite score).
4. Download the CSV if you like.

---

## 🏗️  Library usage (optional)

```python
from lbxd import list_friends, scrape_friends, recommend_movies

user = "gari4107"
friends = list_friends(user, "mutual")

# threaded scrape of all friends + self
df_friends, friends_data, df_me = scrape_friends(user, friends)

# top 30 recs
recs = recommend_movies(friends_data, df_me, top_n=30)
print(recs.head())
```

---

## 🔧 Configuration knobs

| Location | Variable | Purpose |
|----------|----------|---------|
| `lbxd/config.py` | `REQUEST_DELAY` | polite delay between HTTP requests (s) |
|  | `MAX_WORKERS` | thread-pool size for scraping |
|  | `POOL_SIZE` | underlying urllib3 connection-pool size |
| `lbxd/recommend.py` | `rating_w`, `like_w`, `pop_w` | weights in composite score |

---

## 🖼️  Screenshots

> _Add a couple screenshots or a GIF of the app here._

---

## 📜 License

[MIT](LICENSE)

---

## 🤝 Contributing

PRs & issues welcome!  Take a look at the
[open issues](https://github.com/<your-handle>/movie-recommender/issues) or file a new one.

1. Fork the repo & create your branch.
2. **Black-format** & add tests where appropriate.
3. Submit a pull request - we'll review ASAP.

---

## 🛣  Roadmap / TODO

- [ ] Cache HTML responses on disk to avoid re-scraping.
- [ ] Support genre filters & minimum-rating thresholds.
- [ ] Dockerfile & CI deploy to Streamlit Cloud.
- [ ] Unit tests for every module.

---

> **Made with ❤️ & 🍿by@<your-handle>**

