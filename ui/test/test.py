# import cv2

# from ultralytics import YOLO

# # Load the YOLO11 model
# model = YOLO("yolo11n.pt")

# # Open the video file
# video_path = "H:\\datasets\\traffic_video\\41315-429396382_small.mp4"
# cap = cv2.VideoCapture(video_path)

# # Loop through the video frames
# while cap.isOpened():
#     # Read a frame from the video
#     success, frame = cap.read()

#     if success:
#         # Run YOLO11 tracking on the frame, persisting tracks between frames
#         results = model.track(frame, persist=True)

#         # Visualize the results on the frame
#         annotated_frame = results[0].plot()

#         # Display the annotated frame
#         cv2.imshow("YOLO11 Tracking", annotated_frame)

#         # Break the loop if 'q' is pressed
#         if cv2.waitKey(1) & 0xFF == ord("q"):
#             break
#     else:
#         # Break the loop if the end of the video is reached
#         break

# # Release the video capture object and close the display window
# cap.release()
# cv2.destroyAllWindows()

# '''
# 通过队列实现生产者消费者模型
# '''

# import threading,queue,time


# # 创建一个队列，队列最大长度为2
# q = queue.Queue(maxsize=2)


# def product():
#     while True:
#         # 生产者往队列塞数据
#         q.put('money')
#         print('生产时间',time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
#         print('生产了')

# def consume():
#     while True:
#         time.sleep(2)
#         # 消费者取出数据
#         data = q.get()
#         print('消费时间',time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
#         print('消费了%s'%data)


# t = threading.Thread(target=product)
# t1 = threading.Thread(target=consume)
# t.start()
# t1.start()


# import queue
# import time
# import threading

# def set_value(q):
#     index = 0
#     while True:
#         q.put(index)
#         index += 1
#         time.sleep(3)

# def get_value(q):
#     index = 0
#     while True:
#         print(q.get())
#         time.sleep(0.5)
# def main():
#     q = queue.Queue(4)
#     t1 = threading.Thread(target=set_value,args=[q])
#     t2 = threading.Thread(target=get_value,args=[q])
#     t1.start()
#     t2.start()


# if __name__ == '__main__':
#     main()


# """
# 安装依赖库：
# 1. Pillow
# 2. PySide2
# 3. PyQtGraph
# from https://blog.csdn.net/zhy29563/article/details/119754910
# """

# import sys

# import numpy as np
# import pyqtgraph as pg
# from PIL import Image
# from PyQt5.QtWidgets import QApplication, QVBoxLayout, QPushButton, QWidget, QFileDialog
# from pyqtgraph import ImageView

# # 设置 PyQtGraph 显示配置
# ########################################################################################################################
# # 设置显示背景色为白色，默认为黑色
# pg.setConfigOption('background', 'w')
# # 设置显示前景色为黑色，默认为灰色
# pg.setConfigOption('foreground', 'k')
# # 设置图像显示以行为主，默认以列为主
# pg.setConfigOption('imageAxisOrder', 'row-major')


# class PyQtGraphicDemo(QWidget):
#     def __init__(self, parent=None):
#         super(PyQtGraphicDemo, self).__init__(parent)

#         self.resize(600, 400)

#         # 图像显示控件
#         self.graphicsView = ImageView(self)
#         # 隐藏直方图，菜单按钮，ROI
#         self.graphicsView.ui.histogram.hide()
#         self.graphicsView.ui.menuBtn.hide()
#         self.graphicsView.ui.roiBtn.hide()

#         image = Image.open(r'E:\\iray_mv\\MV Viewer\Development\Samples\\Python\\IMV\\opencv_byGetFrame\\myWindow_screenshot_27.11.2024.png')
#         if image is not None:
#             # 如果之前未设置显示选项以行为主，这里需要对显示图像进行转置
#             self.graphicsView.setImage(np.array(image))

#         self.verticalLayout = QVBoxLayout(self)
#         self.verticalLayout.addWidget(self.graphicsView)

#         # 设置窗口布局
#         self.setLayout(self.verticalLayout)


# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     window = PyQtGraphicDemo()
#     window.show()
#     sys.exit(app.exec_())


# -*- coding: utf-8 -*-
# import time

# from PyQt5 import QtWidgets, QtCore, QtGui
# from PyQt5.QtCore import QSize
# from PyQt5.QtCore import Qt
# from PyQt5.QtCore import pyqtSignal
# from PyQt5.QtGui import QCursor
# from PyQt5.QtGui import QPixmap
# from PyQt5.QtWidgets import QApplication
# from PyQt5.QtWidgets import QMenu, QAbstractItemView, QListWidgetItem, QListView
# from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout


# class ImageListWidget(QtWidgets.QListWidget):
#     signal = pyqtSignal(list)

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.image_cmp_widget = None
#         self.single_image = None
#         self.setWindowTitle('All Images')
#         self.resize(1400, 700)
#         self.setContextMenuPolicy(Qt.CustomContextMenu)
#         # 创建QMenu信号事件
#         self.customContextMenuRequested.connect(self.showMenu)
#         self.contextMenu = QMenu(self)
#         self.CMP = self.contextMenu.addAction('比较')
#         # self.CP = self.contextMenu.addAction('复制')
#         self.DL = self.contextMenu.addAction('删除')
#         # self.CP.triggered.connect(self.copy)
#         self.DL.triggered.connect(self.del_text)

