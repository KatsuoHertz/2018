# -*- coding: UTF-8 -*-

import sys
import numpy as np
import math

if len(sys.argv) < 4:
    print("")
    print("水平方位角（Θ）、仰角（φ）、距離（ρ）を与えて")
    print("３次元平面上の点群データを出力")
    print("")
    print("[Usage] %s theta phi rho [Options]" % sys.argv[0])
    print("")
    print("Options:")
    print("-num_cols (int): 点群の列数")
    print("-num_rows (int): 点群の行数")
    print("-grid_pitch (float): 点群のピッチ")
    print("-noise_sigma_xz (float): 面内（xz）方向のノイズの標準偏差（一様分布）")
    print("-noise_sigma_y (float): 距離（y）方向のノイズの標準偏差（一様分布）")
    print("-rotate (float) (float) (float) (float): 最初に加える原点周りの回転(v1 v2 v3 theta)")
    print("-translate (float) (float) (float): 最後に加える平行移動")
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

theta = float(sys.argv[1]) * math.pi / 180.0
phi = float(sys.argv[2]) * math.pi / 180.0
rho = float(sys.argv[3])

num_cols = 11
i = []
if optFound(sys.argv, "-num_cols", i):
    num_cols = int(sys.argv[i[0] + 1])

num_rows = 7
if optFound(sys.argv, "-num_rows", i):
    num_rows = int(sys.argv[i[0] + 1])

grid_pitch = 8
if optFound(sys.argv, "-grid_pitch", i):
    pt_step = float(sys.argv[i[0] + 1])

noise_sigma_xz = 0.5
if optFound(sys.argv, "-noise_sigma_xz", i):
    noise_sigma_xz = float(sys.argv[i[0] + 1])

noise_sigma_y = 1.0
if optFound(sys.argv, "-noise_sigma_y", i):
    noise_sigma_y = float(sys.argv[i[0] + 1])

q = np.array([0.0, 0.0, 0.0, 0.0])
if optFound(sys.argv, "-rotate", i):
    v1 = float(sys.argv[i[0] + 1])
    v2 = float(sys.argv[i[0] + 2])
    v3 = float(sys.argv[i[0] + 3])
    th = float(sys.argv[i[0] + 4]) * math.pi / 180.0
    r = math.sqrt(v1 * v1 + v2 * v2 + v3 * v3)
    v1 /= r
    v2 /= r
    v3 /= r
    s = math.sin(th / 2.0)
    c = math.cos(th / 2.0)
    q[0] = v1 * s
    q[1] = v2 * s
    q[2] = v3 * s
    q[3] = c

translate = np.array([0.0, 0.0, 0.0])
if optFound(sys.argv, "-translate", i):
    translate[0] = float(sys.argv[i[0] + 1])
    translate[1] = float(sys.argv[i[0] + 2])
    translate[2] = float(sys.argv[i[0] + 3])

# 点群の座標値をしまうリスト
pts_buf = []

# まず、原点を通る、xz 平面内に点群を作る
for i in range(num_rows):
    for j in range(num_cols):
        x = - (num_cols - 1) * grid_pitch / 2.0 + grid_pitch * j
        z = (num_rows - 1) * grid_pitch / 2.0 - grid_pitch * i
        y = 0.0
        # ノイズ付加
        x += noise_sigma_xz * (np.random.rand() - 0.5) * 2
        z += noise_sigma_xz * (np.random.rand() - 0.5) * 2
        y += noise_sigma_y * (np.random.rand() - 0.5) * 2
        pts_buf.append(np.array([x, y, z]))

# 原点周りの回転
x = q[0]
y = q[1]
z = q[2]
w = q[3]
qA = np.array([
    [1 - 2 * (y * y + z * z), 2 * ( x * y - z * w), 2 * ( z * x + y * w )],
    [2 * (x * y + z * w), 1 - 2 * (z * z + x * x),  2 * ( y * z - x * w )],
    [2 * (z * x - y * w),  2 * (y * z + x * w),  1 - 2 * ( x * x + y * y )]
])
for a in pts_buf:
    b = np.dot(qA, a)
    a[0] = b[0]
    a[1] = b[1]
    a[2] = b[2]

# y 方向に ρ 平行移動
for a in pts_buf:
    a[1] += rho

# φ 回転
c = math.cos(phi)
s = math.sin(phi)
for a in pts_buf:
    y = a[1]
    z = a[2]
    y2 =  c * y - s * z
    z2 =  s * y + c * z
    a[1] = y2
    a[2] = z2

# Θ 回転
c = math.cos(theta)
s = math.sin(theta)
for a in pts_buf:
    x = a[0]
    y = a[1]
    x2 =   c * x + s * y
    y2 = - s * x + c * y
    a[0] = x2
    a[1] = y2

# 平行移動
for a in pts_buf:
    a[0] += translate[0]
    a[1] += translate[1]
    a[2] += translate[2]

# 出力
for p in pts_buf:
    s = "%f %f %f" % (p[0], p[1], p[2])
    print(s)
