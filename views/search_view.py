import streamlit as st
import pandas as pd
from database import get_data

def show_search_page():    
    st.header("🔍 検索")
    search_query = st.text_input("検索ワードを入力", key="search_input_main")

    # --- 1. データの読み込み ---
    df_company = get_data("Company")
    df_manager = get_data("Manager")
    df_partnership = get_data("Partnership")
    df_robot = get_data("Robot")
    df_relation = get_data("Company_Robot_Relation")

    if df_company.empty:
        st.info("データがありません。先に会社登録を行ってください。")
        return

    # --- 2. テーブルの結合 (SQLのLEFT JOIN相当) ---
    # (1) Company と Manager を結合 (会社名で紐付け)
    # Managerは1社に複数いる可能性があるため、最新の1人のみを表示するか重複を許容するか選べますが、
    # ここではシンプルにそのままマージします。
    df = pd.merge(df_company, df_manager[['select_company', 'manager', 'mail']], 
                  left_on='name', right_on='select_company', how='left')

    # (2) さらに Partnership を結合 (会社IDで紐付け)
    df = pd.merge(df, df_partnership[['company_id', 'allotted_time']], 
                  left_on='id', right_on='company_id', how='left')

    # --- 3. 検索フィルタリング ---
    if search_query:
        # 会社名、または特徴にキーワードが含まれる行を抽出
        df = df[
            df['name'].str.contains(search_query, na=False) | 
            df['features'].str.contains(search_query, na=False)
        ]

    # --- 4. 表示用の整理 ---
    # SQLのAS句と同様に、カラム名を整える
    display_df = df[[
        'id', 'name', 'allotted_time', 'manager', 'mail', 
        'address', 'tel', 'features', 'logo', 'updated_at'
    ]].copy()
    
    # 日本語名への変換は st.dataframe の column_config で行います

    event = st.dataframe(
        display_df,
        column_config={
            "id": st.column_config.TextColumn("ID", width="small"),
            "name": st.column_config.TextColumn("会社名", width="medium"),
            "allotted_time": st.column_config.NumberColumn("割り当て時間 (h)", width="small"),
            "manager": st.column_config.TextColumn("担当者名", width="medium"),
            "mail": "メールアドレス",
            "address": "住所",
            "tel": "電話番号",
            "features": "特徴",
            "logo": "ロゴ使用許可",
            "updated_at": "更新日"
        },
        width="stretch",
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row",
        key="main_search_df" # keyを追加
    )

    # --- 5. 詳細表示セクション (ロボットメーカー) ---
    if len(event.selection.rows) > 0:
        selected_row_index = event.selection.rows[0]
        # フィルタリング後のdfから選択された行のデータを取得
        selected_row = display_df.iloc[selected_row_index]
        selected_company_id = int(selected_row["id"])
        selected_company_name = selected_row["name"]

        st.markdown(f"### 🤖 {selected_company_name} の取扱いロボットメーカー")

        # 関連テーブルからこの会社のロボットIDを抽出
        target_relations = df_relation[df_relation['company_id'] == selected_company_id]
        
        # ロボット名と結合して取得
        if not target_relations.empty:
            related_robots = pd.merge(target_relations, df_robot, left_on='robot_id', right_on='id', how='inner')
            
            if not related_robots.empty:
                cols = st.columns(len(related_robots))
                for i, (_, row) in enumerate(related_robots.iterrows()):
                    with cols[i]:
                        st.info(f"**{row['name_y']}**") # merge後のカラム名に注意(Robotシートのname)
            else:
                st.write("ロボットメーカーの詳細が見つかりません。")
        else:
            st.write("この会社のロボットメーカー情報はまだ登録されていません。")
    else:

        st.caption("☝️ 表の行をクリックすると、その会社の取扱いロボットメーカーが表示されます。")
