# -*- coding: UTF-8 -*-
import sys
import os
import math

# 使い方
if len(sys.argv) == 1:
    print("")
    print("Fran.exe や LidarGen5.exe で保存した LiDAR の距離データ(csv ファイル）")
    print("を読み込んで、x y z の 3 次元点群座標値を出力")
    print("水平方向が x 、垂直方向が z、奥行き方向が y")
    print("")
    print("[Usage] %s depth.csv [Options]" % sys.argv[0])
    print("")
    print("Options:")
    print("-frame frame_index: 指定したフレームのみ出力。0 始まりの番号")
    print("-out_dir dir_name: 出力フォルダの指定。無ければ作る。デフォルトは out")
    print("-xrange x_min x_max: x_min < x < x_max な点だけ出力")
    print("-yrange y_min y_max: 上と同様")
    print("-zrange z_min z_max: 上と同様")
    print("-start_frame (int): 処理開始フレームの指定")
    print("-end_frame (int): 処理終了フレームの指定（このフレームは含まず）")
    print("-col_range start end: 水平方向の指定した列だけ出力。0～141 で指定。end は含まず。")
    print("-row_range start end: 垂直方向の指定した行だけ出力。0～32 で指定。end は含まず。")
    print("")
    exit(0)

# -------------------------------------------------------------------------------------
# 設定
# -------------------------------------------------------------------------------------

# 全フレーム出力時の出力ディレクトリ
OUT_DIR = "out"

# 全フレーム出力時のファイル名書式
OUT_FILE = "%04d.txt"

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

# カンマ区切りの 1 行の距離データを三次元点群座標値に展開
#・3次元座標値のリストを返す
#・与えられた文字列が無効なフォーマットであれば空のリストを返す
def expandTo3d( 
    line_str, # カンマ区切りの 1 行の距離データ
    sensor_h_cols = 141, # センサーの水平画素数
    sensor_h_angle_start = -70.0, # センサーの一番左の列の方位角 [deg]
    sensor_h_angle_step = 1.0, # センサーの水平分解能 [deg]
    sensor_v_lines = ( # センサーのライン毎の垂直分解能
        1.2, 1.2, 1.2, 1.2, 1.2, 1.2, 
        0.6, 0.6, 
        0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 
        1.2, 1.2, 1.2, 1.2
    ), 
    sensor_v_angle_start = 9.4, # センサーの一番上のラインの仰角 [deg]
    big_dist_val = 16000, # 距離値の異常値：この値より大きな値は 0 にする
    x_range_min = None, # x 座標値がこの値より小さい点は出力しない
    x_range_max = None, # x 座標値がこの値より大きい点は出力しない
    y_range_min = None, # y 座標値がこの値より小さい点は出力しない
    y_range_max = None, # y 座標値がこの値より大きい点は出力しない
    z_range_min = None, # z 座標値がこの値より小さい点は出力しない
    z_range_max = None, # z 座標値がこの値より大きい点は出力しない
    col_range_min = 0, # この列より小さい列は出力しない。
    col_range_max = 141, # この列以上の列は出力しない。
    row_range_min = 0, # この行より小さい行は出力しない。
    row_range_max = 32, # この行以上の行は出力しない。
     ):

    # 返り値
    pointList = []

    # 水平画素数
    width = sensor_h_cols

    # 垂直画素数
    height = len(sensor_v_lines)

    # csv ファイルの列数
    num_cols = width * height + 1

    # カンマで列分割
    la = line_str.split(',')

    # 列数が所定の数だったら
    if len(la) == num_cols:

        # 垂直方位角 [deg]
        pitch_deg = 0.0

        # データ読み込み
        for i in range(height):
            for j in range(width):

                # 距離値
                try:
                    dist = float(la[i * width + j + 1]) # 最初の列は飛ばす
                except:
                    # 失敗したらそこで終了
                    return []

                # 異常値は 0 にする
                if dist > big_dist_val:
                   dist = 0

                # 水平方位角
                yaw_rad = (sensor_h_angle_start + sensor_h_angle_step * j) * math.pi / 180.0 

                # 垂直方位角 [rad]
                pitch_rad = (sensor_v_angle_start - pitch_deg) * math.pi / 180.0

                # z 座標値
                z = dist * math.sin(pitch_rad)

                # x 座標値
                x = dist * math.cos(pitch_rad) * math.sin(yaw_rad)

                # y 座標値
                y = dist * math.cos(pitch_rad) * math.cos(yaw_rad)

                # 範囲外チェック
                if (x_range_min != None and x < x_range_min) or \
                    (x_range_max != None and x > x_range_max) or \
                    (y_range_min != None and y < y_range_min) or \
                    (y_range_max != None and y > y_range_max) or \
                    (z_range_min != None and z < z_range_min) or \
                    (z_range_max != None and z > z_range_max):
                    continue

                # 範囲外チェック２
                if ( j < col_range_min or j >= col_range_max or i < row_range_min or i >= row_range_max ):
                    continue

                #リスト追加
                pointList.append([x, y, z])

            # 垂直方位角のインクリメント
            pitch_deg += sensor_v_lines[i]

    return pointList

