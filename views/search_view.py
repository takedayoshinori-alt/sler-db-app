import streamlit as st
import pandas as pd
from database import get_data

def show_search_page():    
    st.header("🔍 検索")
    search_query = st.text_input("検索ワードを入力", key="search_input_main")

    # --- 1. データの読み込み ---
    # キャッシュ(ttl)が効いている間に一気に読み込みます
    df_company = get_data("Company")
    df_manager = get_data("Manager")
    df_partnership = get_data("Partnership")
    df_robot = get_data("Robot")
    df_relation_robot = get_data("Company_Robot_Relation")
    df_plc = get_data("Plc")
    df_relation_plc = get_data("Company_Plc_Relation")
    df_camera = get_data("Camera2D")
    df_relation_camera = get_data("Company_Camera2D_Relation")

    if df_company.empty:
        st.info("データがありません。先に会社登録を行ってください。")
        return

    # --- 2. テーブルの結合 ---
    df = pd.merge(df_company, df_manager[['select_company', 'manager', 'mail']], 
                  left_on='name', right_on='select_company', how='left')
    df = pd.merge(df, df_partnership[['company_id', 'allotted_time']], 
                  left_on='id', right_on='company_id', how='left')
    

    # --- 3. 検索フィルタリング ---
    if search_query:
        df = df[
            df['name'].str.contains(search_query, na=False) | 
            df['features'].str.contains(search_query, na=False)
        ]

    # --- 4. 表示用の整理 ---
    display_df = df[['id', 'name', 'allotted_time', 'manager', 'mail', 
                     'address', 'tel', 'features', 'logo', 'updated_at']].copy()
    
    event = st.dataframe(
        display_df,
        column_config={
            "id": st.column_config.TextColumn("ID", width="small"),
            "name": st.column_config.TextColumn("会社名", width="medium"),
            "allotted_time": st.column_config.NumberColumn("割り当て時間 (h)", width="small"),
            "manager": st.column_config.TextColumn("担当者名", width="medium"),
            "updated_at": "更新日"
        },
        width="stretch",
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row",
        key="main_search_df"
    )

    # --- 5. 詳細表示セクション (ロボット & PLC) ---
    if len(event.selection.rows) > 0:
        selected_row_index = event.selection.rows[0]
        selected_row = display_df.iloc[selected_row_index]
        selected_company_id = int(selected_row["id"])
        selected_company_name = selected_row["name"]
        
        st.markdown(f"---")
        st.subheader(f"🏢 {selected_company_name} の詳細情報")

        # 4つのカラムに分割
        col_1, col_2, col_3, col_4 = st.columns(4)

        # --- カラム1：ロボットメーカー ---
        with col_1:
            st.markdown("#### 🤖 取扱いロボット")
            target_rel_robot = df_relation_robot[df_relation_robot['company_id'] == selected_company_id]
            if not target_rel_robot.empty:
                related_robots = pd.merge(target_rel_robot, df_robot, left_on='robot_id', right_on='id', how='inner')
                for _, row in related_robots.iterrows():
                    st.info(f"**{row['name']}**")
            else:
                st.write("未登録")

        # --- カラム2：PLCメーカー ---
        with col_2:
            st.markdown("#### 🔌 取扱いPLC")
            target_rel_plc = df_relation_plc[df_relation_plc['company_id'] == selected_company_id]
            if not target_rel_plc.empty:
                related_plcs = pd.merge(target_rel_plc, df_plc, left_on='plc_id', right_on='id', how='inner')
                for _, row in related_plcs.iterrows():
                    st.success(f"**{row['name']}**")
            else:
                st.write("未登録")

        # --- カラム3:2Dカメラメーカー ---
        with col_3:
            st.markdown("#### 📷 取扱い2Dカメラ")
            target_rel_camera = df_relation_camera[df_relation_camera['company_id'] == selected_company_id]
            if not target_rel_camera.empty:
                related_cameras = pd.merge(target_rel_camera, df_camera, left_on='camera2D_id', right_on='id', how='inner')
                for _, row in related_cameras.iterrows():
                    st.warning(f"**{row['name']}**")
            else:
                st.write("未登録")
    else:
        st.caption("☝️ 表の行をクリックすると、詳細な取扱いメーカーが表示されます。")