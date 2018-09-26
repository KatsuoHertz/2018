import argparse
import re
import math
import struct

desp = '''
テキストファイルに書かれた３次元点群のデータを pcd 形式のファイルにする。
テキストファイルには、
x1  y1  z1  r1  g1  b1   
x2  y2  z2  r2  g2  b2
・・・
という具合に空白文字区切りで３次元座標値と色を１行１点で書いておく。
x, y, z は、任意の実数値。
r, g, b は、[0,255] の 8bit の値。
'''
parser = argparse.ArgumentParser(description=desp)
parser.add_argument("input.txt", help='入力テキストファイル')
parser.add_argument("output.pcd", help='出力ファイル名')
args = parser.parse_args()

# 引数処理
in_fn = vars(args)['input.txt']
out_fn = vars(args)['output.pcd']

# 入力データをしまうバッファ
inp_dat = []

# 入力ファイルのオープン
for line in open(in_fn):

    # 空白文字でスプリット
    la = line.split()

    # スプリットした結果の要素数が所定の数だったら有効な行と見なす
    if len(la) == 6:
        x = float(la[0])
        y = float(la[1])
        z = float(la[2])
        r = int(la[3])
        g = int(la[4])
        b = int(la[5])
        inp_dat.append([x, y, z, r, g, b])
      
# 情報出力
print("Input data read: ", len(inp_dat))

# 出力ファイルのオープン（一旦テキストモードで開く）
out_pcd = open(vars(args)['output.pcd'],'w')

# PCD ファイルのヘッダーの書き込み
out_pcd.write("# .PCD v0.7 - Point Cloud Data file format\n")
out_pcd.write("VERSION 0.7\n")
out_pcd.write("FIELDS x y z rgb\n")
out_pcd.write("SIZE 4 4 4 4\n")
out_pcd.write("TYPE F F F F\n")
out_pcd.write("COUNT 1 1 1 1\n")
out_pcd.write("WIDTH %d\n" % len(inp_dat))
out_pcd.write("HEIGHT 1\n")
out_pcd.write("VIEWPOINT 0 0 0 1 0 0 0\n")
out_pcd.write("POINTS %d\n" % len(inp_dat))
out_pcd.write("DATA binary\n" )

# 出力ファイルを一旦閉じてバイナリモードで再オープン
out_pcd.close()
out_pcd = open(vars(args)['output.pcd'],'ab')

# 書き込み
for a in inp_dat:
    x, y, z, r, g, b = a[0], a[1], a[2], a[3], a[4], a[5]
    out_pcd.write(struct.pack('fffI', x, y, z, (r << 16) | (g << 8) | b))

# ファイルのクローズ
out_pcd.close()

# 情報表示
print("Output file: ", out_fn)