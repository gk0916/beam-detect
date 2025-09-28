# -*- coding: utf-8 -*-

import os
import math
import time

from PIL import Image


def crop(image, save_path=None):
    img = Image.open(image).convert('RGB')  # 0~255
    width, height = img.size
    # 向上取整，保证原图所有部分都被切割到，不足部分填充0块
    # 若想不保留不满640像素的块，可以向下取整math.floor()
    width_split_num = math.ceil(width / 640)
    height_split_num = math.ceil(height / 640)

    file_name = os.path.basename(image)
    file_name, file_ext = os.path.splitext(file_name)

    cropped_imgs = {}
    for m in range(height_split_num):
        for n in range(width_split_num):
            # left, upper, right, lower
            left = n * 640
            upper = m * 640

            # 直接剪裁默认填充黑色0块
            # right = (n+1) * 640
            # lower = (m+1) * 640

            right = (n + 1) * 640 if n < width_split_num - 1 else width
            lower = (m + 1) * 640 if m < height_split_num - 1 else height
            # 剪裁
            cropped_img = img.crop((left, upper, right, lower))

            # 自定义颜色填充边框
            # e.g. white, black, red
            color = 'white'
            if n == width_split_num - 1 or m == height_split_num - 1:
                # cropped_img = ImageOps.pad(cropped_img, (640, 640), color=color, centering=(0, 0))
                background = Image.new(cropped_img.mode, (640, 640), color=color)
                background.paste(cropped_img, box=(0, 0))
                cropped_img = background
            else:
                None

            # 保存
            img_name = f'{file_name}-{m + 1}行-{n + 1}列{file_ext}'
            if save_path is not None:
                img_name = os.path.join(save_path, img_name)
                cropped_img.save(img_name)
            cropped_imgs[img_name] = cropped_img
    return cropped_imgs


def list_file(data_dir) -> list:
    all_files = []
    # data_dir
    if os.path.isdir(data_dir):
        for root, dirs, files in os.walk(data_dir):
            for file in list(filter(lambda x: x.upper().endswith('.JPG') or x.lower().endswith('.PNG'), files)):
                all_files.append(os.path.join(root, file))
    elif os.path.isfile(data_dir):
        all_files.append(data_dir)
    return all_files


def list_folder_files(data_dir) -> list:
    t1 = time.time()
    from pathlib import Path


    folder_files = {}
    # data_dir
    if os.path.isdir(data_dir):
        for root, dirs, files in os.walk(data_dir):
            img_files = []
            # print(f'root: {root},{dir},{files}')
            for file in list(filter(lambda x: x.upper().endswith('.JPG') or x.upper().endswith('.PNG')
                                    or x.upper().endswith('.AVI'), files)):
                img_files.append(Path(
                    # os.path.abspath(
                        os.path.join(root, file)
                        # )
                        ).as_posix())
            folder_files[root] = img_files
    # print(f'folder_files: {folder_files}')

    t2 = time.time()

    print('遍历文件运行时间:%s毫秒' % ((t2 - t1) * 1000))
    return folder_files
