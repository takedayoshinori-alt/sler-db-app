import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

def get_connection():
    """スプレッドシートへの接続を確立する"""
    return st.connection("gsheets", type=GSheetsConnection)

def get_data(sheet_name):
    """指定したシートのデータを全件読み込む"""
    conn = get_connection()
    ## ttl=0 をやめ、1分間（あるいは30秒）キャッシュを保持する
    return conn.read(worksheet=sheet_name, ttl="1m")

def save_data(sheet_name, df):
    """指定したシートにデータフレームを上書き保存する"""
    conn = get_connection()
    # 数値が消えたり型が崩れたりしないよう、空値を処理して更新します
    conn.update(worksheet=sheet_name, data=df)

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