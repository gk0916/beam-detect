# -*- coding: utf-8 -*-
import sys
import os
import ctypes
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtGui import QStandardItem
from PyQt5.QtCore import Qt
# from CamOperation_class import CameraOperation
# from MvCameraControl_class import *
# from MvErrorDefine_const import *
# from CameraParams_header import *
from ui.detect_main_ui import Ui_MainWindow
from camera.MVSDK.IMVApi import *
from camera.device import *
from task.detect_image import init_model, result2Db

# # 获取选取设备信息的索引，通过[]之间的字符去解析
# def TxtWrapBy(start_str, end, all):
#     start = all.find(start_str)
#     if start >= 0:
#         start += len(start_str)
#         end = all.find(end, start)
#         if end >= 0:
#             return all[start:end].strip()


# # 将返回的错误码转换为十六进制显示
# def ToHexStr(num):
#     chaDic = {10: 'a', 11: 'b', 12: 'c', 13: 'd', 14: 'e', 15: 'f'}
#     hexStr = ""
#     if num < 0:
#         num = num + 2 ** 32
#     while num >= 16:
#         digit = num % 16
#         hexStr = chaDic.get(digit, str(digit)) + hexStr
#         num //= 16
#     hexStr = chaDic.get(num, str(num)) + hexStr
#     return hexStr


