import os
import sys
import csv
import sqlite3
from collections import defaultdict

def create_station_master_table(conn):
    cursor = conn.cursor()
    
    # 駅マスターテーブルの作成
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS station_master (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_name TEXT NOT NULL,
            line_name TEXT NOT NULL,
            UNIQUE(station_name, line_name)
        )
    ''')
    
    conn.commit()

def process_csv_files_for_station_master(folder_path):
    station_master = []

    # CSVファイルを最新の年度から処理するためにソート
    csv_files = sorted(
        [f for f in os.listdir(folder_path) if f.startswith('reorganized_') and f.endswith('.csv')],
        key=lambda x: int(x[len('reorganized_'):len('reorganized_')+4]),
        reverse=True
    )
    
    for file_name in csv_files:
        csv_path = os.path.join(folder_path, file_name)
        
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            header = next(reader)  # ヘッダーをスキップ
            for row in reader:
                station_name, line_name = row[1], row[2]
                station_key = (station_name, line_name)
                
                # 駅マスターに追加（重複しない場合のみ）
                if station_key not in station_master:
                    station_master.append(station_key)
    
    return station_master

def insert_station_master_into_db(conn, station_master):
    cursor = conn.cursor()
    
    # 駅マスターテーブルにデータを挿入
    for station_name, line_name in station_master:
        cursor.execute('''
            INSERT OR IGNORE INTO station_master (station_name, line_name)
            VALUES (?, ?)
        ''', (station_name, line_name))
    
    conn.commit()

def create_ridership_table(conn):
    cursor = conn.cursor()

    # 乗車人数テーブルの作成
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ridership (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_id INTEGER NOT NULL,
            station_name TEXT NOT NULL,
            year_2023 INTEGER,
            year_2022 INTEGER,
            year_2021 INTEGER,
            year_2020 INTEGER,
            year_2019 INTEGER,
            UNIQUE(station_id),
            FOREIGN KEY(station_id) REFERENCES station_master(id)
        )
    ''')
    
    conn.commit()

def process_csv_files_for_ridership(folder_path, conn):
    cursor = conn.cursor()
    ridership_data = defaultdict(lambda: {'year_2023': None, 'year_2022': None, 'year_2021': None, 'year_2020': None, 'year_2019': None})

    # CSVファイルを最新の年度から処理するためにソート
    csv_files = sorted(
        [f for f in os.listdir(folder_path) if f.startswith('reorganized_') and f.endswith('.csv')],
        key=lambda x: int(x[len('reorganized_'):len('reorganized_')+4]),
        reverse=True
    )
    
    for file_name in csv_files:
        year = file_name[len('reorganized_'):len('reorganized_')+4]
        csv_path = os.path.join(folder_path, file_name)
        
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            header = next(reader)  # ヘッダーをスキップ
            for row in reader:
                station_name, line_name, passengers = row[1], row[2], row[3]  # 駅名、線名、乗車人数の列を正しく取得
                station_key = station_name  # 駅名をキーとする

                # 駅IDを取得（駅名だけで選択）
                cursor.execute('''
                    SELECT id FROM station_master WHERE station_name = ?
                ''', (station_name,))
                station_id = cursor.fetchone()[0]

                # 乗車人数データを更新
                ridership_data[station_key][f'year_{year}'] = int(passengers.replace(',', '')) if passengers else None

                # データを挿入または更新
                cursor.execute('''
                    INSERT INTO ridership (station_id, station_name, year_2023, year_2022, year_2021, year_2020, year_2019)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(station_id) DO UPDATE SET
                        year_2023 = COALESCE(EXCLUDED.year_2023, year_2023),
                        year_2022 = COALESCE(EXCLUDED.year_2022, year_2022),
                        year_2021 = COALESCE(EXCLUDED.year_2021, year_2021),
                        year_2020 = COALESCE(EXCLUDED.year_2020, year_2020),
                        year_2019 = COALESCE(EXCLUDED.year_2019, year_2019)
                ''', (station_id, station_name, ridership_data[station_key]['year_2023'], ridership_data[station_key]['year_2022'], ridership_data[station_key]['year_2021'], ridership_data[station_key]['year_2020'], ridership_data[station_key]['year_2019']))
    
    conn.commit()

def main(folder_path):
    # SQLiteデータベースの接続を確立
    conn = sqlite3.connect('train_data.db')
    
    # station_master テーブルの作成
    create_station_master_table(conn)
    
    # 最新の年度から順にCSVファイルを処理して駅マスターデータを作成
    station_master = process_csv_files_for_station_master(folder_path)
    
    # station_master テーブルにデータを挿入
    insert_station_master_into_db(conn, station_master)

    # ridership テーブルの作成
    create_ridership_table(conn)

    # 最新の年度から順にCSVファイルを処理して乗車人数データを挿入
    process_csv_files_for_ridership(folder_path, conn)
    
    conn.close()
    print("Station master and ridership data successfully inserted into the SQLite database.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python mainCsvToSqlite.py <folder_path>")
        sys.exit(1)

    folder_path = sys.argv[1]
    main(folder_path)
