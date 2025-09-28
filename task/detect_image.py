from ultralytics import YOLO
from PIL import Image
import argparse
import time
import os
from db.dbModels import BusiBeamPicBuiler
from db import dbService
from util.utils import crop, list_file, list_folder_files
import re
import platform
from pyzbar import pyzbar

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

IMAGE_COUNT_PER_ROW = 10
PREDICT_THRESHOLD = 0.5
define_class_names = {0: 'crack', 1:'bubble'}
# define_class_names = {1: 'crack', 0:'bubble'}
define_class2key = {'crack': 0,
                    'bubble': 1,
                    'honeycomb': 2,
                    'pittedsurface': 3,
                    'cornerloss': 4,
                    'peeling': 5,
                    'sandlines': 6,
                    'exposedtendons': 7,
                    'rootrot': 8,
                    'holes': 9}
# define_class2key = {'crack': 1,
#                     'bubble': 0,
#                     'honeycomb': 2,
#                     'pittedsurface': 3,
#                     'cornerloss': 4,
#                     'peeling': 5,
#                     'sandlines': 6,
#                     'exposedtendons': 7,
#                     'rootrot': 8,
#                     'holes': 9}

def detect_QR_code(images):
    for img in images:
        barcodes = pyzbar.decode(img,symbols=[pyzbar.ZBarSymbol.QRCODE])

        for barcode in barcodes:
            barcode_data = barcode.data.decode("utf-8")
            barcode_type = barcode.type
            
            if barcode_data and barcode_data != '':
                # print("Barcode Type: {}, Barcode Data: {}".format(barcode_type, barcode_data))
                return barcode_data    
    return None

# # callback
# # global QR_code
# # QR_code = None
# def on_predict_end(predictor):
#     global QR_code
#     for batch in predictor.dataset:
#         if QR_code:
#             break
#         paths, im0s, s = batch
#         if not QR_code:
#             QR_code = detect_QR_code(im0s)
#         else:
#             break
    
#     # if not code:
#     #     predictor.results = []
#     #     # TODO: exeption for no code

#     # for result in predictor.results:
#     #     result.QR_code = code
    


def predict_no_crop(model, folder, images):
    source_name = os.path.basename(folder)
    # images = list_file(source)
    # model = YOLO(model)
    # model = YOLO('yolov8n.pt')
    # model.add_callback('on_predict_end',on_predict_end)

    # size = Image.open(images[0]).size
    results = []
    t1 = time.time()
    # 以原图尺寸检测
    for im in images:
        print(f'im: {im}')
        size = Image.open(im).size
        # result = model.predict(project='mark_pics/' + source_name
        result = model.track(project='mark_pics/' + source_name
                            , name='predict'
                            , source=im
                            , persist=True
                            , task='detect'
                            , save=True
                            , exist_ok=True
                            # , save_crop=True
                            # 尺寸信息传入
                            , imgsz=size
                            , conf=PREDICT_THRESHOLD
                            , show_labels=True
                            , show_conf=True
                            #    , save_txt=True
                            , device = args.device
                            , visualize = args.visualize
                            )
        results.extend(result)
    t2 = time.time()
    print('原图尺寸检测运行时间:%s毫秒' % ((t2 - t1) * 1000))
    return results


# def predict_with_crop(model, source):
#     source_name = os.path.basename(source)
#     images = list_file(source)
#     model = YOLO(model)
    
#     results = []
#     # 裁剪为640*640尺寸检测
#     T1 = time.time()
#     for image in images:
#         croped_images = crop(image, None)
#         result = model.predict(project=source_name
#                                , name=source_name + '_predict'
#                                , source=list(croped_images.values())
#                                , save=True
#                                , conf=PREDICT_THRESHOLD
#                                , show_labels=True
#                                , show_conf=True
#                             #    , save_txt=True
#                                )
#         results.append(result)
#     T2 = time.time()
#     print('剪裁为640*640尺寸检测运行时间:%s毫秒' % ((T2 - T1) * 1000))
#     return result




