import streamlit as st
import pandas as pd
from database import get_data, save_data # database.pyから新しい関数を読み込む
from datetime import datetime

def show_robot_page():
    # ページヘッダー
    st.header("📝 ロボットメーカー追加")

    current_date = datetime.now().strftime("%Y-%m-%d")

    # --- 登録フォーム ---
    with st.form("robot_form", clear_on_submit=True):
        robot_name = st.text_input("ロボット名")
        submitted = st.form_submit_button("保存")

        if submitted:
            if robot_name:
                # 1. 既存データの読み込み
                df = get_data("Robot")
                
                # 2. 新しいIDの採番 (最大ID + 1)
                new_id = int(df["id"].max() + 1) if not df.empty else 1
                
                # 3. 新しい行の作成
                new_entry = {
                    "id": new_id,
                    "name": robot_name,
                    "updated_at": current_date
                }
                
                # 4. データの結合と保存
                updated_df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
                save_data("Robot", updated_df)
                st.cache_data.clear()
                
                st.success(f"ロボットメーカー「{robot_name}」を保存しました！")
                st.rerun()
            else:
                st.warning("ロボット名を入力してください")

    st.header("📝 対応PLCメーカー追加")

    # --- 登録フォーム ---
    with st.form("plc_form", clear_on_submit=True):
        plc_name = st.text_input("メーカー名")
        submitted = st.form_submit_button("保存")

        if submitted:
            if plc_name:
                # 1. 既存データの読み込み
                df = get_data("Plc")
                
                # 2. 新しいIDの採番 (最大ID + 1)
                new_id = int(df["id"].max() + 1) if not df.empty else 1
                
                # 3. 新しい行の作成
                new_entry = {
                    "id": new_id,
                    "name": plc_name,
                    "updated_at": current_date
                }
                
                # 4. データの結合と保存
                updated_df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
                save_data("Plc", updated_df)
                st.cache_data.clear()
                
                st.success(f"「{plc_name}」を保存しました！")
                st.rerun()
            else:
                st.warning("メーカー名を入力してください")