#         # 设置每个item size
#         self.setGridSize(QtCore.QSize(220, 190))
#         # 设置横向list
#         self.setFlow(QListView.LeftToRight)
#         # 设置换行
#         self.setWrapping(True)
#         # 窗口size 变化后重新计算列数
#         self.setResizeMode(QtWidgets.QListView.Adjust)
#         # 设置选择模式
#         self.setSelectionMode(QAbstractItemView.ExtendedSelection)
#         self.setIconSize(QSize(200, 150))

#     # 显示右键菜单
#     def showMenu(self, pos):
#         # pos 鼠标位置
#         # 菜单显示前,将它移动到鼠标点击的位置
#         self.contextMenu.exec_(QCursor.pos())  # 在鼠标位置显示

#     # 获取选择行的内容
#     def selected_text(self):
#         try:
#             selected = self.selectedItems()
#             texts = ''
#             for item in selected:
#                 if texts:
#                     texts = texts + '\n' + item.text()
#                 else:
#                     texts = item.text()
#         except BaseException as e:
#             print(e)
#             return
#         print('selected_text texts', texts)
#         return texts

#     def copy(self):
#         text = self.selected_text()
#         if text:
#             clipboard = QApplication.clipboard()
#             clipboard.setText(text)

#     def del_text(self):
#         try:
#             index = self.selectedIndexes()
#             row = []

#             for i in index:
#                 r = i.row()
#                 row.append(r)
#             for i in sorted(row, reverse=True):
#                 self.takeItem(i)
#         except BaseException as e:
#             print(e)
#             return
#         self.signal.emit(row)

#     def mouseDoubleClickEvent(self, e: QtGui.QMouseEvent) -> None:
#         super().mouseDoubleClickEvent(e)
#         print('double click')
#         selected = self.selectedItems()
#         img_path = ''
#         for item in selected:
#             img_path = item.image_path()
#         if len(img_path) > 0:
#             # 打开新窗口显示单张图片
#             # self.single_image = SingleImageView(image=img_path, background=Qt.white)
#             # self.single_image.show()
#             pass
#         pass

#     def load_images(self, paths):
#         for i in range(len(paths)):
#             img_item = ImageQListWidgetItem("dump image ***", paths[i])
#             self.addItem(img_item)
#             self.setItemWidget(img_item, img_item.widget)

#             # 刷新界面
#             QApplication.processEvents()


# # 自定义的item 继承自QListWidgetItem
# class ImageQListWidgetItem(QListWidgetItem):
#     def __init__(self, name, img_path):
#         super().__init__()

#         self.img_path = img_path
#         # 自定义item中的widget 用来显示自定义的内容
#         self.widget = QWidget()
#         # 用来显示name
#         self.nameLabel = QLabel()
#         self.nameLabel.setText(name)
#         # 用来显示avator(图像)
#         self.avatorLabel = QLabel()
#         # 设置图像源 和 图像大小
#         img_obg = QPixmap(img_path)
#         width = img_obg.width()
#         height = img_obg.height()
#         scale_size = QSize(200, 150)
#         if width < height:
#             scale_size = QSize(150, 200)
#         self.avatorLabel.setPixmap(QPixmap(img_path).scaled(scale_size))
#         # 图像自适应窗口大小
#         self.avatorLabel.setScaledContents(True)
#         # 设置布局用来对nameLabel和avatorLabel进行布局
#         self.hbox = QVBoxLayout()
#         self.hbox.addWidget(self.avatorLabel)
#         self.hbox.addWidget(self.nameLabel)
#         self.hbox.addStretch(1)
#         # 设置widget的布局
#         self.widget.setLayout(self.hbox)
#         # 设置自定义的QListWidgetItem的sizeHint，不然无法显示
#         self.setSizeHint(self.widget.sizeHint())

#     def image_path(self):
#         return self.img_path


# if __name__ == '__main__':
#     print('main layout show')
#     now = time.time()
#     app = QApplication([])
#     main_window = ImageListWidget()
#     main_window.show()

#     image_list = ['icon.jpg', 'icon.jpg', 'icon.jpg']
#     # 数据扩充
#     image_list = image_list + image_list + image_list + image_list
#     main_window.load_images(image_list)

#     # 绑定点击槽函数 点击显示对应item中的name
#     main_window.itemClicked.connect(lambda item: print('clicked item label:', item.nameLabel.text()))
#     print("ImageListWidget 耗时: {:.2f}秒".format(time.time() - now))

#     app.exec_()

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from CamOperation_class import CameraOperation
from MvCameraControl_class import *
from MvErrorDefine_const import *
from CameraParams_header import *
from test_ui import Ui_MainWindow
import ctypes
from camera.MVSDK.IMVApi import *
from camera.device import *
from detect_task import result2Db

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(mainWindow)
    print(f'setuped ui')
    # ui.bnEnum.clicked.connect(enum_devices)
    # ui.bnOpen.clicked.connect(open_device)
    # ui.bnClose.clicked.connect(close_device)
    # ui.bnStart.clicked.connect(start_detecting)
    # ui.bnStop.clicked.connect(stop_detecting)

    # ui.bnSoftwareTrigger.clicked.connect(trigger_once)
    # ui.radioTriggerMode.clicked.connect(set_software_trigger_mode)
    # ui.radioContinueMode.clicked.connect(set_continue_mode)

    # ui.bnGetParam.clicked.connect(get_param)
    # ui.bnSetParam.clicked.connect(set_param)

    # ui.bnSaveImage.clicked.connect(save_bmp)

    # pic = QLabel(ui.widgetDisplay)
    # pic.setGeometry(10, 60, 511, 401)
    # #use full ABSOLUTE path to the image, not relative
    # pic.setPixmap(QPixmap("C:\\Users\\u1\\Pictures\\image_0001.jpg"))

    mainWindow.show()

    app.exec_()


    sys.exit()
