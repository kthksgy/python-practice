# -*- coding:utf-8 -*-
import math
import numpy as np
import matplotlib.pyplot as plt

"""
JPEG圧縮に使われる離散コサイン変換(Discrete Cosine Transform)を実装してみた。
高速化はしていないので実用性は少ない。
"""

__author__ = "sugaok <github.com/sugaok>"
__status__ = "practice"
__version__ = "0.0.1"
__date__ = "August 11, 2019"


class DCT:
    def __init__(self, input_size, version=2):
        # Nはデータ長
        self.N = input_size
        # 基底ベクトルを作成
        self.T1D = np.array([
            [
                math.sqrt((1 if k == 0 else 2) / self.N) *
                math.cos(math.pi * (2 * x + 1) * k / (2 * self.N))
                for x in range(self.N)
            ] for k in range(self.N)
        ])

    def print(self):
        """ 既定ベクトルを表示 """
        print(self.T1D)
    
    def dct(self, data):
        """ 時間領域から周波数領域へ """
        return self.T1D.dot(data)
    
    def idct(self, data):
        """ 周波数領域から時間領域へ """
        return self.T1D.T.dot(data)

    def dct2(self, data):
        """
        二次元の場合は水平にDCTを行った結果を更に垂直にDCTする
        """
        return np.array([self.T1D.dot(d) for d in np.array([self.T1D.dot(d) for d in data]).T])

    def idct2(self, data):
        """
        戻す場合は垂直を戻した後水平を戻す
        """
        return np.array([self.T1D.T.dot(d) for d in np.array([self.T1D.T.dot(d) for d in data]).T])

if __name__ == "__main__":
    input_size = 8
    dct = DCT(input_size)

    for i in range(int(math.pow(input_size, 2))):
        plt.subplot(input_size, input_size, i + 1)
        data = np.zeros(int(math.pow(input_size, 2)))
        data[i] = 1
        data = dct.idct2(data.reshape((input_size, input_size)))
        plt.imshow(data, 'gray')
    plt.show()
