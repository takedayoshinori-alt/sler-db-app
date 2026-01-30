import streamlit as st
import pandas as pd
from database import get_data, save_data
from datetime import datetime

def show_company_page():
    current_date = datetime.now().strftime("%Y-%m-%d")

    # --- 1. 新規登録セクション ---
    st.header("📝 新規会社データ追加")
    with st.form("company_form", clear_on_submit=True):
        name = st.text_input("会社名")
        address = st.text_input("住所")
        tel = st.text_input("電話番号")
        features = st.text_input("特徴")
        logo = st.checkbox("ロゴ使用許可")
        submitted = st.form_submit_button("保存")

        if submitted:
            if name:
                df = get_data("Company")
                new_id = int(df["id"].max() + 1) if not df.empty else 1
                new_entry = {
                    "id": new_id, "name": name, "address": address, 
                    "tel": tel, "features": features, "logo": logo, "updated_at": current_date
                }
                updated_df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
                save_data("Company", updated_df)
                st.cache_data.clear()
                st.success("会社データを保存しました！")
                st.rerun()
            else:
                st.warning("会社名を入力してください")

    # データ読み込み（共通）
    company_df = get_data("Company")
    
    # --- 2. 編集・修正セクション ---
    st.markdown("---")
    st.header("✏️ 登録データの修正")
    
    if not company_df.empty:
        # 修正対象の選択
        edit_target_name = st.selectbox("修正する会社を選択してください", options=company_df['name'].tolist(), key="edit_selector")
        
        # 選択された行のデータを抽出
        target_data = company_df[company_df['name'] == edit_target_name].iloc[0]

        # 修正フォーム
        with st.form("edit_company_form"):
            # valueに現在の値をセットすることで初期値を表示
            upd_name = st.text_input("会社名", value=target_data["name"])
            upd_address = st.text_input("住所", value=target_data["address"])
            upd_tel = st.text_input("電話番号", value=target_data["tel"])
            upd_features = st.text_area("特徴", value=target_data["features"])
            upd_logo = st.checkbox("ロゴ使用許可", value=bool(target_data["logo"]))
            
            update_submitted = st.form_submit_button("修正内容を保存")

            if update_submitted:
                # 該当するIDの行を更新
                idx = company_df[company_df['id'] == target_data['id']].index
                company_df.loc[idx, "name"] = upd_name
                company_df.loc[idx, "address"] = upd_address
                company_df.loc[idx, "tel"] = upd_tel
                company_df.loc[idx, "features"] = upd_features
                company_df.loc[idx, "logo"] = upd_logo
                company_df.loc[idx, "updated_at"] = current_date
                
                save_data("Company", company_df)
                st.cache_data.clear()
                st.success(f"{upd_name} のデータを更新しました！")
                st.rerun()
    else:
        st.info("データがありません。")

    # --- 3. 関連付けセクション ---
    st.markdown("---")
    st.header("📝 会社とロボットメーカー関連付け")
    
    company_list = company_df['name'].tolist()
    robot_df = get_data("Robot")
    robot_list = robot_df['name'].tolist()

    with st.form("company_robot_form", clear_on_submit=True):
        selected_company = st.selectbox("会社名", options=company_list)
        selected_robot = st.selectbox("ロボットメーカー", options=robot_list)
        submitted_relation = st.form_submit_button("関連付けを保存")

        if submitted_relation:
            if selected_company and selected_robot:
                rel_df = get_data("Company_Robot_Relation")
                company_id = int(company_df[company_df['name'] == selected_company]['id'].values[0])
                robot_id = int(robot_df[robot_df['name'] == selected_robot]['id'].values[0])
                
                new_rel_id = int(rel_df["id"].max() + 1) if not rel_df.empty else 1
                new_relation = {
                    "id": new_rel_id, "company_id": company_id, 
                    "robot_id": robot_id, "updated_at": current_date
                }
                
                updated_rel_df = pd.concat([rel_df, pd.DataFrame([new_relation])], ignore_index=True)
                save_data("Company_Robot_Relation", updated_rel_df)
                st.cache_data.clear()
                st.success("関連付けを保存しました！")
                st.rerun()