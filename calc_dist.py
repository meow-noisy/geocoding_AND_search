# 概要: 2店舗の位置座標リストを元に、各拠点同士の距離を計算し、距離がしきい値未満のペアを表示する。
# 使い方: python calc_dist.py <店舗名1> <店舗名2> <tsvのあるディレクトリ> [(任意)しきい値の距離(km)]

import sys
from pathlib import Path

import pandas as pd
from geopy.distance import geodesic

argvs = sys.argv


def _cord_converter(cord):
    # 軽度,緯度の文字列になっているので、(緯度,軽度)のfloatのタプルにする
    cord_list = cord.split(",")

    return (float(cord_list[1]), float(cord_list[0]))


s1 = argvs[1]
s2 = argvs[2]
output_path = Path(argvs[3])
if len(argvs) == 5:
    DIST_THRESHOLD = float(argvs[4])
else:
    DIST_THRESHOLD = 0.200

# 位置座標リストのtsvを読み込み。
df1 = pd.read_csv(str(output_path / f"{s1}.tsv"), sep='\t')
df2 = pd.read_csv(str(output_path / f"{s2}.tsv"), sep='\t')

# 各拠点同士の距離を計算し、距離がしきい値未満のペアを表示する。
result = []
key_list = []
for index1, df1_row in df1.iterrows():
    record1 = df1_row.values.tolist()
    cord1 = record1[2]
    cord1_tuple = _cord_converter(cord1)

    for index2, df2_row in df2.iterrows():
        record2 = df2_row.values.tolist()
        cord2 = record2[2]
        cord2_tuple = _cord_converter(cord2)
        dist = geodesic(cord1_tuple, cord2_tuple).km

        if float(dist) < DIST_THRESHOLD:
            # 無いとは思うが、一応重複排除
            if record1[0] not in key_list:
                key_list.append(record1[0])
                result.append([record1[1], record2[1], dist])

# 結果の表示
for r in result:
    print(r)


print(f"合計: {len(result)}")
