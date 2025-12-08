#%%writefile app.py
import streamlit as st
import pandas as pd
import datetime
import sys
import os

# ---------------------------------------------------------
# db_handler.py を読み込めるようにパスを通す
# ---------------------------------------------------------
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import db_handler

# ---------------------------------------------------------
# 1. 設定 & 定数
# ---------------------------------------------------------
PAGE_TITLE = "投票アプリ"
APP_HEADER = "🗳️ 議題一覧"
APP_DESCRIPTION = "みんなで意見を集めよう！気になる議題に投票できます。"

# ---------------------------------------------------------
# 2. ページ設定
# ---------------------------------------------------------
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon="🗳️",
    layout="centered"
)

# ---------------------------------------------------------
# 4. ヘッダー
# ---------------------------------------------------------
st.title(APP_HEADER)
st.caption(APP_DESCRIPTION)
st.divider()

# ---------------------------------------------------------
# 5. スプレッドシートから議題を取得
# ---------------------------------------------------------
topics_df = db_handler.get_topics_from_sheet()

if topics_df.empty:
    st.info("まだ議題が登録されていません。")
    st.stop()

# ---------------------------------------------------------
# 6. 投票データも取得
# ---------------------------------------------------------
votes_df = db_handler.get_votes_from_sheet()

# 今日の日付
today = datetime.date.today()

for index, topic in topics_df.iterrows():

    # 締切日を取得
    deadline_str = topic.get("deadline", "")
    try:
        deadline = datetime.datetime.strptime(deadline_str, "%Y-%m-%d").date()
    except:
        deadline = None  # 日付不明なら表示する

    # 締切済みならスキップ
    if deadline and today > deadline:
        continue  # この議題は表示しない

    # ----- 以下は既存の表示処理 -----
    title = topic["title"]
    author = topic.get("author", "不明")
    options = topic["options"].split("/")

    topic_votes = votes_df[votes_df["topic_title"] == title] if not votes_df.empty else pd.DataFrame()

    with st.container(border=True):
        st.subheader(title)
        st.caption(f"作成者：{author}｜締切：{deadline_str}")

        col1, col2 = st.columns([1, 2])

        with col1:
            selected_option = st.radio(
                "投票してください",
                options,
                key=f"radio_{index}"
            )

            if st.button("👍 投票する", key=f"vote_{index}"):
                db_handler.add_vote_to_sheet(title, selected_option)
                st.success("投票しました！")
                st.rerun()

        with col2:
            st.write("### 📊 現在の投票数")
            if topic_votes.empty:
                for opt in options:
                    st.write(f"{opt}：0 票")
            else:
                counts = topic_votes["option"].value_counts()
                for opt in options:
                    st.write(f"{opt}：{counts.get(opt, 0)} 票")



