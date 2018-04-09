# -*- coding: UTF-8 -*-
import sys
import os
import math
import numpy as np

# 使い方
if len(sys.argv) == 1:
    print("")
    print("PreScan の npz ファイルを読み込んで、Fran.exe と同じフォーマットの csv に変換")
    print("")
    print("[Usage] %s input.npz output.csv [Options]" % sys.argv[0])
    print("")
    print("Options:")
    print("-start_frame (int): 開始フレームの指定。0 始まりのフレーム番号を指定。")
    print("-num_frames (int): 処理フレーム数の指定。")
    print("")
    exit(0)

# -------------------------------------------------------------------------------------
# 定数
# -------------------------------------------------------------------------------------

# 水平方向解像度
#NUM_ROWS = 141
NUM_COLS = 140

# 垂直方向解像度
NUM_ROWS = 32

# -------------------------------------------------------------------------------------
# 関数
# -------------------------------------------------------------------------------------

# 指定した文字列が引数リストの中にあるかチェック
def foundOpt( argv, opt, idx = []):
    if opt in argv:
        if len(idx) > 0:
            idx[0] = argv.index(opt)
        else:
            idx.append(argv.index(opt))
        return True
    else:
        return False

# -------------------------------------------------------------------------------------
# main
# -------------------------------------------------------------------------------------

# 引数処理
input_npz = sys.argv[1]
output_csv = sys.argv[2]

# フレーム範囲指定
i = []
start_frame = 0
if foundOpt(sys.argv, "-start_frame", i):
    start_frame = int(sys.argv[i[0] + 1])
num_frames = 0
if foundOpt(sys.argv, "-num_frames", i):
    num_frames = int(sys.argv[i[0] + 1])

# npz 読み込み
a = None
try:
    a = np.load(input_npz)['arr_0']
except:
    print("ERROR: Failed to open, %s" % input_npz)
    exit(0)
    
# フレーム総数
if num_frames == 0:
    num_frames = (a.shape)[0]
    if num_frames <= 0:
        print("ERROR: num_frames <= 0 !!!")
        exit(0)

# 出力ファイルを開く
fout = open(output_csv, 'w')

# ヘッダー出力
header = 'time[s]'
for i in range(NUM_ROWS):
    for j in range(NUM_COLS + 1):
        header += ",(%d:%d)" % (j, i)
header += "\n"
fout.write(header)

# フレーム毎処理
for i in range(start_frame, start_frame + num_frames):
    # 出力文字列
    outStr = ""
    # 時間出力
    outStr += "%f" % i
    for j in range(NUM_ROWS):
        for k in range(NUM_COLS):
            # メートル to センチ
            d_cm = int(a[i][0][j][k] * 100 + 0.5)
            outStr += ", %d" % d_cm
        outStr += ", 0"
    outStr += "\n"
    # 書きこみ
    fout.write(outStr)
    # 画面表示
    sys.stdout.write("[" + str(i) + "]")
    sys.stdout.flush()

# 出力ファイルを閉じる
fout.close()

# 画面表示
sys.stdout.write("\n")
