import sys
import numpy as np
import math

if len(sys.argv) == 1:
    print("")
    print("点群データを回転＆平行移動する。")
    print("[R|T] をファイルで与える。3 x 4 行列、スペース区切り")
    print("")
    print("[Usage] %s pts.txt RT.txt [Options]" % sys.argv[0])
    print("")
    print("Options:")
    print("-noise_sigma (float): ノイズの標準偏差（一様分布）")
    print("")
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

pts_file = sys.argv[1]
rt_file = sys.argv[2]

noise_sigma = 0.0
i = []
if optFound(sys.argv, "-noise_sigma", i):
    noise_sigma = float(sys.argv[i[0] + 1])

# R
R = np.zeros((3, 3))

# T
T = np.zeros(3)

# 点群データをしまうバッファ
pts = []

# 点群データを読み込む
for line in open(pts_file):
    la = line.split()
    if len(la) == 3:
        pts.append(np.array([float(la[0]), float(la[1]), float(la[2])]))

# ファイルからRTを読み込み
idx = 0
for line in open(rt_file):
    la = line.split()
    if len(la) == 4:
        R[idx][0] = float(la[0])
        R[idx][1] = float(la[1])
        R[idx][2] = float(la[2])
        T[idx] = float(la[3])
        idx += 1
        if idx == 4:
            break

#print(R, T)

# 点群を変換
for p in pts:
    p2 = np.dot(R, p) + T
    # ノイズ付加
    if noise_sigma > 0:
        p2[0] += noise_sigma * (np.random.rand() - 0.5) * 2
        p2[1] += noise_sigma * (np.random.rand() - 0.5) * 2
        p2[2] += noise_sigma * (np.random.rand() - 0.5) * 2
    # 出力
    s = "%f %f %f" % (p2[0], p2[1], p2[2])
    print(s)
