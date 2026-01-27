import streamlit as st
from database import init_db
from views import search_view, company_view, manager_view, robot_view, partnership_view

# ページ設定（一番最初に呼ぶ必要があります）
st.set_page_config(page_title="Sler企業データベース", layout="wide")

# 1. 起動時に接続確認（database.pyのinit_dbを呼び出す）
# これにより、スプレッドシートが見つからない場合に警告が出ます
init_db()

st.title("🚀 企業・パートナーシップデータベース")

# 2. タブで各ファイルを呼び出す
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔍 検索", 
    "🏢 会社登録", 
    "👤 担当者登録", 
    "🤖 ロボット登録",
    "🤝 パートナーシップ"
])

with tab1:
    search_view.show_search_page()

with tab2:
    company_view.show_company_page()

with tab3:
    manager_view.show_manager_page()

with tab4:
    robot_view.show_robot_page()

with tab5:
    partnership_view.show_partnership_page()