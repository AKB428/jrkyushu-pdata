import pdfplumber
import pandas as pd
import os
import sys

def extract_table_from_pdf(pdf_path, start_page, end_page):
    all_data = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for i in range(start_page - 1, end_page):
            page = pdf.pages[i]
            tables = page.extract_tables()

            for table in tables:
                # 正規化のために空白を除去したり、不要な行を削除
                table = [[cell.replace('\n', '').strip() if cell else '' for cell in row] for row in table]
                all_data.extend(table)
    
    # DataFrameとして読み込むが、ヘッダー行を指定しない
    df = pd.DataFrame(all_data)
    
    # 2行目を列名として設定し、それを削除する
    df.columns = df.iloc[1]
    df = df.drop(index=[0, 1])
    
    # 52行目を削除
    df = df.drop(index=52)
    
    # 50行ごとにデータを分割し、縦に並べ替える
    block_size = 50
    blocks = [df.iloc[i:i+block_size] for i in range(0, len(df), block_size)]
    df_reordered = pd.concat(blocks, axis=0, ignore_index=True)
    
    # output_csv フォルダがなければ作成
    output_folder = "output_csv"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # CSVファイルのパスを生成
    csv_output_path = os.path.join(output_folder, os.path.splitext(os.path.basename(pdf_path))[0] + '.csv')
    
    # CSVに出力
    df_reordered.to_csv(csv_output_path, index=False, encoding='utf-8-sig')
    print(f"Data successfully reorganized and saved to {csv_output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <pdf_path>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    
    # 例として1ページから2ページまでを処理する場合
    extract_table_from_pdf(pdf_path, start_page=1, end_page=2)
