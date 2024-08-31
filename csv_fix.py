import os
import sys
import csv

def reorganize_csv(file_path):
    data = []

    # ファイルを読み込み
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        lines = list(reader)

    # ヘッダー行を取得
    header = lines[0][:4]  # A~D列のヘッダーのみを保持

    # 特定の空白文字を削除する関数
    def remove_whitespace(s):
        return ''.join(c for c in s if not c.isspace())
    
    # 指定された範囲をメモリに格納
    def add_data(start, end, cols):
        for i in range(start, end):
            if i < len(lines):
                row = [lines[i][j] for j in cols if j < len(lines[i])]
                # B列とC列のすべてのスペース（全ての空白文字）を削除
                row[1] = remove_whitespace(row[1])  # 駅名のすべての空白文字を削除
                row[2] = remove_whitespace(row[2])  # 線名のすべての空白文字を削除
                data.append(row[:4])  # A~D列のみを保持

    # A~D, F~I, K~N列のデータを指定の範囲で読み込む
    add_data(1, 52, [0, 1, 2, 3])  # 1行目から51行目のA~D列
    add_data(1, 52, [5, 6, 7, 8])  # 1行目から51行目のF~I列
    add_data(1, 52, [10, 11, 12, 13])  # 1行目から51行目のK~N列
    add_data(52, 103, [0, 1, 2, 3])  # 52行目から102行目のA~D列
    add_data(52, 103, [5, 6, 7, 8])  # 52行目から102行目のF~I列
    add_data(52, 103, [10, 11, 12, 13])  # 52行目から102行目のK~N列

    # 「順位」という値を持つ行を削除する
    data = [row for row in data if row[0] != "順位"]

    # output_csv フォルダがなければ作成
    output_folder = "output_csv"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 新しいCSVファイルのパスを生成
    new_csv_path = os.path.join(output_folder, "reorganized_" + os.path.basename(file_path))

    # メモリに格納したデータを新しいCSVに出力
    with open(new_csv_path, 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(data)

    print(f"Data successfully reorganized and saved to {new_csv_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <csv_path>")
        sys.exit(1)

    csv_path = sys.argv[1]
    reorganize_csv(csv_path)
