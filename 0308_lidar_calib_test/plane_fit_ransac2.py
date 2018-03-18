# -*- coding: UTF-8 -*-

import sys
import numpy as np
import math

# 使い方
if len(sys.argv) == 1:
    print("")
    print("点群データをもらって、平面フィットする。")
    print("平面の方程式 ax + by + cz + d = 0 の a, b, c, d を出力")
    print("RANSAC で行う。")
    print("[Usage] %s 3d_points.txt out_coef.txt [Options]" % sys.argv[0])
    print("")
    print("[Options]")
    print("-ransac_num (int): RANSAC の回数")
    exit(0)

# 引数検索
def optFound( argv, opt, idx = []):
    if opt in argv:
        if len(idx) > 0:
            idx[0] = argv.index(opt)
        else:
            idx.append(argv.index(opt))
        return True
    else:
        return False

# 引数処理
inp_file = sys.argv[1]
out_file = sys.argv[2]
ransac_num = 10000
i = []
if optFound(sys.argv, "-ransac_num", i):
    ransac_num = int(sys.argv[i[0] + 1])

# 点群データをしまうバッファ
pts = []

# 点群データを読み込む
for line in open(inp_file):
    la = line.split()
    if len(la) == 3:
        pts.append(np.array([float(la[0]), float(la[1]), float(la[2])]))

# 評価関数：与えられた平面が点群にどれだけマッチするかを評価
# 評価値が小さいほど良い。
# 点群の各点と平面の距離の総和を返す。
# 法線ベクトル a, b, c は、長さ 1 になっているものとする。
def eval_coef( pts, a, b, c, d ):

    # 各点と平面の距離の総和
    dist_sum = 0.0

    # 点群の各点について
    for p in pts:

        # 点と平面の距離を計算、足し込む
        dist_sum += abs(a * p[0] + b * p[1] + c * p[2] + d)

    return dist_sum

# 最小評価値
min_eval = 1e+10

# 最小評価値の時の平面の方程式の係数
out_coef = [0, 0, 0, 0]

# RANSAC 開始
for i in range(ransac_num):

    # 点群の中からランダムに３点をピックアップする
    idx = np.random.choice(len(pts), 3, replace=False)
    p1 = pts[idx[0]]
    p2 = pts[idx[1]]
    p3 = pts[idx[2]]

    # ３点を通る平面の方程式
    ax = p1[0]
    ay = p1[1]
    az = p1[2]
    bx = p2[0]
    by = p2[1]
    bz = p2[2]
    cx = p3[0]
    cy = p3[1]
    cz = p3[2]
    a = (by - ay) * (cz - az) - (cy - ay) * (bz - az)
    b = (bz - az) * (cx - ax) - (cz - az) * (bx - ax)
    c = (bx - ax) * (cy - ay) - (cx - ax) * (by - ay)
    d = -( a * ax + b * ay + c * az )

    # 法線ベクトルを正規化
    vlen = math.sqrt(a * a + b * b + c * c)
    # 長さが小さいときは、このサンプルは無視
    if abs(vlen) < 1e-6:
        continue
    a /= vlen
    b /= vlen
    c /= vlen
    d /= vlen

    # z 方向の単位ベクトルは必ず正とする
    if c < 0:
        a *= -1
        b *= -1
        c *= -1
        d *= -1

    # 評価
    eval_val = eval_coef(pts, a, b, c, d)

    # 評価値とこれまでの最小値と比較
    if eval_val < min_eval:
        min_eval = eval_val
        out_coef[0] = a
        out_coef[1] = b
        out_coef[2] = c
        out_coef[3] = d
        print("%d, %f %f %f %f, %f" % (i, a, b, c, d, min_eval))
    #print("%d, %f %f %f %f, %f, %f" % (i, a, b, c, d, eval_val, min_eval))

# 出力
s = "%f %f %f %f %f" % (out_coef[0], out_coef[1], out_coef[2], out_coef[3], min_eval)
print(s)
fout = open(out_file, 'w')
fout.write(s + "\n")
fout.write("0 0 0 0 0\n")
fout.close()
