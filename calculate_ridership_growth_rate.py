import sqlite3

def create_ridership_growth_rate_table(conn, years):
    cursor = conn.cursor()

    # 増減率を保存するテーブルを作成
    columns = ", ".join([f'growth_rate_{year} REAL' for year in years[:-1]])  # 最も古い年を除く
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS ridership_growth_rate (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_id INTEGER NOT NULL,
            station_name TEXT NOT NULL,
            {columns},
            FOREIGN KEY(station_id) REFERENCES station_master(id)
        )
    ''')
    
    conn.commit()

def calculate_and_insert_growth_rate(conn, years):
    cursor = conn.cursor()

    # すべての駅ごとに増減率を計算して挿入
    cursor.execute('SELECT id, station_name FROM station_master')
    stations = cursor.fetchall()
    
    for station_id, station_name in stations:
        growth_rates = {}
        for i in range(len(years) - 1):
            current_year = years[i]
            previous_year = years[i + 1]

            # 現在の年の増減数と前の年の乗車人数を取得
            cursor.execute(f'''
                SELECT r.year_{previous_year}, d.diff_{current_year}
                FROM ridership r
                JOIN ridership_difference d ON r.station_id = d.station_id
                WHERE r.station_id = ?
            ''', (station_id,))
            result = cursor.fetchone()

            if result and result[0] is not None and result[1] is not None:
                growth_rate = (result[1] / result[0]) * 100  # 増減率をパーセンテージで計算
                growth_rates[f'growth_rate_{current_year}'] = growth_rate
            else:
                growth_rates[f'growth_rate_{current_year}'] = None
        
        # 増減率を ridership_growth_rate テーブルに挿入
        if growth_rates:
            columns = ', '.join(growth_rates.keys())
            placeholders = ', '.join(['?'] * len(growth_rates))
            values = [growth_rates[key] for key in growth_rates]
            cursor.execute(f'''
                INSERT INTO ridership_growth_rate (station_id, station_name, {columns})
                VALUES (?, ?, {placeholders})
            ''', (station_id, station_name, *values))
    
    conn.commit()

def main():
    # SQLiteデータベースの接続を確立
    conn = sqlite3.connect('train_data.db')

    # ridership テーブルから年度を抽出
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(ridership)")
    columns = [info[1] for info in cursor.fetchall() if info[1].startswith('year_')]
    years = sorted([col.split('_')[1] for col in columns], reverse=True)  # 年度を降順にソート
    
    # ridership_growth_rate テーブルの作成
    create_ridership_growth_rate_table(conn, years)

    # 増減率を計算して ridership_growth_rate テーブルに挿入
    calculate_and_insert_growth_rate(conn, years)

    conn.close()
    print("Ridership growth rate data successfully inserted into the SQLite database.")

if __name__ == "__main__":
    main()
