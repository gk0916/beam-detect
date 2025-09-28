# import json
# import os
# import os.path as osp
# import base64
# import warnings
# from PIL import Image
 
# # import PIL.Image
# import yaml
# from labelme import utils
# import cv2
# import numpy as np
# # from skimage import img_as_ubyte
 
 
# def main(json_file):
#     warnings.warn("This script is aimed to demonstrate how to convert the\\n"
#                   "JSON file to a single image dataset, and not to handle\\n"
#                   "multiple JSON files to generate a real-use dataset.")
#     # json文件加入列表
#     list_path = []
#     for json_single in os.listdir(json_file):
#         if json_single.endswith('.json'):
#             list_path.append(json_single)
 
#     for i in range(0, len(list_path)):
#         # 挨个读取json文件
#         path = os.path.join(json_file, list_path[i])
#         if os.path.isfile(path):
#             data = json.load(open(path,encoding='utf-8'))
#             img = utils.img_b64_to_arr(data['imageData'])
#             print('imagedata: ', data['imageData'])
#             print('datashape: ', data['shapes'])
#             lbl, lbl_names = utils.labelme_shapes_to_label(img.shape, data['shapes'])
 
#             captions = ['%d: %s' % (l, name) for l, name in enumerate(lbl_names)]
 
#             lbl_viz = utils.draw_label(lbl, img, captions)
#             # out_dir = osp.basename(path).replace('.', '_')
#             out_dir = osp.basename(path).split('.json')[0]
#             save_file_name = out_dir
#             # out_dir = osp.join(osp.dirname(path), out_dir)
 
#             if not osp.exists(json_file + 'mask'):
#                 os.mkdir(json_file + 'mask')
#             maskdir = json_file + 'mask'
 
#             if not osp.exists(json_file + 'mask_viz'):
#                 os.mkdir(json_file + 'mask_viz')
#             maskvizdir = json_file + 'mask_viz'
#             out_dir1 = maskdir
 
#             # 保存
#             Image.fromarray(lbl).save(out_dir1 + '/' + save_file_name + '.png')
#             Image.fromarray(lbl_viz).save(maskvizdir + '/' + save_file_name + '_label_viz.png')
 
#             with open(osp.join(out_dir1, 'label_names.txt'), 'w') as f:
#                 for lbl_name in lbl_names:
#                     f.write(lbl_name + '\\n')
#             warnings.warn('info.yaml is being replaced by label_names.txt')
#             info = dict(label_names=lbl_names)
#             with open(osp.join(out_dir1, 'info.yaml'), 'w') as f:
#                 yaml.safe_dump(info, f, default_flow_style=False)
#             print('Saved to: %s' % out_dir1)
 
 
# if __name__ == '__main__':
#     json_file = r"D:\\dev\\datasets\\dataset\\crack.v2i.yolov8\\test-seg-test\\images\\"
#     main(json_file)


# import cv2 as cv
# import numpy as np
# import json
# import os


# def convertPolygonToMask(jsonfilePath):
#     with open(jsonfilePath, "r", encoding='utf-8') as jsonf:
#         jsonData = json.load(jsonf)
#         img_h = jsonData["imageHeight"]
#         img_w = jsonData["imageWidth"]
#         mask = np.zeros((img_h, img_w), np.uint8)
#         #图片中目标的数量 num=len(jsonData["shapes"])
#         num = 0
#         for obj in jsonData["shapes"]:
#             label = obj["label"]
#             polygonPoints = obj["points"]
#             polygonPoints = np.array(polygonPoints,np.int32)
#             # print("+" * 50, "\\n", polygonPoints)
#             # print(label)
#             num+=1
#             cv.drawContours(mask,[polygonPoints],-1,(255),-1)

#     return mask

# def main():
#     jsonfileFolder = r"K:\\imageData\\colorR\\dataset\\label"
#     maskSaveFolder = r"K:\\imageData\\colorR\\dataset\\mask"

