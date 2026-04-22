import streamlit as st
import pandas as pd
from database import get_data

def show_search_page():    
    st.header("🔍 検索")

    # --- 1. データの読み込み (Session State で API 節約) ---
    # 読み込むシートのリスト
    sheets = [
        "Company", "Manager", "Partnership", "Robot", 
        "Company_Robot_Relation", "Plc", "Company_Plc_Relation",
        "Camera2D", "Company_Camera2D_Relation",
        "Camera3D", "Company_Camera3D_Relation"
    ]

    # セッションにデータがなければ読み込む
    for sheet in sheets:
        state_key = f"df_{sheet.lower()}"
        if state_key not in st.session_state:
            try:
                # APIを叩いてデータを取得し、セッションに保存
                st.session_state[state_key] = get_data(sheet)
            except Exception as e:
                st.error(f"シート '{sheet}' の読み込みに失敗しました。名前を確認してください。")
                return

    # セッションからデータを取り出して変数に割り当て
    df_company = st.session_state.df_company
    df_manager = st.session_state.df_manager
    df_partnership = st.session_state.df_partnership
    df_robot = st.session_state.df_robot
    df_relation_robot = st.session_state.df_company_robot_relation
    df_plc = st.session_state.df_plc
    df_relation_plc = st.session_state.df_company_plc_relation
    df_camera = st.session_state.df_camera2d
    df_relation_camera = st.session_state.df_company_camera2d_relation
    df_camera3D = st.session_state.df_camera3d
    df_relation_camera3D = st.session_state.df_company_camera3d_relation

    # --- 2. 検索フィルタリング ---
    search_query = st.text_input("検索ワードを入力", key="search_input_main")

    if df_company.empty:
        st.info("データがありません。先に会社登録を行ってください。")
        return

    # テーブルの結合
    df = pd.merge(df_company, df_manager[['select_company', 'manager', 'mail']], 
                  left_on='name', right_on='select_company', how='left')
    df = pd.merge(df, df_partnership[['company_id', 'allotted_time']], 
                  left_on='id', right_on='company_id', how='left')

    if search_query:
        df = df[
            df['name'].str.contains(search_query, na=False) | 
            df['features'].str.contains(search_query, na=False)
        ]

    # --- 3. メインテーブルの表示 ---
    # memo を含めるのを忘れずに
    display_df = df[['id', 'name', 'duedate', 'allotted_time', 'manager', 'mail', 
                     'address', 'tel', 'features', 'logo', 'updated_at', 'memo']].copy()
    
    event = st.dataframe(
        display_df,
        column_config={
            "id": st.column_config.TextColumn("ID", width="small"),
            "name": st.column_config.TextColumn("会社名", width="medium"),
            "duedate": st.column_config.DateColumn("契約期限", width="small"),
            "allotted_time": st.column_config.NumberColumn("割り当て時間 (h)", width="small"),
            "manager": st.column_config.TextColumn("担当者名", width="medium"),
            "features": st.column_config.TextColumn("特徴（要望）", width="stretch"),
            "updated_at": "更新日"
        },
        width="stretch",
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row",
        key="main_search_df"
    )

    # --- 4. 詳細表示セクション ---
    if len(event.selection.rows) > 0:
        selected_row_index = event.selection.rows[0]
        selected_row = display_df.iloc[selected_row_index]
        selected_company_id = int(selected_row["id"])
        selected_company_name = selected_row["name"]
        
        st.markdown(f"---")
        st.subheader(f"🏢 {selected_company_name} の詳細情報")

        col_1, col_2, col_3, col_4 = st.columns(4)

        # カラム1：ロボット
        with col_1:
            st.markdown("#### 🤖 取扱いロボット")
            rel = df_relation_robot[df_relation_robot['company_id'] == selected_company_id]
            if not rel.empty:
                merged = pd.merge(rel, df_robot, left_on='robot_id', right_on='id', how='inner')
                for n in merged['name']: st.info(f"**{n}**")
            else: st.write("未登録")

        # カラム2：PLC
        with col_2:
            st.markdown("#### 🔌 取扱いPLC")
            rel = df_relation_plc[df_relation_plc['company_id'] == selected_company_id]
            if not rel.empty:
                merged = pd.merge(rel, df_plc, left_on='plc_id', right_on='id', how='inner')
                for n in merged['name']: st.success(f"**{n}**")
            else: st.write("未登録")

        # カラム3：2Dカメラ
        with col_3:
            st.markdown("#### 📷 取扱い2Dカメラ")
            rel = df_relation_camera[df_relation_camera['company_id'] == selected_company_id]
            if not rel.empty:
                merged = pd.merge(rel, df_camera, left_on='camera2D_id', right_on='id', how='inner')
                for n in merged['name']: st.warning(f"**{n}**")
            else: st.write("未登録")

        # カラム4：3Dカメラ
        with col_4:
            st.markdown("#### 📸 取扱い3Dカメラ")
            rel = df_relation_camera3D[df_relation_camera3D['company_id'] == selected_company_id]
            if not rel.empty:
                merged = pd.merge(rel, df_camera3D, left_on='camera3D_id', right_on='id', how='inner')
                for n in merged['name']: st.warning(f"**{n}**")
            else: st.write("未登録")

        # メモ表示
        st.markdown("---")
        st.markdown("#### 📝 備考・メモ")
        memo_content = selected_row.get("memo", "")
        if pd.notna(memo_content) and memo_content != "":
            st.write(memo_content)
        else:
            st.caption("登録されているメモはありません。")
    else:
        st.caption("☝️ 表の行をクリックすると、詳細な取扱いメーカーが表示されます。")