# 概要: 店舗名を入力すると、ID、拠点名、位置座標のリストをtsv形式で作成するスクリプト。YOLPを使用している。
# .envファイルに CLIENT_ID=YOLPのクライアントID を設定しておく。
# 使い方: python get_shop_geo.py <店舗名> <出力ディレクトリ>
# 結果のtsvは、"<出力ディレクトリ>/<店舗名>.tsv"という名前で生成される。


import sys
import os

import requests
from urllib.parse import quote
from pathlib import Path

from dotenv import load_dotenv
import pandas as pd

# シークレットの読み込み
load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")


record_num = 100

output_path = Path(sys.argv[2])
output_path.mkdir(parents=True, exist_ok=True)

# クエリのパーセントエンコーディング
query = sys.argv[1]
query_percent = quote(query)
url = f"https://map.yahooapis.jp/search/local/V1/localSearch?appid={CLIENT_ID}&query={query_percent}&output=json&results={record_num}"

# 1ページ目の取得
response = requests.get(url)
response_dict = response.json()

# ヒットした店舗のID、店舗名、位置座標をリストに格納
shop_list = []
for record in response_dict['Feature']:
    id = record["Id"]
    name = record["Name"]
    cord = record['Geometry']["Coordinates"]
    shop_list.append([id, name, cord])

# ページ数を取得し、残り何ページ取得する必要があるかを計算
total_num = int(response_dict["ResultInfo"]['Total'])
page_len = (total_num // record_num) + 1

# もしも2ページ目以降があれば1ページ目と同様の方法で取得し、リストに格納する
for page in range(1, page_len):
    start = page * record_num + 1
    url = f"https://map.yahooapis.jp/search/local/V1/localSearch?appid={CLIENT_ID}&query={query_percent}&output=json&results={record_num}&start={start}"
    response = requests.get(url)
    response_dict = response.json()

    for record in response_dict['Feature']:
        id = record["Id"]
        name = record["Name"]
        cord = record['Geometry']["Coordinates"]
        shop_list.append([id, name, cord])


# tsv形式で書き出し。ファイル名はクエリ名。
df = pd.DataFrame(shop_list, columns=["Id", "Name", "Coordinates"])
print(df)
csv_path = output_path / f"{query}.tsv"
df.to_csv(str(csv_path), sep='\t', index=False)
print(f"create {csv_path}")
