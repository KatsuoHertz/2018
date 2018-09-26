import argparse
from open3d import *

desp = '''
pcd フォーマットの３次元点群ファイルビューア
'''
parser = argparse.ArgumentParser(description=desp)
parser.add_argument("input.pcd", help='pcd フォーマットの３次元点群ファイル（複数指定可）', nargs='+')
args = parser.parse_args()

pcds = []
for f in vars(args)["input.pcd"]:
    pcd = read_point_cloud(f)
    pcds.append(pcd)

draw_geometries(pcds)

if len(pcds) > 1:
    for pcd in pcds:
        draw_geometries([pcd])

#vis = Visualizer()
#vis.create_window()
#vis.add_geometry(pcds[0])
#vis.run()
#vis.destroy_window()
#vis = Visualizer()
#vis.create_window()
#vis.add_geometry(pcds[1])
#vis.run()
#vis.destroy_window()

#index = 0
#def next_pcd(vis):
#    vis.destroy_window()
#    global index
#    index += 1
#    if index >= len(pcds):
#        index -= 1
#    print(index)
#    vis = Visualizer()
#    vis.create_window()
#    vis.add_geometry(pcds[index])
#    vis.run()
#    vis.destroy_window()
#def prev_pcd(vis):
#    vis.destroy_window()
#    global index
#    index -= 1
#    if index < 0:
#        index = 0
#    print(index)
#    vis = Visualizer()
#    vis.create_window()
#    vis.add_geometry(pcds[index])
#    vis.run()
#    vis.destroy_window()
#key_to_callback = {}
#key_to_callback[ord("K")] = next_pcd
#key_to_callback[ord("J")] = prev_pcd
#draw_geometries_with_key_callbacks(pcds, key_to_callback)



