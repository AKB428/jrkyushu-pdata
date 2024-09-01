import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# SQLiteデータベースに接続
conn = sqlite3.connect('train_data.db')

# Streamlitアプリの設定
st.title("JR九州乗客人数-可視化")

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
        column_to_plot = "乗客人数"
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
        column_to_plot = "増減人数"
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
        column_to_plot = "増減率"

    # データを数値型に変換してからソート
    df[column_to_plot] = pd.to_numeric(df[column_to_plot], errors='coerce')
    sorted_df = df.sort_values(by=column_to_plot, ascending=False)

    # 横棒グラフを描画（上位30位のみ表示、指定された列をプロット）
    st.subheader(f"{selected_tab} - {selected_year}")
    fig = px.bar(sorted_df.head(30), y="駅名", x=column_to_plot, orientation='h', 
                 labels={column_to_plot: column_to_plot, "駅名": "駅名"},
                 title=f"{selected_tab} - {selected_year}")

    # Y軸（駅名）を反転
    fig.update_layout(yaxis=dict(categoryorder='total ascending'))

    st.plotly_chart(fig)

    # 表を表示（すべてのレコードを表示、インデックス列を除外）
    df_reset = df.reset_index(drop=True)
    st.dataframe(df_reset)

# データベースの接続を閉じる
conn.close()
