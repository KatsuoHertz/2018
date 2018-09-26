# -*- coding: shift_jis -*-
import numpy as np 
import cv2
import argparse

desp = '''
Prescan の npz 形式のデータのビューア。
次元が [フレーム, チャンネル, 縦, 横] の次元数が４なデータ。
次元数が３の場合は、[フレーム, 0, 縦, 横] と解釈して読む。
次元数が２の場合は、[0, 0, 縦, 横] と解釈して読む。
それ以外はエラー。
'''

# 疑似カラー生成
def pseudo_color(val8b):
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
    #return [r, g, b]
    return [b, g, r]

# 2 次元配列データを画像データ化。
def make_image( dat ):
    color_table = [
        [  0,   0, 255],
        [  0, 255,   0],
        [255,   0,   0],
        [255, 255,   0],
        [255,   0, 255],
        [  0, 255, 255],
        [  0,   0, 128],
        [  0, 128,   0],
        [128,   0,   0],
        [128, 128,   0],
        [128,   0, 128],
        [  0, 128, 128],
        [255, 128,   0],
        [128, 255,   0],
        [255,   0, 128],
        [128,   0, 255],
        [  0, 255, 128],
        [  0, 128, 255],
    ]
    img = np.zeros((dat.shape[0], dat.shape[1], 3), np.uint8)
    if dat.dtype == np.int32 or dat.dtype == np.int64:
        for y in range(dat.shape[0]):
            for x in range(dat.shape[1]):
                img[y,x] = color_table[(dat[y, x] - 1) % len(color_table)]
        img[dat == 0] = [0, 0, 0]
        #test
        img[dat == 9] = [0, 0, 0]
        img[dat == 10] = [0, 0, 0]
        #img[dat == 11] = [0, 0, 0]
        img[dat == 12] = [0, 0, 0]
        #test
    elif dat.dtype == np.float32 or dat.dtype == np.float64:
        max_val = dat.max()
        min_val = dat.min()
        if max_val == min_val:
            pass
        for y in range(dat.shape[0]):
            for x in range(dat.shape[1]):
                val = int((dat[y,x] - min_val) / float((max_val - min_val)) * 255 + 0.5)
                img[y,x] = pseudo_color(val)
    elif dat.dtype == np.uint8:
        pass
    else:
        print("ERROR: invalid dtype, ", dat.dtype)
        exit()
    return img

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = desp)
    parser.add_argument("input.npz", type=str, help="入力 npz ファイル")
    parser.add_argument("-z", "--zoom", type=int, default=4, help="拡大表示率。1 以上の整数で指定。default=4")
    args = parser.parse_args()

    # 引数処理
    zoom = int(args.zoom)

    # 入力ファイルをロード
    npz = np.load(vars(args)['input.npz'])['arr_0']
    print(npz.shape)

    # データを [フレーム, チャンネル, 縦, 横] に統一
    if len(npz.shape) == 4:
        pass
    elif len(npz.shape) == 3:        
        npz = npz[:, np.newaxis, :, :]
    elif len(npz.shape) == 2:
        npz = npz[np.newaxis, np.newaxis, :, :]
    else:
        print("ERROR: invalid data shape, ", npz.shape)
        exit()
    print(npz.shape)

    # １フレームずつ
    #for f in range(len(npz)):
    f = 0
    while(f < len(npz)):

        # チャネルごとに
        for c in range(len(npz[f])):
            
            # データ
            dat = npz[f][c]

            # 画像化
            img = make_image(dat)

            # 表示
            cv2.imshow("ch: {}".format(c), cv2.resize(img, dsize=(0,0), fx=zoom, fy=zoom, interpolation=cv2.INTER_NEAREST))
            cv2.waitKey(1) # これがないと連続でフレーム送りしたときに画像が更新されない
        
        # コンソール情報表示
        print("frame: {}".format(f))

        # キーボード入力まち
        cmd = cv2.waitKey(0)
        
        if cmd == ord('n'):
            f += 1
            if f >= len(npz):
                f -= len(npz) - 1
        elif cmd == ord('p'):
            f -= 1
            if f < 0:
                f = 0
        elif cmd == ord('N'):
            f += 10
            if f >= len(npz):
                f -= 10
        elif cmd == ord('P'):
            f -= 10
            if f < 0:
                f += 10
        elif cmd == ord('q') or cmd == 27 :
            break

    # 後処理
    cv2.destroyAllWindows()

