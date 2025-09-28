from ultralytics import YOLO
# from PIL import Image
import argparse
# import time
import os
# from collections import Counter

from db.dbModels import BusiBeamPicBuiler
from db import dbService
from util.utils import crop, list_file
import re
import platform
from pyzbar import pyzbar

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

IMAGE_COUNT_PER_ROW = 10
PREDICT_THRESHOLD = 0.5


parser = argparse.ArgumentParser()
parser.add_argument("-m", "--model", help="模型文件")
parser.add_argument("-src", "--source", help="待检测文件")
parser.add_argument("-d", "--device", default=0)
parser.add_argument("-vsl", "--visualize", default=False, type=bool)
parser.add_argument("-db", "--database", default=False, type=bool)
args = parser.parse_args()

model = YOLO(args.model)
# model.predict(source=args.source
#                             , task='detect'
#                             , save=True
#                             # , save_crop=True
#                             # 尺寸信息传入
#                             # , imgsz=size
#                             , conf=PREDICT_THRESHOLD
#                             , show_labels=True
#                             , show_conf=True
#                             #    , save_txt=True
#                             , device = args.device
#                             , visualize = args.visualize
#                             )
model.track(source=args.source,show=True)