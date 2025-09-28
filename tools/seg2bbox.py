import os
import argparse
import io

def seg_to_bbox(seg_info):
    # Example input: 5 0.046875 0.369141 0.0644531 0.384766 0.0800781 0.402344 ...
    class_id, *points = seg_info.split()
    points = [float(p) for p in points]
    x_min, y_min, x_max, y_max = min(points[0::2]), min(points[1::2]), max(points[0::2]), max(points[1::2])
    width, height = x_max - x_min, y_max - y_min
    x_center, y_center = (x_min + x_max) / 2, (y_min + y_max) / 2
    bbox_info = f"{int(class_id)} {x_center} {y_center} {width} {height}"
    return bbox_info



parser = argparse.ArgumentParser()
parser.add_argument('data')
args = parser.parse_args()

  

files = os.listdir(args.data)
files = list(filter(lambda x: x.lower().endswith('.txt'), files))
for file in files:
    print(file)
    if not os.path.exists(os.path.join(args.data,'bbox-labels')):
        os.makedirs(os.path.join(args.data,'bbox-labels'))
    f2 = open(os.path.join(args.data,'bbox-labels',file), 'w', encoding='utf-8')
    fi = io.open(os.path.join(args.data, file), mode='r+')

    for line in fi.readlines():
        bbox_info = seg_to_bbox(line)
        f2.write(bbox_info)
        f2.write('\r')

    f2.close()
    
