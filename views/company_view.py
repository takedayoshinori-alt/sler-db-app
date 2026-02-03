import streamlit as st
import pandas as pd
from database import get_data, save_data
from datetime import datetime

def show_company_page():
    current_date = datetime.now().strftime("%Y-%m-%d")

    ## セッション（メモリ）にデータがなければ読み込む
    if "company_df" not in st.session_state:
        st.session_state.company_df = get_data("Company")
    if "robot_df" not in st.session_state:
        st.session_state.robot_df = get_data("Robot")
    if "plc_df" not in st.session_state:
        st.session_state.plc_df = get_data("Plc")
    # 以降、すべての処理で st.session_state.company_df を使う
    
    company_df = st.session_state.company_df
    robot_df = st.session_state.robot_df
    plc_df = st.session_state.plc_df
    rel_robot_df = get_data("Company_Robot_Relation")
    rel_plc_df = get_data("Company_Plc_Relation")

    company_list = company_df['name'].tolist() if not company_df.empty else []
    robot_list = robot_df['name'].tolist() if not robot_df.empty else []
    plc_list = plc_df['name'].tolist() if not plc_df.empty else []

    # --- 1. 新規登録セクション ---
    st.header("📝 新規会社データ追加")
    with st.form("company_form", clear_on_submit=True):
        name = st.text_input("会社名")
        address = st.text_input("住所")
        tel = st.text_input("電話番号")
        features = st.text_input("特徴")
        logo = st.checkbox("ロゴ使用許可")
        if st.form_submit_button("保存"):
            if name:
                new_id = int(company_df["id"].max() + 1) if not company_df.empty else 1
                new_entry = {"id": new_id, "name": name, "address": address, "tel": tel, "features": features, "logo": logo, "updated_at": current_date}
                save_data("Company", pd.concat([company_df, pd.DataFrame([new_entry])], ignore_index=True))
                st.rerun()
            else:
                st.warning("会社名を入力してください")

    # --- 2. 修正セクション ---
    st.markdown("---")
    st.header("✏️ 登録データの修正")
    if not company_df.empty:
        edit_target = st.selectbox("修正する会社を選択", options=company_list, key="edit_sel")
        target_row = company_df[company_df['name'] == edit_target].iloc[0]
        with st.form("edit_form"):
            u_name = st.text_input("会社名", value=target_row["name"])
            u_addr = st.text_input("住所", value=target_row["address"])
            u_tel = st.text_input("電話番号", value=target_row["tel"])
            u_feat = st.text_area("特徴", value=target_row["features"])
            u_logo = st.checkbox("ロゴ使用許可", value=bool(target_row["logo"]))
            if st.form_submit_button("修正内容を保存"):
                idx = company_df[company_df['id'] == target_row['id']].index
                company_df.loc[idx, ["name", "address", "tel", "features", "logo", "updated_at"]] = [u_name, u_addr, u_tel, u_feat, u_logo, current_date]
                save_data("Company", company_df)
                st.rerun()

    # --- 3. 関連付けセクション (ロボット) ---
    st.markdown("---")
    st.header("🤖 ロボットメーカー関連付け")
    with st.form("rel_robot_form"):
        sel_c = st.selectbox("会社名", options=company_list, key="rel_c_r")
        sel_r = st.selectbox("ロボットメーカー", options=robot_list)
        if st.form_submit_button("関連付けを保存"):
            c_id = company_df[company_df['name'] == sel_c]['id'].values[0]
            r_id = robot_df[robot_df['name'] == sel_r]['id'].values[0]
            new_id = int(rel_robot_df["id"].max() + 1) if not rel_robot_df.empty else 1
            new_rel = {"id": new_id, "company_id": c_id, "robot_id": r_id, "updated_at": current_date}
            save_data("Company_Robot_Relation", pd.concat([rel_robot_df, pd.DataFrame([new_rel])], ignore_index=True))
            st.rerun()

    # --- 4. 関連付けセクション (PLC) ---
    st.markdown("---")
    st.header("🔌 PLCメーカー関連付け")
    with st.form("rel_plc_form"):
        sel_c = st.selectbox("会社名", options=company_list, key="rel_c_p")
        sel_p = st.selectbox("PLCメーカー", options=plc_list)
        if st.form_submit_button("関連付けを保存"):
            c_id = company_df[company_df['name'] == sel_c]['id'].values[0]
            p_id = plc_df[plc_df['name'] == sel_p]['id'].values[0]
            new_id = int(rel_plc_df["id"].max() + 1) if not rel_plc_df.empty else 1
            new_rel = {"id": new_id, "company_id": c_id, "plc_id": p_id, "updated_at": current_date}
            save_data("Company_Plc_Relation", pd.concat([rel_plc_df, pd.DataFrame([new_rel])], ignore_index=True))
            st.rerun()

    # --- 5. 関連付けセクション (Camera2D) ---
    st.markdown("---")
    st.header("📷 2Dカメラメーカー関連付け")
    camera2D_df = get_data("Camera2D")
    camera2D_list = camera2D_df['name'].tolist() if not camera2D_df.empty else []
    rel_camera2D_df = get_data("Company_Camera2D_Relation")
    with st.form("rel_camera2D_form"):
        sel_c = st.selectbox("会社名", options=company_list, key="rel_c_cam")
        sel_cam = st.selectbox("2Dカメラメーカー", options=camera2D_list)
        if st.form_submit_button("関連付けを保存"):
            c_id = company_df[company_df['name'] == sel_c]['id'].values[0]
            cam_id = camera2D_df[camera2D_df['name'] == sel_cam]['id'].values[0]
            new_id = int(rel_camera2D_df["id"].max() + 1) if not rel_camera2D_df.empty else 1
            new_rel = {"id": new_id, "company_id": c_id, "camera2D_id": cam_id, "updated_at": current_date}
            save_data("Company_Camera2D_Relation", pd.concat([rel_camera2D_df, pd.DataFrame([new_rel])], ignore_index=True))
            st.rerun()

    # --- 6. 関連付けセクション (Camera3D) ---
    st.markdown("---")
    st.header("📹 3Dカメラメーカー関連付け")
    camera3D_df = get_data("Camera3D")
    camera3D_list = camera3D_df['name'].tolist() if not camera3D_df.empty else []
    rel_camera3D_df = get_data("Company_Camera3D_Relation")
    with st.form("rel_camera3D_form"):
        sel_c = st.selectbox("会社名", options=company_list, key="rel_c_cam3d")
        sel_cam3d = st.selectbox("3Dカメラメーカー", options=camera3D_list)
        if st.form_submit_button("関連付けを保存"):
            c_id = company_df[company_df['name'] == sel_c]['id'].values[0]
            cam3d_id = camera3D_df[camera3D_df['name'] == sel_cam3d]['id'].values[0]
            new_id = int(rel_camera3D_df["id"].max() + 1) if not rel_camera3D_df.empty else 1
            new_rel = {"id": new_id, "company_id": c_id, "camera3D_id": cam3d_id, "updated_at": current_date}
            save_data("Company_Camera3D_Relation", pd.concat([rel_camera3D_df, pd.DataFrame([new_rel])], ignore_index=True))
            st.rerun()

            
