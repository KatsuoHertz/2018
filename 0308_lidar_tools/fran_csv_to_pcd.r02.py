import argparse
import re
import math
import struct

desp = '''
Fran.exe で計測した Gen.5 LiDAR の depth.csv と intensity.csv を読み込んで、
pcd 形式のファイルに出力する。
r02: z と y を入れ替え（ y が高さ、z が奥行）
'''
parser = argparse.ArgumentParser(description=desp)
parser.add_argument("input_depth.csv", help='Fran から出力された 距離データファイル')
parser.add_argument("input_intensity.csv", help='Fran から出力された 強度データファイル')
parser.add_argument("output.pcd", help='出力ファイル名')
parser.add_argument("-f", "--frame", type=int, default=0, help='読み込むフレームの指定。0 始まり。（default: 0）')
parser.add_argument("-c", "--color", default='intensity', choices=['intensity', 'depth'], help='色付け規範（default: intensity）')
args = parser.parse_args()

# 8 bit の値を受け取って疑似カラーの r, g, b 値を返す
def get_pseudo_col(val8b):
    r, g, b = 0, 0, 0
    if val8b < 64:
        r = 0
        g = int(val8b / 64.0 * 255.0 + 0.5)
        b = 255
    elif val8b < 128:
        r = 0
        g = 255
        b = int((128 - val8b) / 64.0 * 255.0 + 0.5)
    elif val8b < 192:
        r = int((val8b - 128) / 64.0 * 255.0 + 0.5)
        g = 255
        b = 0
    else:
        r = 255
        g = int((255 - val8b) / 64.0 * 255.0 + 0.5)
        b = 0        
    r = 0 if r < 0 else r
    r = 255 if r > 255 else r
    g = 0 if g < 0 else g
    g = 255 if g > 255 else g
    b = 0 if b < 0 else b
    b = 255 if b > 255 else b
    return r, g, b

# 距離値のヒストグラム上位 (100 - m) % と下位 m % の値を求める
def get_val_range( dat, m ):
    val_min = 0
    val_max = 999999
    a = sorted(dat)
    b = sum(a)
    c = 0.0
    for d in a:
        c += d
        val_min = d
        if c / b * 100 > m:
            break
    for d in a:
        c += d
        val_max = d
        if c / b * 100 > (100 - m):
            break
    return val_min, val_max

# センサの水平画素数
SENSOR_WIDTH = 141

# センサの垂直画素数
SENSOR_HEIGHT = 32

# 距離値の最大値：これより大きい距離値は、不正の値とみなす。0 にする。
MAX_DEPTH_VAL = 16000

# センサの垂直分解能 [deg]
SENSOR_V_ANGLE_STEP = (
    1.2, 1.2, 1.2, 1.2, 1.2, 1.2, 
    0.6, 0.6, 
    0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 
    1.2, 1.2, 1.2, 1.2
)

# センサの水平開始角度 [deg]
SENSOR_H_START = 70.0

# センサの垂直開始角度 [deg]
SENSOR_V_START = 8.8

# 距離ファイルのオープン
dep_csv = open(vars(args)['input_depth.csv'])

# 強度ファイルのオープン
int_csv = open(vars(args)['input_intensity.csv'])

# 出力ファイルのオープン（一旦テキストモードで開く）
out_pcd = open(vars(args)['output.pcd'],'w')

# PCD ファイルのヘッダーの書き込み
out_pcd.write("# .PCD v0.7 - Point Cloud Data file format\n")
out_pcd.write("VERSION 0.7\n")
out_pcd.write("FIELDS x y z rgb\n")
out_pcd.write("SIZE 4 4 4 4\n")
out_pcd.write("TYPE F F F F\n")
out_pcd.write("COUNT 1 1 1 1\n")
out_pcd.write("WIDTH %d\n" % (SENSOR_WIDTH * SENSOR_HEIGHT) )
out_pcd.write("HEIGHT 1\n")
out_pcd.write("VIEWPOINT 0 0 0 1 0 0 0\n")
out_pcd.write("POINTS %d\n" % (SENSOR_WIDTH * SENSOR_HEIGHT) )
out_pcd.write("DATA binary\n" )

# 出力ファイルを一旦閉じてバイナリモードで再オープン
out_pcd.close()
out_pcd = open(vars(args)['output.pcd'],'ab')

# 読み込むフレームカウント
frame_count = 0

# １行ずつ読み込む
while True:

    # 読み込み
    dep_line = dep_csv.readline()
    int_line = int_csv.readline()

    # EOF に達したら終了
    if not dep_line or not int_line:
        break

    # カンマで分割
    dep_dat = dep_line.split(',')
    int_dat = int_line.split(',')

    # 最初のヘッダーは無視
    if re.match(r'\d+\.\d+',dep_dat[0]) == None: # １列目が小数点を含む数値表記かどうかで判別
        continue

    # データのチェック
    if len(dep_dat) != len(int_dat):
        print("Invalid data: len(dep_dat) != len(int_dat) ...")
        exit(-1)
    if len(dep_dat) != SENSOR_WIDTH * SENSOR_HEIGHT + 1:
        print("Invalid data: len(dep_dat) != SENSOR_WIDTH * SENSOR_HEIGHT + 1 ...")
        exit(-1)

    # フレームカウントのインクリメント
    frame_count += 1

    # 指定フレーム未満であれば次のフレームへ
    if frame_count < args.frame + 1:
        continue

    # 垂直方位角
    pitch_deg = 0

    # 色付け用に値の範囲を事前に計算
    tmp_dat = None
    if args.color == 'depth':
        tmp_dat = [ float(x) for x in dep_dat[1:]]
    else:
        tmp_dat = [ float(x) for x in int_dat[1:]]
    val_min, val_max = get_val_range(tmp_dat, 2 )

    # 各点ごとに処理
    for i in range(SENSOR_HEIGHT):
        for j in range(SENSOR_WIDTH):
            
            # 距離値
            dep_val = float(dep_dat[i * SENSOR_WIDTH + j + 1])

            # 強度値
            int_val = float(int_dat[i * SENSOR_WIDTH + j + 1])

            # 距離値の異常値はゼロにする
            if dep_val > MAX_DEPTH_VAL:
                dep_val = 0

            # 水平方位角
            yaw_rad = (SENSOR_H_START + j) * math.pi / 180.0
            
            # 垂直方位角
            pitch_rad = (SENSOR_V_START - pitch_deg) * math.pi / 180.0

            # y 座標値
            y = dep_val * math.sin(pitch_rad)

            # x 座標値
            x = dep_val * math.cos(pitch_rad) * math.sin(yaw_rad)

            # z 座標値
            z = dep_val * math.cos(pitch_rad) * math.cos(yaw_rad)

            # カラー
            val = dep_val if args.color == 'depth' else int_val
            n_val = (val - val_min) / (val_max - val_min)
            n_val = 0 if n_val < 0 else n_val
            n_val = 1 if n_val > 1 else n_val
            val2 = (int)(n_val * 255 + 0.5)
            r, g, b = get_pseudo_col(val2)

            # 書き込み
            out_pcd.write(struct.pack('fffI', x, y, z, (r << 16) | (g << 8) | b))

        # 垂直方位角のインクリメント
        pitch_deg += SENSOR_V_ANGLE_STEP[i]

    # ループを抜ける
    break
    
# ファイルのクローズ
dep_csv.close()
int_csv.close()
out_pcd.close()
