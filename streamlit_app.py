import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt

# SQLiteデータベースに接続
conn = sqlite3.connect('train_data.db')

# Streamlitアプリの設定
st.title("JR乗客人数データ可視化")

# タブの選択肢
tabs = ["乗客人数", "増減人数", "増減率"]
selected_tab = st.selectbox("種類を選択", tabs)

# 年の選択肢をメモリに保持
years_mapping = {
    "乗客人数": [str(year) for year in range(2023, 2018, -1)],  # 2019年まで表示
    "増減人数": [str(year) for year in range(2023, 2019, -1)],  # 2020年まで表示
    "増減率": [str(year) for year in range(2023, 2019, -1)],  # 2020年まで表示
}
available_years = years_mapping[selected_tab]
selected_year = st.selectbox("年を選択", available_years)

# 決定ボタン
if st.button("決定"):
    # タブによって表示するデータを切り替え
    if selected_tab == "乗客人数":
        query = f'''
            SELECT rank() OVER (ORDER BY year_{selected_year} DESC) AS "順位",
                   station_name AS "駅名",
                   year_{selected_year} AS "乗客人数"
            FROM ridership
            ORDER BY year_{selected_year} DESC
        '''
        df = pd.read_sql_query(query, conn)
    elif selected_tab == "増減人数":
        previous_year = str(int(selected_year) - 1)
        query = f'''
            SELECT rank() OVER (ORDER BY diff_{selected_year} DESC) AS "順位",
                   r.station_name AS "駅名",
                   diff_{selected_year} AS "増減人数",
                   r.year_{selected_year} AS "元になった年の人数",
                   r.year_{previous_year} AS "元になった年から1年前の人数"
            FROM ridership r
            JOIN ridership_difference d ON r.station_id = d.station_id
            WHERE diff_{selected_year} IS NOT NULL
            ORDER BY diff_{selected_year} DESC
        '''
        df = pd.read_sql_query(query, conn)
    elif selected_tab == "増減率":
        previous_year = str(int(selected_year) - 1)
        query = f'''
            SELECT rank() OVER (ORDER BY growth_rate_{selected_year} DESC) AS "順位",
                   r.station_name AS "駅名",
                   growth_rate_{selected_year} AS "増減率",
                   d.diff_{selected_year} AS "元になった年の増加人数",
                   r.year_{previous_year} AS "元になった年から1年前の乗客人数"
            FROM ridership r
            JOIN ridership_growth_rate g ON r.station_id = g.station_id
            JOIN ridership_difference d ON r.station_id = d.station_id
            WHERE growth_rate_{selected_year} IS NOT NULL
            ORDER BY growth_rate_{selected_year} DESC
        '''
        df = pd.read_sql_query(query, conn)

    # グラフを描画（上位30位のみ表示）
    st.subheader(f"{selected_tab} - {selected_year}")
    st.bar_chart(df.set_index("駅名").head(30)[df.columns[-1]])

    # 表を表示（すべてのレコードを表示）
    st.dataframe(df)

# データベースの接続を閉じる
conn.close()
