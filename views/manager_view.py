import streamlit as st
import pandas as pd
from database import get_data, save_data # 新しい関数をインポート
from datetime import datetime

def show_manager_page():
    current_date = datetime.now().strftime("%Y-%m-%d")

    # --- 1. 会社リストを取得 (selectbox用) ---
    company_df = get_data("Company")
    company_list = company_df['name'].tolist()
    
    st.header("📝 担当者追加")
    
    if not company_list:
        st.warning("先に「会社登録」から会社を登録してください。")
        return

    with st.form("manager_form", clear_on_submit=True):
        select_company = st.selectbox("会社名", options=company_list)
        manager = st.text_input("担当者")
        post = st.text_input("役職")
        tel = st.text_input("電話番号")
        mail = st.text_input("mail")
        submitted = st.form_submit_button("保存")

        if submitted:
            if manager:
                # --- 2. データの読み込みと追加 ---
                manager_df = get_data("Manager")
                
                # 新しいIDの採番
                new_id = int(manager_df["id"].max() + 1) if not manager_df.empty else 1
                
                # 新しいデータの作成
                new_entry = {
                    "id": new_id,
                    "select_company": select_company,
                    "manager": manager,
                    "post": post,
                    "tel": tel,
                    "mail": mail,
                    "updated_at": current_date
                }
                
                # 結合と保存
                updated_manager_df = pd.concat([manager_df, pd.DataFrame([new_entry])], ignore_index=True)
                save_data("Manager", updated_manager_df)
                st.cache_data.clear()
                
                st.success("担当者データを保存しました！")
                st.rerun()
            else:
                st.warning("担当者を入力してください")