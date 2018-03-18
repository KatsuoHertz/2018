# -*- coding: UTF-8 -*-

import sys
import numpy as np
import math

if len(sys.argv) == 1:
    print("")
    print("キャリブレーションアルゴリズムのテスト")
    print("")
    print("[Usage] %s sensor1.coef.plane1.txt sensor1.coef.plane2.txt sensor1.coef.plane3.txt sensor2.coef.plane1.txt sensor2.coef.plane2.txt sensor2.coef.plane3.txt [Options]" % sys.argv[0])
    print("")
    print("Options:")
    print("-sign_flip (0or1) (0or1) (0or1)")
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

# sensorB の読み込み係数の符号を反転する
sign_flip = [ False, False, False ]
i = []
if optFound(sys.argv, "-sign_flip", i):
    if int(sys.argv[i[0] + 1]) != 0:
        sign_flip[0] = True
    if int(sys.argv[i[0] + 2]) != 0:
        sign_flip[1] = True
    if int(sys.argv[i[0] + 3]) != 0:
        sign_flip[2] = True
    #print(sign_flip)

# 係数読み込み
a = []
for line in open(sys.argv[1]):
    la = line.split()
    if len(la) == 5:
        a.append(float(la[0]))
        a.append(float(la[1]))
        a.append(float(la[2]))
        a.append(float(la[3]))
        break
a11 = a[0]
a12 = a[1]
a13 = a[2]
a14 = a[3]
a = []
for line in open(sys.argv[2]):
    la = line.split()
    if len(la) == 5:
        a.append(float(la[0]))
        a.append(float(la[1]))
        a.append(float(la[2]))
        a.append(float(la[3]))
        break
a21 = a[0]
a22 = a[1]
a23 = a[2]
a24 = a[3]
a = []
for line in open(sys.argv[3]):
    la = line.split()
    if len(la) == 5:
        a.append(float(la[0]))
        a.append(float(la[1]))
        a.append(float(la[2]))
        a.append(float(la[3]))
        break
a31 = a[0]
a32 = a[1]
a33 = a[2]
a34 = a[3]

a = []
for line in open(sys.argv[4]):
    la = line.split()
    if len(la) == 5:
        a.append(float(la[0]))
        a.append(float(la[1]))
        a.append(float(la[2]))
        a.append(float(la[3]))
        break
b11 = a[0]
b12 = a[1]
b13 = a[2]
b14 = a[3]
a = []
for line in open(sys.argv[5]):
    la = line.split()
    if len(la) == 5:
        a.append(float(la[0]))
        a.append(float(la[1]))
        a.append(float(la[2]))
        a.append(float(la[3]))
        break
b21 = a[0]
b22 = a[1]
b23 = a[2]
b24 = a[3]
a = []
for line in open(sys.argv[6]):
    la = line.split()
    if len(la) == 5:
        a.append(float(la[0]))
        a.append(float(la[1]))
        a.append(float(la[2]))
        a.append(float(la[3]))
        break
b31 = a[0]
b32 = a[1]
b33 = a[2]
b34 = a[3]

# sensorBの符号反転
if sign_flip[0]:
    b11 *= -1
    b12 *= -1
    b13 *= -1
    b14 *= -1
if sign_flip[1]:
    b21 *= -1
    b22 *= -1
    b23 *= -1
    b24 *= -1
if sign_flip[2]:
    b31 *= -1
    b32 *= -1
    b33 *= -1
    b34 *= -1

# 方程式
A = np.array([
    [ a11, a12, a13,   0,   0,   0,   0,   0,   0,   0,   0,   0],
    [   0,   0,   0, a11, a12, a13,   0,   0,   0,   0,   0,   0],
    [   0,   0,   0,   0,   0,   0, a11, a12, a13,   0,   0,   0],
    [   0,   0,   0,   0,   0,   0,   0,   0,   0, a11, a12, a13],
    [ a21, a22, a23,   0,   0,   0,   0,   0,   0,   0,   0,   0],
    [   0,   0,   0, a21, a22, a23,   0,   0,   0,   0,   0,   0],
    [   0,   0,   0,   0,   0,   0, a21, a22, a23,   0,   0,   0],
    [   0,   0,   0,   0,   0,   0,   0,   0,   0, a21, a22, a23],
    [ a31, a32, a33,   0,   0,   0,   0,   0,   0,   0,   0,   0],
    [   0,   0,   0, a31, a32, a33,   0,   0,   0,   0,   0,   0],
    [   0,   0,   0,   0,   0,   0, a31, a32, a33,   0,   0,   0],
    [   0,   0,   0,   0,   0,   0,   0,   0,   0, a31, a32, a33]
])
B = np.array([
    b11, b12, b13, b14 - a14, b21, b22, b23, b24 - a24, b31, b32, b33, b34 - a34
])

#print(A)
#print(B)

# A の逆行列
#print(np.linalg.inv(A))

# A X = B を解く
X = np.dot(np.linalg.inv(A), B)

# 求まった R, T
R2 = np.array([
    [X[0], X[3], X[6]],
    [X[1], X[4], X[7]],
    [X[2], X[5], X[8]]
])
T2 = np.array([X[9], X[10], X[11]])

# 表示
#print(R2)
#print(T2)
print( "%f %f %f %f" % (R2[0][0], R2[0][1], R2[0][2], T2[0]) )
print( "%f %f %f %f" % (R2[1][0], R2[1][1], R2[1][2], T2[1]) )
print( "%f %f %f %f" % (R2[2][0], R2[2][1], R2[2][2], T2[2]) )

