import os
import sys
import csv
import sqlite3

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
    station_master = set()
    
    for file_name in os.listdir(folder_path):
        if file_name.startswith('reorganized_') and file_name.endswith('.csv'):
            csv_path = os.path.join(folder_path, file_name)
            
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                header = next(reader)  # ヘッダーをスキップ
                for row in reader:
                    station_name, line_name = row[1], row[2]
                    station_master.add((station_name, line_name))
    
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

def main(folder_path):
    # SQLiteデータベースの接続を確立
    conn = sqlite3.connect('train_data.db')
    
    # station_master テーブルの作成
    create_station_master_table(conn)
    
    # CSVファイルから駅名と路線名を抽出してstation_masterテーブルを作成
    station_master = process_csv_files_for_station_master(folder_path)
    
    # station_master テーブルにデータを挿入
    insert_station_master_into_db(conn, station_master)
    
    conn.close()
    print("Station master data successfully inserted into the SQLite database.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python mainCsvToSqlite.py <folder_path>")
        sys.exit(1)

    folder_path = sys.argv[1]
    main(folder_path)
