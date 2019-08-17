# coding: utf-8

"""
到着パケットが複数のM/M/1/K待ち行列を迂回する場合のシミュレーションプログラム

迂回ルールは、最も滞在パケット数が少ない待ち行列に迂回する
待ち行列数を1とする事で単独の場合をシミュレーション可能
バッファサイズKを0以下とする事でM/M/1待ち行列としてシミュレーション可能
"""
__author__ = "sugaok <github.com/sugaok>"
__status__ = "completion"
__version__ = "1.0"
__date__    = "06 Aug. 2019"

import queue
import random
import math
import statistics
import matplotlib.pyplot as plt

if __name__ == '__main__':
    random.seed(19676018)       # 疑似乱数のシード値
    SERVICE_RATE = 100000       # サービス率
    SR_RCP = 1 / SERVICE_RATE   # サービス率の逆数(効率化のため)
    SAMPLE_LENGTH = 100000      # 標本区間長
    NUM_SAMPLES = 10            # 標本数

    num_queues = int(input("使用するM/M/1/K待ち行列の数を指定[個] -> "))

    k = int(input("個々のキューのバッファサイズKを指定(M/M/1ならば-1)[packets] -> "))

    # 回線利用率(Line Utilization Rate)の間隔(Interval)
    lur_itv = int(input("回線利用率の間隔を指定(1 ~ 100)[%] -> "))
    lur_itv = min(100, max(1, lur_itv))  # 範囲外の入力を排除
    
    results = [None for _ in range(int(100 / lur_itv) + 1)]
    
    for lur in range(0, 100, lur_itv):
        if lur < 1:
            lur = 1
        print("回線利用率%d%%のシミュレーションを開始..." % lur)
        ar_rcp = 1 / (SERVICE_RATE * (lur / 100))

        st_samples = []
        pl_samples = []
        for sidx in range(NUM_SAMPLES):
            # N個のM/M/1/K待ち行列
            # (キュー本体, 次回の退去時間)
            queues = [[[], 0] for _ in range(num_queues)]
            # 一番短いキューのインデックスを保持する
            shortest = 0
            next_arrival = 0  # 次の到着時刻
            st_temp = 0  # 総滞在時間
            l_temp = 0  # パケット廃棄数
            num_serviced = 0  # 退去済みパケット数

            while num_serviced < SAMPLE_LENGTH:
                # 到着処理を行うか
                do_arrival = True
                # 全ての待ち行列について退去処理判定を行う
                for i, q in enumerate(queues):
                    if q[0] and q[1] < next_arrival:
                        packet = q[0].pop(0)
                        st_temp += (q[1] - packet[0])
                        num_serviced += 1
                        if q[0]:
                            q[1] += q[0][0][1]
                        if len(q[0]) < len(queues[shortest][0]):
                            shortest = i
                        do_arrival = False  # 退去処理をした場合は到着処理はしない
                        break
                # どちらの待ち行列も退去しない場合に到着処理を行う
                if do_arrival:
                    # 長さが短い方の待ち行列に到着させる
                    # バッファサイズKを考慮する以外は課題1と同じ
                    a_t = next_arrival
                    d = -SR_RCP * math.log(1 - random.random()) * 1000000
                    packet = [a_t, d]
                    if not queues[shortest][0]:
                        queues[shortest][1] = next_arrival + d
                    # バッファサイズK未満ならばパケットを待ち行列に追加
                    if k < 1 or len(queues[shortest][0]) < k:
                        queues[shortest][0].append(packet)
                        for i, q in enumerate(queues):
                            if len(q[0]) < len(queues[shortest][0]):
                                shortest = i
                    else:
                        # 待ち行列に入りきらなかったので廃棄数を加算
                        l_temp += 1
                    a = -ar_rcp * math.log(1 - random.random()) * 1000000
                    next_arrival += a
            st_sample = st_temp / SAMPLE_LENGTH
            pl_sample = (l_temp / (SAMPLE_LENGTH + l_temp)) * 100
            st_samples.append(st_sample)
            pl_samples.append(pl_sample)
            print("回線利用率{}%[標本{}] - 平均滞在時間: {:.4f}[μs], パケット廃棄率{:.3f}%".format(lur, sidx, st_sample, pl_sample))
        # 信頼区間を算出する
        st_mean = statistics.mean(st_samples)
        st_variance = statistics.variance(st_samples)
        # 95%信頼区間なのでta=1.96
        st_95delta = 1.96 * math.sqrt(st_variance / NUM_SAMPLES)
        pl_mean = statistics.mean(pl_samples)
        results[int(lur / lur_itv)] = (lur, st_mean, st_95delta, pl_mean)
    # 結果の初期値(無効値)を削除
    results.remove(None)
    # 各回線利用率について結果を表示
    for r in results:
        print(" --- 回線利用率: {0}% --- ".format(r[0]))
        if k < 1 and num_queues == 1:
            print("平均滞在時間(理論値): {:.4f}[μs]".format(1000000 / (SERVICE_RATE * (1 - r[0] / 100))))
        print("平均滞在時間: {0:.4f}[μs], 95%信頼区間: {1:.4f} ~ {2:.4f}[μs], パケット廃棄率: {3:.3f}%".format(r[1], r[1] - r[2], r[1] + r[2], r[3]))
    # TeXの表として出力する
    if input("TeXの表形式を出力しますか(y/n) -> ").lower() == 'y':
        print("1. 回線利用率 | 平均滞在時間 | 95%信頼区間 | 平均滞在時間(理論値)")
        print("2. 回線利用率 | 平均滞在時間 | パケット廃棄率")
        tex_type = int(input("表示形式を選択してください -> "))
        if tex_type == 1:
            print("回線利用率[\\%] & 平均滞在時間$\\bar{w}(n)$[$\\mu s$] & 95\\%信頼区間[$\\mu s$] & 理論値$\\hat{w}$[$\\mu s$] \\\\")
            for r in results:
                print("{} & {:.4f} & {:.4f} $\\sim$ {:.4f} & {:.4f} \\\\".format(r[0], r[1], r[1] - r[2], r[1] + r[2], 1000000 / (SERVICE_RATE * (1 - r[0] / 100))))
        elif tex_type == 2:
            print("回線利用率[\\%] & 平均滞在時間$\\bar{w}(n)$[$\\mu s$] & パケット廃棄率[\\%] \\\\")
            for r in results:
                print("{} & {:.4f} & {:.3f} \\\\".format(r[0], r[1], r[3]))
    # グラフを出力する
    if input("グラフを出力しますか(y/n) -> ").lower() == 'y':
        # 図にそれぞれの回線利用率に関して平均滞在時間の理論値とシミュレーション値、95%信頼区間を出力
        plt.xlabel("Line Utilization Rate[%]")
        plt.ylabel("Average Stay Time[μs]")
        plt.grid()
        if num_queues == 1:
            # 式(38)から理論値[μs]を求める
            graph_x = [i for i in range(results[-1][0] + 1)]
            graph_y = [1000000 / (SERVICE_RATE * (1 - i / 100)) for i in range(results[-1][0] + 1)]
            plt.plot(graph_x, graph_y, color='blue', linestyle='dashed', alpha=0.5, linewidth=1)
        for r in results:
            plt.plot([r[0], r[0]], [r[1] - r[2], r[1] + r[2]], color='red')
            plt.plot(r[0], r[1], color='black', marker='_', markersize=3)
        plt.show()
