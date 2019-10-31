import csv
import numpy as np
from sklearn import linear_model

if __name__ == '__main__':
    # 文字列と数値の変換用辞書
    EVALUATION = {'unacc': 0, 'acc': 1/3, 'good': 2/3, 'vgood': 1}
    PRICE = {'vhigh': 0, 'high': 0.1, 'med': 0.7, 'low': 1}
    MAINTENANCE_COST = {'vhigh': 0, 'high': 0.1, 'med': 0.9, 'low': 1}
    NUM_OF_DOORS = {'2': 0, '3': 0.7, '4': 0.9, '5more': 1}
    SEATING_CAPACITY = {'2': 0, '4': 0.8, 'more': 1,}
    SAFETY = {'high': 1, 'med': 0.6, 'low': 0}

    # データセットの読み込み
    with open('car.data') as f:
        reader = csv.reader(f)
        raw_data = [row for row in reader]

    # 文字列から数値への変換
    x_y = [
        [PRICE[row[0]], MAINTENANCE_COST[row[1]],
        NUM_OF_DOORS[row[2]], SEATING_CAPACITY[row[3]], SAFETY[row[5]],
        EVALUATION[row[6]]]
        for row in raw_data
    ]

    # 説明変数xと目的変数yに分離
    x_y = np.array(x_y)
    x = x_y[:, :5]
    y = x_y[:, -1:]
    # モデル1: ファジィ測度が1の場合
    model1 = linear_model.LinearRegression()
    model1.fit(x, y)
    print('[ファジィ測度1] 決定係数R^2', model1.score(x, y))
    print('偏回帰係数:', ', '.join(['{:.5f}'.format(k) for k in model1.coef_[0]]))
    print('切片:', model1.intercept_[0])
    t_norm = [ # t-ノルム, 二項演算はx*y
        [p[0]*p[1], p[0]*p[2], p[0]*p[3], p[0]*p[4],
         p[1]*p[2], p[1]*p[3], p[1]*p[4],
         p[2]*p[3], p[2]*p[4],
         p[3]*p[4]]
        for p in x
    ]
    # モデル2: ファジィ測度が2の場合
    x = np.hstack([x, t_norm])
    model2 = linear_model.LinearRegression()
    model2.fit(x, y)
    print('[ファジィ測度2] 決定係数R^2', model2.score(x, y))
    print('偏回帰係数:', ', '.join(['{:.5f}'.format(k) for k in model2.coef_[0]]))
    print('切片:', model2.intercept_[0])
    