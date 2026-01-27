import streamlit as st
import pandas as pd
from database import get_data, save_data # 修正した関数をインポート
from datetime import datetime

def show_company_page():
    # 注意: ここでの「検索」はヘッダーのみ。実際の検索は別ファイル
    st.header("📝 新規会社データ追加")

    current_date = datetime.now().strftime("%Y-%m-%d")

    # --- 1. 会社登録セクション ---
    with st.form("company_form", clear_on_submit=True):
        name = st.text_input("会社名")
        address = st.text_input("住所")
        tel = st.text_input("電話番号")
        features = st.text_input("特徴")
        logo = st.checkbox("ロゴ使用許可")
        submitted = st.form_submit_button("保存")

        if submitted:
            if name:
                # 現在のデータを取得
                df = get_data("Company")
                
                # 新しいIDを採番 (既存データがあれば最大値+1、なければ1)
                new_id = int(df["id"].max() + 1) if not df.empty else 1
                
                # 追加する新しい行を辞書形式で作成
                new_entry = {
                    "id": new_id,
                    "name": name,
                    "address": address,
                    "tel": tel,
                    "features": features,
                    "logo": logo,
                    "updated_at": current_date
                }
                
                # 既存のDataFrameに結合して保存
                updated_df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
                save_data("Company", updated_df)
                st.cache_data.clear()
                
                st.success("会社データを保存しました！")
                st.rerun()
            else:
                st.warning("会社名を入力してください")

    # --- 2. リスト取得 (関連付け用) ---
    company_df = get_data("Company")
    company_list = company_df['name'].tolist()
    
    robot_df = get_data("Robot")
    robot_list = robot_df['name'].tolist()

    # --- 3. 会社とロボットメーカー関連付け ---
    st.header("📝 会社とロボットメーカー関連付け")
    with st.form("company_robot_form", clear_on_submit=True):
        selected_company = st.selectbox("会社名", options=company_list)
        selected_robot = st.selectbox("ロボットメーカー", options=robot_list)
        submitted_relation = st.form_submit_button("関連付けを保存")

        if submitted_relation:
            if selected_company and selected_robot:
                # 各種データの読み込み
                rel_df = get_data("Company_Robot_Relation")
                
                # 会社IDとロボットIDを名前から特定
                company_id = int(company_df[company_df['name'] == selected_company]['id'].values[0])
                robot_id = int(robot_df[robot_df['name'] == selected_robot]['id'].values[0])
                
                # 新しいIDを採番
                new_rel_id = int(rel_df["id"].max() + 1) if not rel_df.empty else 1
                
                new_relation = {
                    "id": new_rel_id,
                    "company_id": company_id,
                    "robot_id": robot_id,
                    "updated_at": current_date
                }
                
                # 保存
                updated_rel_df = pd.concat([rel_df, pd.DataFrame([new_relation])], ignore_index=True)
                save_data("Company_Robot_Relation", updated_rel_df)
                st.cache_data.clear()
                
                st.success("関連付けを保存しました！")
                st.rerun()
            else:
                st.warning("会社名とロボットメーカーを選択してください")