if __name__ == "__main__":

    # # 绑定下拉列表至设备信息索引
    # def xFunc(event):
    #     global nSelCamIndex
    #     nSelCamIndex = TxtWrapBy("[", "]", ui.ComboDevices.get())

    # Decoding Characters
    def decoding_char(c_ubyte_value):
        c_char_p_value = ctypes.cast(c_ubyte_value, ctypes.c_char_p)
        try:
            decode_str = c_char_p_value.value.decode('gbk')  # Chinese characters
        except UnicodeDecodeError:
            decode_str = str(c_char_p_value.value)
        return decode_str

    #设置软触发配置
    def setSoftTriggerConf(cam):
        nRet = cam.IMV_SetEnumFeatureSymbol("TriggerSource", "Software")
        if IMV_OK != nRet:
            print("Set triggerSource value failed! ErrorCode[%d]" % nRet)
            return nRet

        nRet = cam.IMV_SetEnumFeatureSymbol("TriggerSelector", "FrameStart")
        if IMV_OK != nRet:
            print("Set triggerSelector value failed! ErrorCode[%d]" % nRet)
            return nRet

        nRet = cam.IMV_SetEnumFeatureSymbol("TriggerMode", "On")
        if IMV_OK != nRet:
            print("Set triggerMode value failed! ErrorCode[%d]" % nRet)
            return nRet

    # ch:枚举相机 | en:enum devices
    def enum_devices():
        global SysDevice
        SysDevice = DeviceSystem()
        SysDevice.initSystem()
        
        ui.ComboDevices.clear()
        # SysDevice.m_DeviceStr.append('test')
        ui.ComboDevices.addItems(SysDevice.m_DeviceStr)
        ui.ComboDevices.stateChange(None)
        enable_controls()
    
    # ch:打开相机 | en:open device
    def open_device():
        global isOpen
        global isDetecting
        global threads

        if not isOpen and len(ui.ComboDevices.selected_items) > 0:
            for cameraIndex in ui.ComboDevices.selected_items:
            # for cameraIndex in range(0, SysDevice.m_DeviceNum):
                device = SysDevice.m_Device[cameraIndex]
                ret = device.openDevicebyKey()
                if ret != IMV_OK:
                    print("open camera[%d] failed[%d]"% (cameraIndex, ret))
                    break

                setSoftTriggerConf(device.obj_cam)
                
                ret = device.startGrabbing(ui.pictureView)
                if ret != IMV_OK:
                    break

            # get_param()
            isOpen = True
            # isDetecting = True
            enable_controls()
        else:
            # TODO: 勾选提醒
            QMessageBox.information(ui.centralwidget,"消息提醒","请确认已选择对应相机！",QMessageBox.Ok|QMessageBox.Cancel,QMessageBox.Ok)
            pass

        #     get_param()

        #     isOpen = True
        #     enable_controls()

    # ch:开始检测
    def start_detecting():
        global job 
        job = f'mark_pics/job_{time.strftime("%Y-%m-%d_%H点%M分%S秒", time.localtime())}'
        global job_results 
        job_results = []
        global job_lock 
        job_lock = threading.Lock()
        if not os.path.exists(f'{job}'):
            os.makedirs(f'{job}')

        model_file = f'models/{ui.ComboModels.currentText()}' 
        detect_model = init_model(model=model_file)

        for cameraIndex in ui.ComboDevices.selected_items:
        # for cameraIndex in range(0, SysDevice.m_DeviceNum):
            device = SysDevice.m_Device[cameraIndex]
            ret = device.startDetecting(model=detect_model,job=job,job_lock=job_lock,job_results=job_results,winHandle=ui.pictureView)
            if ret != IMV_OK:
                break

        # get_param()
        global isOpen
        global isDetecting
        # isOpen = True
        isDetecting = True
        enable_controls()

    # ch:停止检测
    def stop_detecting():
        global job
        global job_results
        for cameraIndex in ui.ComboDevices.selected_items:
        # for cameraIndex in range(0, SysDevice.m_DeviceNum):
            device = SysDevice.m_Device[cameraIndex]
            ret = device.stopDetecting(job,job_lock,job_results,ui.pictureView)
            if ret != IMV_OK:
                break
        global isDetecting
        isDetecting = False
        enable_controls()
        result = result2Db(job_results)

        job_name = job.split('/')[1]
        print(f'Job[{job_name}] results count: {len(job_results)}')
        col1 = QStandardItem(f'{job_name}')
        col1.setToolTip(f'{job_name}')
        col1.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        
        beam_code = result['beam_code']
        col2 = QStandardItem()
        col2.setToolTip(beam_code)
        col2.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        bubble_num = str(result['bubble_num'])
        col3 = QStandardItem(bubble_num)
        col3.setToolTip(bubble_num)
        col3.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        crack_num = str(result['crack_num'])
        col4 = QStandardItem(crack_num)
        col4.setToolTip(crack_num)
        col4.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        ui.resultModel.appendRow([col1,col2,col3,col4])
        

    # ch:关闭设备 | Close device
    def close_device():
        global isOpen
        global isDetecting
        # global obj_cam_operation

        if isOpen and len(ui.ComboDevices.selected_items) > 0:
            for cameraIndex in ui.ComboDevices.selected_items:
            # for cameraIndex in range(0, SysDevice.m_DeviceNum):
                device = SysDevice.m_Device[cameraIndex]
                device.stopGrabbing()
                device.closeDevice()
            # SysDevice.unInitSystem()
            isOpen = False
            ui.pictureView.clear()

        # isDetecting = False

            enable_controls()
        else:
            # TODO: 勾选提醒
            QMessageBox.information(ui.centralwidget,"消息提醒","请确认已选择对应相机！",QMessageBox.Ok|QMessageBox.Cancel,QMessageBox.Ok)
            pass
    
    def close_all_device():
        for cameraIndex in range(0, SysDevice.m_DeviceNum):
            device = SysDevice.m_Device[cameraIndex]
            device.stopGrabbing()
            device.closeDevice()
        # SysDevice.unInitSystem()

    def tree():
        print(f'tree view')

    def list_models(model_path):
        all_models = []
        for root,dirs,files in os.walk(model_path):
            for file in list(filter((lambda x: x.lower().endswith('.pt')),files)):
                all_models.append(file)
        return all_models
    
    # ch: 设置控件状态 | en:set enable status
    def enable_controls():
        global isDetecting
        global isOpen

        # 先设置group的状态，再单独设置各控件状态
        # ui.groupDetect.setEnabled(isOpen)
        # ui.groupParam.setEnabled(isOpen)

        ui.bnOpen.setEnabled(not isOpen)
        ui.bnClose.setEnabled(isOpen and (not isDetecting))

        ui.ComboModels.setEnabled((not isOpen) or (not isDetecting))
        ui.bnStart.setEnabled(isOpen and (not isDetecting))
        ui.bnStop.setEnabled(isOpen and isDetecting)
        # ui.bnSoftwareTrigger.setEnabled(isDetecting and ui.radioTriggerMode.isChecked())

        # ui.bnSaveImage.setEnabled(isOpen and isDetecting)

    global cam
    cam = MvCamera()
    global nSelCamIndex
    nSelCamIndex = 0
    global obj_cam_operation
    obj_cam_operation = 0
    global isOpen
    isOpen = False
    global isDetecting
    isDetecting = False
    global isCalibMode  # 是否是标定模式（获取原始图像）
    isCalibMode = True
    

    # ch: 初始化app, 绑定控件与函数 | en: Init app, bind ui and api
    app = QApplication(sys.argv)
    mainWindow = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(mainWindow)

    ui.ComboModels.addItems(list_models('models'))
    
    ui.bnEnum.clicked.connect(enum_devices)
    ui.bnOpen.clicked.connect(open_device)
    ui.bnClose.clicked.connect(close_device)
    ui.bnStart.clicked.connect(start_detecting)
    ui.bnStop.clicked.connect(stop_detecting)

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
 
    # print(ui.ComboModels.currentText())
    

    mainWindow.show()

    app.exec_()

    close_all_device()
    sys.exit()
