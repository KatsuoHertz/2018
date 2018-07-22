import argparse
from open3d import *

desp = '''
pcd フォーマットの３次元点群ファイルビューア
'''
parser = argparse.ArgumentParser(description=desp)
parser.add_argument("input.pcd", help='pcd フォーマットの３次元点群ファイル')
args = parser.parse_args()

pcd = read_point_cloud(vars(args)["input.pcd"])
draw_geometries([pcd])


