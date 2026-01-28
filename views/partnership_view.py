import streamlit as st
import pandas as pd
from database import get_data, save_data
from datetime import datetime

def show_partnership_page():
    st.header("👪 パートナーシップ情報登録")
    current_date = datetime.now().strftime("%Y-%m-%d")

    # --- 1. 各データの準備 (あらかじめ読み込んでおく) ---
    company_df = get_data("Company")
    partnership_df = get_data("Partnership")
    record_df = get_data("Partnership_Record")
    
    if company_df.empty:
        st.warning("先に「会社登録」タブから会社を登録してください。")
        return

    company_list = company_df['name'].tolist()

    # --- 2. 割り当て時間消化履歴表示 ---
    st.subheader("📚 割り当て時間消化履歴")
    if not record_df.empty:
        # SQLのJOINをPandasのmergeで再現
        merged_record = pd.merge(record_df, company_df[['id', 'name']], left_on='company_id', right_on='id', how='left')
        display_record = merged_record[['updated_at', 'name', 'Digestion_time', 'details']].copy()
        display_record.columns = ['記録日', '会社名', '消化時間', '内容']
        st.dataframe(display_record.sort_values('記録日', ascending=False), width="stretch", hide_index=True)
    else:
        st.write("履歴はまだありません。")

    # --- 3. グラフ表示 ---
    st.subheader("📊 割り当て時間残量グラフ")
    if not partnership_df.empty:
        merged_ps = pd.merge(partnership_df, company_df[['id', 'name']], left_on='company_id', right_on='id', how='left')
        st.bar_chart(data=merged_ps, x='name', y='allotted_time')

    # --- 4. 消化履歴登録 & Partnershipテーブルの更新 ---
    st.subheader("📝 割り当て時間消化履歴登録")
    with st.form("partnership_record_form", clear_on_submit=True):
        selected_company = st.selectbox("会社名", options=company_list, key="pr_company_select")
        digestion_time = st.number_input("消化時間 (h)", min_value=0.0, step=0.5, key="pr_digestion_input")
        details = st.text_area("内容", key="pr_details_input")
        submitted = st.form_submit_button("保存")

        if submitted:
            # 会社ID特定
            company_id = int(company_df[company_df['name'] == selected_company]['id'].values[0])
            
            # (A) Partnership_Record への新規追加
            new_record_id = int(record_df["id"].max() + 1) if not record_df.empty else 1
            new_record = pd.DataFrame([{
                "id": new_record_id,
                "company_id": company_id,
                "Digestion_time": digestion_time,
                "details": details,
                "updated_at": current_date
            }])
            updated_record_df = pd.concat([record_df, new_record], ignore_index=True)
            save_data("Partnership_Record", updated_record_df)
            st.cache_data.clear()

            # (B) Partnership テーブルの値を引き算して更新 (SQLのUPDATE相当)
            if not partnership_df.empty and (partnership_df['company_id'] == company_id).any():
                # 対象の行を特定して allotted_time を引く
                partnership_df.loc[partnership_df['company_id'] == company_id, 'allotted_time'] -= digestion_time
                partnership_df.loc[partnership_df['company_id'] == company_id, 'updated_at'] = current_date
                save_data("Partnership", partnership_df)
                st.cache_data.clear()

                st.success(f"{selected_company} の消化時間を登録し、残量を更新しました！")
                st.rerun()
            else:
                st.error("この会社にはまだ「割り当て時間」が設定されていません。下のフォームで登録してください。")

    # --- 5. 会社と割り当て時間新規登録 ---
    st.subheader("📝 会社と割り当て時間登録")
    with st.form("partnership_form", clear_on_submit=True):
        selected_company_ps = st.selectbox("会社名", options=company_list, key="ps_company_select")
        hour = st.number_input("割り当て時間 (h)", min_value=0.0, step=0.5, key="ps_hour_input")
        submitted_ps = st.form_submit_button("新規割り当て保存")

        if submitted_ps:
            company_id = int(company_df[company_df['name'] == selected_company_ps]['id'].values[0])
            new_ps_id = int(partnership_df["id"].max() + 1) if not partnership_df.empty else 1
            
            new_ps = pd.DataFrame([{
                "id": new_ps_id,
                "company_id": company_id,
                "allotted_time": hour,
                "updated_at": current_date
            }])
            
            updated_ps_df = pd.concat([partnership_df, new_ps], ignore_index=True)
            save_data("Partnership", updated_ps_df)
            st.cache_data.clear()
            
            st.success("割り当て時間を保存しました！")

            st.rerun()