# 点群データの出力
def writePointList( 
    point_list, # 3次元座標値のリスト
    stream = sys.stdout # 出力先
    ):
    for a in point_list:
        out_str = "%f %f %f \n" % (a[0], a[1], a[2])
        stream.write(out_str)

# -------------------------------------------------------------------------------------
# main
# -------------------------------------------------------------------------------------

# 入力ファイル名
input_file_name = sys.argv[1]

# フレーム番号指定
single_frame = False
frame_to_read = 0
i = []
if foundOpt(sys.argv, "-frame", i):
    single_frame = True
    frame_to_read = int(sys.argv[i[0] + 1])

# 出力ディレクトリ
out_dir = OUT_DIR
if foundOpt(sys.argv, "-out_dir", i):
    out_dir = sys.argv[i[0] + 1]

# ディレクトリ、無かったら作る
if not os.path.exists(out_dir):
    os.mkdir(out_dir)

# 範囲指定
x_min = None
x_max = None
if foundOpt(sys.argv, "-xrange", i):
    x_min = float(sys.argv[i[0] + 1])
    x_max = float(sys.argv[i[0] + 2])
y_min = None
y_max = None
if foundOpt(sys.argv, "-yrange", i):
    y_min = float(sys.argv[i[0] + 1])
    y_max = float(sys.argv[i[0] + 2])
z_min = None
z_max = None
if foundOpt(sys.argv, "-zrange", i):
    z_min = float(sys.argv[i[0] + 1])
    z_max = float(sys.argv[i[0] + 2])

# フレーム範囲指定
start_frame = 0
if foundOpt(sys.argv, "-start_frame", i):
    start_frame = int(sys.argv[i[0] + 1])
end_frame = 0
if foundOpt(sys.argv, "-end_frame", i):
    end_frame = int(sys.argv[i[0] + 1])

# 範囲指定２
col_start = 0
col_end = 141
if foundOpt(sys.argv, "-col_range", i):
    col_start = float(sys.argv[i[0] + 1])
    col_end = float(sys.argv[i[0] + 2])
row_start = 0
row_end = 32
if foundOpt(sys.argv, "-row_range", i):
    row_start = float(sys.argv[i[0] + 1])
    row_end = float(sys.argv[i[0] + 2])

# フレームカウンター
frame_count = 0

# 入力ファイルを１行ずつ読み込む
for line in open(input_file_name):
    
    # 3次元展開
    pointList = expandTo3d(line,
    x_range_min=x_min, x_range_max=x_max,
    y_range_min=y_min, y_range_max=y_max,
    z_range_min=z_min, z_range_max=z_max,
    col_range_min=col_start, col_range_max=col_end,
    row_range_min=row_start, row_range_max=row_end,
    )

    # 成功したら
    if len(pointList) > 0:

        # 単フレーム表示の場合
        if single_frame:
            
            # 所定のフレーム番号に達したら
            if frame_count == frame_to_read:

                # 画面に出力
                writePointList(pointList)

                # 終了
                break

        # 全フレーム出力の場合
        elif (end_frame == 0) or (start_frame <= frame_count < end_frame):

            # 出力ファイル名
            out_filename = OUT_FILE % frame_count

            # 出力ファイル名フルパス
            out_filepath = "%s/%s" % (out_dir, out_filename)

            # ファイルを開く
            try:
                outf = open(out_filepath, "w")
            except:
                print("ERROR: Failed to open the file, " + out_filepath)
                exit(-1)

            # 書き込み
            writePointList(pointList, outf)

            # ファイルを閉じる
            outf.close()

            # gnuplot 用出力
            print("splot '%s/%s' w p" % (out_dir, out_filename))
            print("pause -1")

        # フレーム数のカウント
        frame_count += 1

# EOP
exit(0)
