# JR九州 乗客数情報の分析

データ元

https://www.jrkyushu.co.jp/company/info/data/station.html

## 必要なライブラリ

```
pip install pdfplumber pandas
pip install streamlit pandas matplotlib sqlite3
```

## 準備

https://www.jrkyushu.co.jp/company/info/data/station.html

からPDFをダウンロード

./pass-data/　にダウンロードするものとする

## Step1 PDFからCSV

```
python3 mainPdf2csv.py ./pass-data/2023ekibetsu.pdf
python3 mainPdf2csv.py ./pass-data/2022ekibetsu.pdf
python3 mainPdf2csv.py ./pass-data/2021ekibetsu.pdf
python3 mainPdf2csv.py ./pass-data/2020ekibetsu.pdf
python3 mainPdf2csv.py ./pass-data/2019ekibetsu.pdf
```

## Step2 CSVからSQLite

```
python3 mainCsvToSqlite.py ./output_csv/
```

## Step3 差分テーブルの算出と登録

```
python3 calculate_ridership_difference.py
```

## Step4 増減率テーブルの算出と登録

```
python3 calculate_ridership_growth_rate.py
```