#     for jsonfile in os.listdir(jsonfileFolder):
#         jsonfilePath = os.path.join(jsonfileFolder,jsonfile)
#         mask = convertPolygonToMask(jsonfilePath)
#         maskName = jsonfile.split(".")[0] + ".png"
#         maskPath = os.path.join(maskSaveFolder,maskName)
#         cv.imwrite(maskPath,mask)


# if __name__ == "__main__":
#     #main()
#     jsonfilePath = r"D:\\dev\\datasets\\dataset\\crack.v2i.yolov8\\test-seg-test\\images\\1616.rf.c868709931a671796794fdbb95352c5a.json"
#     maskSaveFolder = r"D:\\dev\\datasets\\dataset"
#     mask = convertPolygonToMask(jsonfilePath)
#     # 为了可视化把mask做一下阈值分割
#     _, th = cv.threshold(mask, 0, 255, cv.THRESH_BINARY)
#     cv.imshow("mask", th)
#     src = cv.imread(r"D:\\dev\\datasets\\dataset\\crack.v2i.yolov8\\test-seg-test\\images\\1616.rf.c868709931a671796794fdbb95352c5a.jpg")
#     cv.imwrite(maskSaveFolder + "\\mask.png", mask)
#     cv.imshow("src", src)
#     cv.waitKey(0)
#     cv.destroyAllWindows()



import argparse
import json
import os
import os
import PIL.Image
import yaml
from labelme import utils
import base64
import numpy as np
import cv2 as cv
from skimage import img_as_ubyte


def parse_arguments():
    parser = argparse.ArgumentParser(description="This script is aimed to demonstrate how to convert the\n"
                  "JSON file to a single image dataset, and not to handle\n"
                  "multiple JSON files to generate a real-use dataset.")
    parser.add_argument("--input_path", type=str,default='segmentation')
    parser.add_argument("--output_path", type=str,default='seg2_mask')
    return parser.parse_args()

def main():


    args = parse_arguments()
    target = args.output_path
    if not os.path.exists(target):
        os.mkdir(target)
    if not os.path.exists(target+'/img/'):
        os.mkdir(target+'/img/')
    if not os.path.exists(target+'/label/'):
        os.mkdir(target+'/label/' )

    json_file = args.input_path
    count = [e for e in os.listdir(json_file) if e.endswith('.json')]
    for i in range(0, len(count)):
        path = os.path.join(json_file, count[i])
        name = count[i].split('.')[0]
        if os.path.isfile(path):
            data = json.load(open(path))

            if data['imageData']: #包含数据 直接读入
                imageData = data['imageData']
            else:  # 不包含去路径读入
                imagePath = os.path.join(os.path.dirname(path), data['imagePath'])
                with open(imagePath, 'rb') as f:
                    imageData = f.read()
                    imageData = base64.b64encode(imageData).decode('utf-8')
            img_b64decode = base64.b64decode(imageData)  # base64解码
            img_array = np.frombuffer(img_b64decode, np.uint8)  # 转换np序列
            img = cv.imdecode(img_array, cv.COLOR_BGR2RGB)  # 转换Opencv格式

            # create mask
            mask = np.zeros_like(img, dtype=np.uint8)
            # get the points
            if len(data["shapes"])<2: 
                print(count[i])
                continue
            if data["shapes"][0]['label'] == 'pupil':
                points = data["shapes"][1]["points"]
                points = np.array(points, dtype=np.int32)  # tips: points location must be int32
                cv.fillPoly(mask, [points], (255, 255, 255))

                points = data["shapes"][0]["points"]
                points = np.array(points, dtype=np.int32)  # tips: points location must be int32
                cv.fillPoly(mask, [points], (0, 0, 0))
            else:
                points = data["shapes"][0]["points"]
                points = np.array(points, dtype=np.int32)  # tips: points location must be int32
                cv.fillPoly(mask, [points], (255, 255, 255))

                points = data["shapes"][1]["points"]
                points = np.array(points, dtype=np.int32)  # tips: points location must be int32
                cv.fillPoly(mask, [points], (0, 0, 0))
                
            cv.imwrite('%s/img/%s.png' % (target, name), img)
            cv.imwrite('%s/label/%s.png' % (target, name), mask)




if __name__ == '__main__':
    main()