'''
通过图片文件路径解析映射梁体位置。图片路径命名规则：1/2面-i排-j张，例如：1面-1排-1张；2面-1排-2张
解析结果：
    par_type = 1或2；
    若每排拍摄图片张数固定为n：pic_order = (i-1)*n + j
    todo: 若不固定以1或2文件夹下图片排序计数
'''
def parseImageCoordinate(image_path: str):
    # pass
    # 每排拍摄图片张数固定为n
    n = IMAGE_COUNT_PER_ROW

    pattern = r'.*(\d+)面-(\d+)排-(\d+)张'
    
    res = re.match(pattern, image_path, re.M|re.I)
    if res:
        part_type = res.group(1)
        pic_order = (int(res.group(2))  - 1) * n + int(res.group(3))
    else:
        raise Exception(f'图片保存路径不符合命名规则，路径：{image_path}')
    return part_type, pic_order


def result2Db(results: list):
    datas = []
    total_datas = {}
    cls_ids = {}
    sub_data = {
        'bubble_num': 0,
        'crack_num': 0,
        'honeycomb_num': 0,
        'pittedsurface_num': 0,
        'cornerloss_num': 0,
        'peeling_num': 0,
        'sandlines_num': 0,
        'exposedtendons_num': 0,
        'rootrot_num': 0,
        'holes_num': 0,
    }
    
    QR_code = None
    for result in results:
        orig_img = result.orig_img
        # QR_code = 'A004'
        QR_code = detect_QR_code([orig_img])
        if QR_code:
            break
    beam_code = QR_code
      
    part = 0
    count = 0
    for i in range(len(results)):
        result = results[i]
        origin_pic = result.path
        part_type, pic_order = parseImageCoordinate(origin_pic)
        # todo: 每排拍摄张数不固定时，pic_order以在当前文件夹下的排序计数
        if part_type != part:
            count = pic_order = 1
            part = part_type
        else:
            count += 1
            pic_order = count

        mark_pic = os.path.join(result.save_dir, os.path.basename(origin_pic))
        if platform.system().lower() == 'windows':
            mark_pic = mark_pic.replace('\\','/')
        # 前端显示加虚拟路径profile
        mark_pic = '/profile/' + mark_pic
        pic_height  = result.boxes.orig_shape[0]
        pic_width = result.boxes.orig_shape[1]

        label_names = result.names
        # if label_names != define_class_names:
        #     raise Exception(f'检测结果标签与定义标签不匹配；定义标签：{define_class_names},检测标签：{label_names}')

        # 各标签检测数量
        # print(f'boxes:{result.boxes}')
        if not result.boxes.is_track:
            cls = []
            ids = []
        else:
            cls = result.boxes.cls.tolist()
            ids = result.boxes.id.tolist()
        # detect_result = Counter(result.boxes.cls.tolist())
        detect_result = dict(zip(map(int,cls),map(int,ids)))
        cls_ids.update(detect_result) 
        # beam_code = predict_QR_code()
        # beam_code = result.QR_code
        # beam_code = QR_code

        bubble_num = detect_result[define_class2key['bubble']] if define_class2key['bubble'] in detect_result else 0
        crack_num = detect_result[define_class2key['crack']] if define_class2key['crack'] in detect_result else 0
        honeycomb_num = detect_result[define_class2key['honeycomb']] if define_class2key['honeycomb'] in detect_result else 0
        pittedsurface_num = detect_result[define_class2key['pittedsurface']] if define_class2key['pittedsurface'] in detect_result else 0
        cornerloss_num = detect_result[define_class2key['cornerloss']] if define_class2key['cornerloss'] in detect_result else 0
        peeling_num = detect_result[define_class2key['peeling']] if define_class2key['peeling'] in detect_result else 0
        sandlines_num = detect_result[define_class2key['sandlines']] if define_class2key['sandlines'] in detect_result else 0
        exposedtendons_num = detect_result[define_class2key['exposedtendons']] if define_class2key['exposedtendons'] in detect_result else 0
        rootrot_num = detect_result[define_class2key['rootrot']] if define_class2key['rootrot'] in detect_result else 0
        holes_num = detect_result[define_class2key['holes']] if define_class2key['holes'] in detect_result else 0

        busi_beam_pic = (BusiBeamPicBuiler().beam_code(beam_code)
                         .part_type(part_type)
                         .pic_order(pic_order)
                         .pic_length(pic_height)
                         .pic_width(pic_width)
                         .oripic_url(origin_pic)
                         .markpic_url(mark_pic)
                         .bubble_num(bubble_num)
                         .crack_num(crack_num)
                         .honeycomb_num(honeycomb_num)
                         .pittedsurface_num(pittedsurface_num)
                         .cornerloss_num(cornerloss_num)
                         .peeling_num(peeling_num)
                         .sandlines_num(sandlines_num)
                         .exposedtendons_num(exposedtendons_num)
                         .rootrot_num(rootrot_num)
                         .holes_num(holes_num)
                         .build())
        datas.append(busi_beam_pic)
        print(f'busi_beam_pic is: {busi_beam_pic}')

        # if i == 0:
        #     total_datas[beam_code] = sub_data
        # total_datas[beam_code]['bubble_num'] = total_datas[beam_code]['bubble_num'] + bubble_num
        # total_datas[beam_code]['crack_num'] = total_datas[beam_code]['crack_num'] + crack_num
        # total_datas[beam_code]['honeycomb_num'] = total_datas[beam_code]['honeycomb_num'] + honeycomb_num
        # total_datas[beam_code]['pittedsurface_num'] = total_datas[beam_code]['pittedsurface_num'] + pittedsurface_num
        # total_datas[beam_code]['cornerloss_num'] = total_datas[beam_code]['cornerloss_num'] + cornerloss_num
        # total_datas[beam_code]['peeling_num'] = total_datas[beam_code]['peeling_num'] + peeling_num
        # total_datas[beam_code]['sandlines_num'] = total_datas[beam_code]['sandlines_num'] + sandlines_num
        # total_datas[beam_code]['exposedtendons_num'] = total_datas[beam_code]['exposedtendons_num'] + exposedtendons_num
        # total_datas[beam_code]['rootrot_num'] = total_datas[beam_code]['rootrot_num'] + rootrot_num
        # total_datas[beam_code]['holes_num'] = total_datas[beam_code]['holes_num'] + holes_num
    print(f'cls_ids: {cls_ids}')
    print(f'key: {define_class2key['bubble']}')
    total_datas['beam_code'] = beam_code
    total_datas['bubble_num'] = cls_ids[define_class2key['bubble']] if define_class2key['bubble'] in cls_ids else 0
    total_datas['crack_num'] = cls_ids[define_class2key['crack']] if define_class2key['crack'] in cls_ids else 0
    total_datas['honeycomb_num'] = cls_ids[define_class2key['honeycomb']] if define_class2key['honeycomb'] in cls_ids else 0
    total_datas['pittedsurface_num'] = cls_ids[define_class2key['pittedsurface']] if define_class2key['pittedsurface'] in cls_ids else 0
    total_datas['cornerloss_num'] = cls_ids[define_class2key['cornerloss']] if define_class2key['cornerloss'] in cls_ids else 0
    total_datas['peeling_num'] = cls_ids[define_class2key['peeling']] if define_class2key['peeling'] in cls_ids else 0
    total_datas['sandlines_num'] = cls_ids[define_class2key['sandlines']] if define_class2key['sandlines'] in cls_ids else 0
    total_datas['exposedtendons_num'] = cls_ids[define_class2key['exposedtendons']] if define_class2key['exposedtendons'] in cls_ids else 0
    total_datas['rootrot_num'] = cls_ids[define_class2key['rootrot']] if define_class2key['rootrot'] in cls_ids else 0
    total_datas['holes_num'] = cls_ids[define_class2key['holes']] if define_class2key['holes'] in cls_ids else 0

    print(f'busi_beam is: {beam_code} => {total_datas}')
    try:    
        # 批量写入数据库
        dbService.session.begin()
        if dbService.database_open:
            dbService.update_busi_beam_pic_list(datas)
            dbService.update_busi_beam(beam_code,total_datas[beam_code])
        dbService.session.commit()
    except Exception as e:
        dbService.session.rollback()
        print(f'rollback data beacause of error: {e}')
    finally:
        dbService.session.close()
    return total_datas

