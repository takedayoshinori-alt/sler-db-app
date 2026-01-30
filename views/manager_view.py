import streamlit as st
import pandas as pd
from database import get_data, save_data
from datetime import datetime

def show_manager_page():
    current_date = datetime.now().strftime("%Y-%m-%d")

    # --- 1. 基礎データの読み込み ---
    company_df = get_data("Company")
    company_list = company_df['name'].tolist()
    manager_df = get_data("Manager")
    
    st.header("📝 担当者追加")
    
    if not company_list:
        st.warning("先に「会社登録」から会社を登録してください。")
        return

    # --- 2. 新規追加フォーム ---
    with st.form("manager_form", clear_on_submit=True):
        select_company = st.selectbox("会社名", options=company_list)
        manager = st.text_input("担当者名")
        post = st.text_input("役職")
        tel = st.text_input("電話番号")
        mail = st.text_input("メールアドレス")
        submitted = st.form_submit_button("新規保存")

        if submitted:
            if manager:
                new_id = int(manager_df["id"].max() + 1) if not manager_df.empty else 1
                new_entry = {
                    "id": new_id,
                    "select_company": select_company,
                    "manager": manager,
                    "post": post,
                    "tel": tel,
                    "mail": mail,
                    "updated_at": current_date
                }
                updated_manager_df = pd.concat([manager_df, pd.DataFrame([new_entry])], ignore_index=True)
                save_data("Manager", updated_manager_df)
                st.cache_data.clear()
                st.success(f"{manager} さんのデータを保存しました！")
                st.rerun()
            else:
                st.warning("担当者名を入力してください")

    # --- 3. 修正・削除セクション ---
    st.markdown("---")
    st.header("✏️ 担当者データの修正・削除")

    if not manager_df.empty:
        # 「会社名：担当者名」という表示形式にして選びやすくする
        manager_df["display_name"] = manager_df["select_company"] + " : " + manager_df["manager"]
        edit_target = st.selectbox("修正する担当者を選択", options=manager_df["display_name"].tolist())
        
        # 選択されたデータの抽出
        target_row = manager_df[manager_df["display_name"] == edit_target].iloc[0]

        with st.form("edit_manager_form"):
            # 初期値をセット
            upd_company = st.selectbox("会社名", options=company_list, index=company_list.index(target_row["select_company"]))
            upd_manager = st.text_input("担当者名", value=target_row["manager"])
            upd_post = st.text_input("役職", value=target_row["post"])
            upd_tel = st.text_input("電話番号", value=target_row["tel"])
            upd_mail = st.text_input("メールアドレス", value=target_row["mail"])
            
            col1, col2 = st.columns(2)
            with col1:
                update_btn = st.form_submit_button("修正内容を保存")
            with col2:
                delete_btn = st.form_submit_button("この担当者を削除", type="primary")

            if update_btn:
                idx = manager_df[manager_df["id"] == target_row["id"]].index
                manager_df.loc[idx, "select_company"] = upd_company
                manager_df.loc[idx, "manager"] = upd_manager
                manager_df.loc[idx, "post"] = upd_post
                manager_df.loc[idx, "tel"] = upd_tel
                manager_df.loc[idx, "mail"] = upd_mail
                manager_df.loc[idx, "updated_at"] = current_date
                
                # 不要な表示用カラムを削除して保存
                save_df = manager_df.drop(columns=["display_name"])
                save_data("Manager", save_df)
                st.cache_data.clear()
                st.success("担当者情報を更新しました！")
                st.rerun()

            if delete_btn:
                # 削除処理
                updated_df = manager_df[manager_df["id"] != target_row["id"]]
                save_df = updated_df.drop(columns=["display_name"])
                save_data("Manager", save_df)
                st.cache_data.clear()
                st.warning(f"{target_row['manager']} さんのデータを削除しました")
                st.rerun()
    else:
        st.info("登録されている担当者がいません。")