import streamlit as st
import pandas as pd
import time
from streamlit_gsheets import GSheetsConnection

def get_connection():
    """スプレッドシートへの接続を確立する"""
    return st.connection("gsheets", type=GSheetsConnection)

# キャッシュを有効にする（10分間はGoogleに再確認しない）
@st.cache_data(ttl=600)
def get_data(sheet_name):
    """指定したシートのデータを全件読み込む"""
    conn = get_connection()
    return conn.read(worksheet=sheet_name)

def save_data(sheet_name, df):
    conn = get_connection()
    conn.update(worksheet=sheet_name, data=df)
    # 以下の2行を追加して、メモリ内のデータをリセットする
    st.cache_data.clear()
    time.sleep(1)
    # セッション内の該当データを削除して、次回の get_data で最新を読み込ませる
    state_key = f"df_{sheet_name.lower()}"
    if state_key in st.session_state:
        del st.session_state[state_key]

def init_db():
    """
    SQL版との互換性のために残していますが、スプレッドシートでは
    ブラウザでシート（タブ）を作成済みであることを前提とします。
    """
    st.info("スプレッドシート接続モードで動作中")
    # ここで接続確認だけ行う
    try:
        get_data("Company")
    except Exception as e:
        st.error(f"シートの読み込みに失敗しました。シート名が正しいか確認してください: {e}")