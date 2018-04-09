# -*- coding: UTF-8 -*-
import sys
import os
import math

# 使い方
if len(sys.argv) == 1:
    print("")
    print("Fran.exe や LidarGen5.exe で保存した LiDAR の距離データ(csv ファイル）を読み込んで、")
    print("時間方向のメディアンを取る。結果を入力と同じフォーマットで出力。")
    print("")
    print("[Usage] %s depth.csv [Options]" % sys.argv[0])
    print("")
    print("Options:")
    print("-start_frame (int): 開始フレームの指定。0 始まりのフレーム番号を指定。")
    print("-num_frames (int): 平均化するフレーム数の指定。")
    print("")
    exit(0)

# -------------------------------------------------------------------------------------
# 定数
# -------------------------------------------------------------------------------------

# 水平方向解像度
NUM_ROWS = 32

# 垂直方向解像度
NUM_COLS = 141

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

# 入力ファイル名
input_file_name = sys.argv[1]

# フレーム範囲指定
i = []
start_frame = 0
if foundOpt(sys.argv, "-start_frame", i):
    start_frame = int(sys.argv[i[0] + 1])
num_frames = 0
if foundOpt(sys.argv, "-num_frames", i):
    num_frames = int(sys.argv[i[0] + 1])

# 平均処理のための足し込みバッファ
# buf = [0.0]*NUM_COLS * NUM_ROWS
# 全データを一時保持しておくためのバッファ
buf = []
for i in range(NUM_COLS * NUM_ROWS):
    buf.append([])

# フレーム番号カウンター
frame_count = 0

# 処理フレーム数カウンタ
proc_frame_count = 0

# ヘッダー部を保持しておくバッファ
headers = []

# ヘッダー部を保持しておくためのフラグ
init = True

# 入力ファイルを１行ずつ読み込む
for line in open(input_file_name):
    
    # カンマで列分割
    la = line.split(',')

    # 列数が所定の数だったら
    if len(la) == NUM_COLS * NUM_ROWS + 1:

        # 最初の該当行はタイトル行なのでスキップ
        if init:
            headers.append(line)
            init = False
            continue

        # フレームカウンタをインクリメント
        frame_count += 1

        # 指定されたフレーム範囲に入っているかチェック
        if frame_count <= start_frame:
            continue # 入っていなかったら次のフレームへ
        
        # 処理フレーム総数が指定された値を超えたかチェック
        if num_frames > 0 and proc_frame_count >= num_frames:
            break # 超えたら終了
        
        # 処理フレーム数をカウント
        proc_frame_count += 1

        # データをバッファにしまう
        for i in range(NUM_COLS * NUM_ROWS):
            buf[i].append(float(la[i + 1]))

        #print(frame_count, proc_frame_count, len(buf[0]))

    # そうでなければ
    else:

        # ヘッダー部として、最後に出力するように保持しておく
        headers.append(line)

# 各セルのメディアンを取る
buf2 = [ sorted(a)[len(a) / 2] for a in buf ]

# 出力
for line in headers:
    sys.stdout.write(line)
sys.stdout.write("0000.000")
for a in buf2:
    sys.stdout.write(", %d" % a)
sys.stdout.write("\n")

# EOP
exit(0)
