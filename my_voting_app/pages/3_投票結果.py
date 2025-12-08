import streamlit as st
import pandas as pd
from app import get_topics_from_sheet, get_votes_from_sheet

st.title("📊 投票結果ページ")

# データ読み込み
topics_df = get_topics_from_sheet()
votes_df = get_votes_from_sheet()

if topics_df.empty:
    st.warning("議題が登録されていません。")
else:
    topic_titles = topics_df["title"].tolist()

    # 議題選択
    selected_topic = st.selectbox("議題を選んでください", topic_titles)

    if selected_topic:
        # 該当議題の投票を抽出
        topic_votes = votes_df[votes_df["topic_title"] == selected_topic]

        if topic_votes.empty:
            st.info("まだ投票がありません。")
        else:
            # 集計
            result = topic_votes["option"].value_counts().reset_index()
            result.columns = ["選択肢", "投票数"]

            st.subheader(f"📝 議題: {selected_topic}")

            # 表
            st.table(result)

            # グラフ
            st.bar_chart(result.set_index("選択肢"))
