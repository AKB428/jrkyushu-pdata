import sys
import os
from pdf2csv import extract_table_from_pdf
from csv_fix import reorganize_csv

def main(pdf_path):
    # PDFからCSVを作成
    extract_table_from_pdf(pdf_path, start_page=1, end_page=2)
    
    # 生成されたCSVファイル名を取得
    csv_file = os.path.splitext(os.path.basename(pdf_path))[0] + '.csv'
    csv_path = os.path.join("output_csv", csv_file)
    
    # CSVを整形
    reorganize_csv(csv_path)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python mainPdf2csv.py <pdf_path>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    main(pdf_path)
