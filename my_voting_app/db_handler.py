import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import streamlit as st
import os  # ファイルがあるか確認するために必要
import datetime # 日付を扱うために必要

# ---------------------------------------------------------
# 設定
# ---------------------------------------------------------
SPREADSHEET_NAME = "voting_app_db"
KEY_FILE = "key.json"

# ---------------------------------------------------------
# Googleスプレッドシートに接続する関数（ここが修正ポイント！）
# ---------------------------------------------------------
def connect_to_sheet():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    
    # パソコンに key.json があるかチェック
    if os.path.exists(KEY_FILE):
        # パソコンの場合：ファイルから読み込む
        creds = ServiceAccountCredentials.from_json_keyfile_name(KEY_FILE, scope)
    else:
        # Streamlit Cloudの場合：Secretsから読み込む
        # (Secretsに "gcp_service_account" という名前で登録されている前提)
        try:
            key_dict = dict(st.secrets["gcp_service_account"])
            creds = ServiceAccountCredentials.from_json_keyfile_dict(key_dict, scope)
        except Exception:
            # Secretsも設定されていない場合のエラーメッセージ
            st.error("認証エラー: key.jsonも見つからず、Secretsも設定されていません。")
            return None

    client = gspread.authorize(creds)
    sheet = client.open(SPREADSHEET_NAME)
    return sheet

# ---------------------------------------------------------
# データ操作用の関数
# ---------------------------------------------------------

# 1. 議題を保存する
def add_topic_to_sheet(title, author, options, deadline):
    sheet = connect_to_sheet()
    if sheet is None: return # 認証エラーなら何もしない
    
    worksheet = sheet.worksheet("topics")
    created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_row = [title, author, options, str(deadline), created_at]
    worksheet.append_row(new_row)

# 2. 議題を読み込む
def get_topics_from_sheet():
    try:
        sheet = connect_to_sheet()
        if sheet is None: return pd.DataFrame()
        
        worksheet = sheet.worksheet("topics")
        data = worksheet.get_all_records()
        return pd.DataFrame(data)
    except:
        return pd.DataFrame()

# 3. 投票を保存する
def add_vote_to_sheet(topic_title, option):
    sheet = connect_to_sheet()
    if sheet is None: return
    
    worksheet = sheet.worksheet("votes")
    voted_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_row = [topic_title, option, voted_at]
    worksheet.append_row(new_row)

# 4. 投票数を集計する
def get_votes_from_sheet():
    try:
        sheet = connect_to_sheet()
        if sheet is None: return pd.DataFrame()
        
        worksheet = sheet.worksheet("votes")
        data = worksheet.get_all_records()
        return pd.DataFrame(data)
    except:
        return pd.DataFrame()