# python detect_task.py --model D:\dev\best.pt --source D:\dev\workspaces\precast-beam-detect\dataset\beam-images
parser = argparse.ArgumentParser()
parser.add_argument("-m", "--model", help="模型文件")
parser.add_argument("-src", "--source", help="待检测文件")
parser.add_argument("-d", "--device", default=0)
parser.add_argument("-vsl", "--visualize", default=False, type=bool)
parser.add_argument("-db", "--database", default=False, type=bool)
args = parser.parse_args()

def init_model(model='yolov8n.pt'):
    t1 = time.time()
    
    model = YOLO(model)
    # model.add_callback('on_predict_end',on_predict_end)
    
    t2 = time.time()
    print('加载模型运行时间:%s毫秒' % ((t2 - t1) * 1000))
    
    return model

def detectFrame(model,job,image):
        # predict
        t1 = time.time()
        # 以原图尺寸检测
        results = model.track(project=job
                            , name='predict'
                            , source=image
                            , persist=True
                            , task='detect'
                            , save=True
                            , exist_ok=True
                            # , save_crop=True
                            # 尺寸信息传入
                            # , imgsz=(5120,5120)
                            , conf=PREDICT_THRESHOLD
                            , show_labels=True
                            , show_conf=True
                            #    , save_txt=True
                            , device = args.device
                            , visualize = args.visualize
                            )
        t2 = time.time()
        print('图片-原图尺寸检测运行时间:%s毫秒' % ((t2 - t1) * 1000))
        # save
        result2Db(results)
        return results

