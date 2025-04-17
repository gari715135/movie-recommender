from __future__ import annotations

import pandas as pd
import streamlit as st
import altair as alt

from lbxd import friend_similarity, list_friends, recommend_movies, scrape_friends
from lbxd.config import DOMAIN, MAX_WORKERS

# ───────────────────────── Streamlit page config ──────────────────────────
st.set_page_config(
    page_title="Letterboxd Recommender",
    page_icon="🎬",
    layout="wide",
)

st.title("🎬  Letterboxd Friend-Based Recommender")

# ───────────────────────── Sidebar inputs ────────────────────────────────
with st.sidebar:
    st.header("Parameters")
    user = st.text_input("Your Letterboxd username", value="gari4107")
    mode = st.selectbox("Which friend list?", ["mutual", "following", "followers"])
    top_n = st.slider("How many recommendations?", 5, 100, 25)
    run_btn = st.button("Generate")

if not run_btn:
    st.info("Enter your username, tweak parameters, then press **Generate**.")
    st.stop()

# ───────────────────────── Scraping ─────────────────────────
with st.spinner("Fetching friend list…"):
    friends = list_friends(user, mode)

if not friends:
    st.error(f"No {mode} friends found for **{user}**.")
    st.stop()

with st.spinner(f"Scraping {len(friends)} friends using {MAX_WORKERS} threads…"):
    df_friends, friends_data, df_me = scrape_friends(user, friends)

# ───────────────────────── Recommendations ───────────────────────────────
with st.spinner("Generating recommendations…"):
    recs = recommend_movies(friends_data, df_me, top_n=top_n)

if recs.empty:
    st.warning("No unseen movies left to recommend - you've watched everything!")
    st.stop()

# ensure link is fully-qualified and build HTML anchor for clickable title
recs["link"] = DOMAIN + recs["link"].astype(str)
recs["Title"] = recs.apply(lambda r: f'<a href="{r["link"]}" target="_blank">{r["title"]}</a>', axis=1)

# prepare table columns
nice = recs.rename(
    columns={
        "pred_rating": "Pred ★",
        "score": "Composite Score",
        "num_friends": "#Friends",
    }
)[["Title", "Pred ★", "Composite Score", "#Friends"]]
nice = nice.loc[nice["#Friends"] >= 1]
nice["#Friends"] = nice["#Friends"].astype(int)

st.subheader("🍿  Recommended Movies")
# Render as HTML so the links are clickable
st.write(nice.to_html(escape=False, index=False), unsafe_allow_html=True)
# CSV download
st.download_button(
    "Download CSV",
    recs.to_csv(index=False).encode(),
    file_name="recommendations.csv",
    mime="text/csv",
)
# explanation of composite score
with st.expander("What is the 'Composite Score'?"):
    st.markdown(
        """
        The **Composite Score** combines four factors:
        
        | Factor | Weight | Description |
        |--------|--------|-------------|
        | *Predicted rating* | 5x | Your expected ★-rating based on taste similarity. |
        | *Like ratio* | 1x | Weighted proportion of friends who marked the film as *liked*. |
        | *Popularity among friends* | 1x | How many friends have logged the film. |
        | *(Optional) extra weights* | - | Tune these in `lbxd/recommend.py`. |
        
        The higher the score, the stronger the recommendation.
        """
    )
# ───────────────────────── Similarity ─────────────────────────
# build similarity table and drop the user themselves if present
sim_df = friend_similarity(df_me, friends_data)
sim_df = sim_df[sim_df["username"] != user]

st.subheader("👥  Closest-Match Friends")
if sim_df.empty:
    st.write("No comparable friends with overlapping ratings yet.")
else:
    st.dataframe(
        sim_df.style.format({"similarity": "{:.2f}"}),
        hide_index=True,
        height=300,
    )

# ───────────────────────── Visualisation ────────────────────────────────
if not sim_df.empty:
    st.subheader("📊  Friend Similarity (top15)")
    top_sim = sim_df.head(15).sort_values("similarity", ascending=False)
    chart = (
        alt.Chart(top_sim.reset_index(drop=True))
        .mark_bar()
        .encode(
            y=alt.Y("username:N", sort="-x", title="Friend"),
            x=alt.X("similarity:Q", title="Similarity"),
            tooltip=["username", alt.Tooltip("similarity", format=".2f")],
        )
        .properties(height=400)
    )
    st.altair_chart(chart, use_container_width=True)
