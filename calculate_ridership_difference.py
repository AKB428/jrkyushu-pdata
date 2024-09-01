import sqlite3

def create_ridership_difference_table(conn, years):
    cursor = conn.cursor()

    # 差分を保存するテーブルを作成
    columns = ", ".join([f'diff_{year} INTEGER' for year in years[:-1]])  # 最も古い年を除く
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS ridership_difference (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_id INTEGER NOT NULL,
            station_name TEXT NOT NULL,
            {columns},
            FOREIGN KEY(station_id) REFERENCES station_master(id)
        )
    ''')
    
    conn.commit()

def calculate_and_insert_difference(conn, years):
    cursor = conn.cursor()
    
    # すべての駅ごとに差分を計算して挿入
    cursor.execute('SELECT id, station_name FROM station_master')
    stations = cursor.fetchall()
    
    for station_id, station_name in stations:
        differences = {}
        for i in range(len(years) - 1):
            current_year = years[i]
            previous_year = years[i + 1]

            # 現在の年と前の年の乗車人数を取得
            cursor.execute(f'''
                SELECT year_{current_year}, year_{previous_year}
                FROM ridership
                WHERE station_id = ?
            ''', (station_id,))
            result = cursor.fetchone()

            if result and result[0] is not None and result[1] is not None:
                differences[f'diff_{current_year}'] = result[0] - result[1]
            else:
                differences[f'diff_{current_year}'] = None
        
        # 差分を ridership_difference テーブルに挿入
        if differences:
            columns = ', '.join(differences.keys())
            placeholders = ', '.join(['?'] * len(differences))
            values = [differences[key] for key in differences]
            cursor.execute(f'''
                INSERT INTO ridership_difference (station_id, station_name, {columns})
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
    
    # ridership_difference テーブルの作成
    create_ridership_difference_table(conn, years)

    # 差分を計算して ridership_difference テーブルに挿入
    calculate_and_insert_difference(conn, years)

    conn.close()
    print("Ridership difference data successfully inserted into the SQLite database.")

if __name__ == "__main__":
    main()