def detect(source,model='models/bubble-best.pt'):
    model = init_model(model=model)

    for folder, images in list_folder_files(source).items():
        # predict
        results = []
        t1 = time.time()
        # 以原图尺寸检测
        for im in images:
            print(f'im: {im}')
            result = model.track(project=source
                                , name='predict'
                                , source=im
                                , persist=True
                                , task='detect'
                                , save=True
                                , exist_ok=True
                                # , save_crop=True
                                # 尺寸信息传入
                                , imgsz=(5120,5120)
                                , conf=PREDICT_THRESHOLD
                                , show_labels=True
                                , show_conf=True
                                #    , save_txt=True
                                , device = args.device
                                , visualize = args.visualize
                                )
            results.extend(result)
        t2 = time.time()
        print('图片-原图尺寸检测运行时间:%s毫秒' % ((t2 - t1) * 1000))
        # save
        print(f'results: {results}')
        result2Db(results)


def track(source,model_file='models/bubble-best.pt'):
    model = init_model(model=model_file)

    for folder, videos in list_folder_files(source).items():
        # track
        results = []
        t1 = time.time()
        # 以原图尺寸检测
        for video in videos:
            print(f'video: {video}')
            result = model.track(project=source
                                , name='track'
                                , source=video
                                # , task='detect'
                                , save=True
                                , exist_ok=True
                                # , save_crop=True
                                # 尺寸信息传入
                                # , size = (5120,5120)
                                , conf=PREDICT_THRESHOLD
                                , show_labels=True
                                , show_conf=True
                                #    , save_txt=True
                                , device = args.device
                                , visualize = args.visualize
                                )
            results.extend(result)
        t2 = time.time()
        print('视频-原图尺寸检测运行时间:%s毫秒' % ((t2 - t1) * 1000))
        # save
        print(f'results: {results}')
        # result2Db(results)

if __name__ == '__main__':

    detect(args.source, args.model)