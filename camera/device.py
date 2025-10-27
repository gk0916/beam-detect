# -- coding: utf-8 --

import sys
import time
import threading
import inspect
import numpy
import cv2
from multiprocessing import JoinableQueue
from PyQt5.QtGui import QPixmap, QImage
# from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QLabel
# from PIL import Image
from task.detect_image import detectFrame

# sys.path.append("./MVSDK")
from camera.MVSDK.IMVApi import *
import yaml
import logging
from queue import Empty

device_dic = {'xy-01-01':'1面-1排',
              'xy-01-02':'1面-2排',
              'xy-01-03':'1面-3排',
              'xy-02-01':'2面-1排',
              'xy-02-02':'2面-2排',
              'xy-02-03':'2面-3排'}

def Async_raise(tid, exctype):
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")

# 停止线程
def Stop_thread(thread):
    Async_raise(thread.ident, SystemExit)

def displayDeviceInfo(deviceInfoList):
    logging.info("Idx  Type   Vendor              Model           S/N                 DeviceUserID    IP Address")
    logging.info("------------------------------------------------------------------------------------------------")
    for i in range(0,deviceInfoList.nDevNum):
        pDeviceInfo=deviceInfoList.pDevInfo[i]
        strType=""
        strVendorName = pDeviceInfo.vendorName.decode("ascii")
        strModeName = pDeviceInfo.modelName.decode("ascii")
        strSerialNumber = pDeviceInfo.serialNumber.decode("ascii")
        strCameraname = pDeviceInfo.cameraName.decode("ascii")
        strIpAdress = pDeviceInfo.DeviceSpecificInfo.gigeDeviceInfo.ipAddress.decode("ascii")
        if pDeviceInfo.nCameraType == typeGigeCamera:
            strType="Gige"
        elif pDeviceInfo.nCameraType == typeU3vCamera:
            strType="U3V"
        logging.info ("[%d]  %s   %s    %s      %s     %s           %s" % (i+1, strType,strVendorName,strModeName,strSerialNumber,strCameraname,strIpAdress))

class CameraDevice():
    def __init__(self
                 , obj_cam=None
                # , st_device_list=None
                # , n_connect_num=0
                , b_open_device=False
                , b_start_grabbing=False
                , b_start_detecting=False,
                #  st_frame_info=None, b_save_bmp=False, b_save_jpg=False,
                #  buf_save_image=None,
                #  n_save_image_size=0, n_win_gui_id=0, frame_rate=0, exposure_time=0, gain=0
                 ):
        self.m_index = 0xff
        self.m_Key = ""
        self.m_userId = ""
        self.camInfo = None

        
        self.obj_cam = obj_cam
        # self.st_device_list = st_device_list
        # self.n_connect_num = n_connect_num
        self.b_open_device = b_open_device
        self.b_start_grabbing = b_start_grabbing
        self.b_start_detecting = b_start_detecting
        # self.st_frame_info = st_frame_info
        # self.b_save_bmp = b_save_bmp
        # self.b_save_jpg = b_save_jpg
        # self.buf_save_image = buf_save_image
        # self.n_save_image_size = n_save_image_size

        # self.b_exit = False
        self.h_thread_handle = None
        self.b_thread_closed = False
        self.h_thread_handle_detect = None
        self.b_thread_closed_detect = False
        self.image_queue = JoinableQueue()
        self.put_image = False
        self.stop_grab_event = threading.Event()
        self.stop_detect_event = threading.Event()
        
        # self.frame_rate = frame_rate
        # self.exposure_time = exposure_time
        # self.gain = gain
        self.buf_lock = threading.Lock()  # 取图和存图的buffer锁

    def init(self,index,camInfo):
        self.m_index = index
        self.m_Key = camInfo.cameraKey
        self.m_userId = camInfo.cameraName
        self.camInfo = camInfo
        return IMV_OK

    def openDevice(self):
        if not self.b_open_device:
            self.obj_cam = MvCamera()
            nRet = self.obj_cam.IMV_CreateHandle(IMV_ECreateHandleMode.modeByIndex, byref(c_void_p(self.m_index)))
            if IMV_OK != nRet:
                logging.error(f"Create devHandle failed! ErrorCode {nRet}")
                return nRet

            # 打开相机
            nRet = self.obj_cam.IMV_Open()
            if IMV_OK != nRet:
                logging.error(f"Open devHandle failed! ErrorCode {nRet}")
                self.obj_cam.IMV_DestroyHandle()
                return nRet
            else:
                logging.info(f"open device[{self.m_index}] successfully!")
                self.b_open_device = True
                self.b_thread_closed = False
            return IMV_OK

    def openDevicebyKey(self):
        if not self.b_open_device:
            self.obj_cam = MvCamera()
            nRet = self.obj_cam.IMV_CreateHandle(IMV_ECreateHandleMode.modeByCameraKey, self.m_Key)
            if IMV_OK != nRet:
                logging.error(f"Create devHandle failed! ErrorCode {nRet}")
                return nRet

            # 打开相机
            nRet = self.obj_cam.IMV_Open()
            if IMV_OK != nRet:
                logging.error(f"Open devHandle failed! ErrorCode {nRet}")
                self.obj_cam.IMV_DestroyHandle()
                return nRet
            else:
                logging.info(f"open device[{self.m_index}] successfully!")
                self.b_open_device = True
                self.b_thread_closed = False
            return IMV_OK
            
        # if not self.b_open_device:
        #     self.obj_cam = MvCamera()
        #     nRet = self.obj_cam.IMV_CreateHandle(IMV_ECreateHandleMode.modeByCameraKey, self.m_Key)
        #     if IMV_OK != nRet:
        #         logging.error("Create devHandle by CameraKey failed! Key is [%s], ErrorCode[%d]", self.m_Key, nRet)
        #         sys.exit()

        #     # 打开相机
        #     nRet = self.obj_cam.IMV_Open()
        #     if IMV_OK != nRet:
        #         logging.error(f"Open devHandle failed! ErrorCode {nRet}")
        #         self.obj_cam.IMV_DestroyHandle()
        #     sys.exit()

        # return nRet

    def openDevicebyUserId(self):

        nRet = self.cam.IMV_CreateHandle(IMV_ECreateHandleMode.modeByDeviceUserID, self.m_userId.encode("ascii"))
        if IMV_OK != nRet:
            logging.error("Create devHandle by device user id failed! User id is [%s], ErrorCode[%d]", self.m_userId, nRet)
            sys.exit()

        # 打开相机
        nRet = self.cam.IMV_Open()
        if IMV_OK != nRet:
            logging.error(f"Open devHandle failed! ErrorCode {nRet}")
            self.cam.IMV_DestroyHandle()
            sys.exit()

    def closeDevice(self):
        # # 关闭相机
        # nRet = self.cam.IMV_Close()
        # if IMV_OK != nRet:
        #     logging.error(f"Close camera failed! ErrorCode {nRet}")
        #     sys.exit()

        # # 销毁句柄
        # if (self.cam.handle):
        #     self.cam.IMV_DestroyHandle()

        if self.b_open_device:
            # 退出线程
            if self.b_thread_closed:
                Stop_thread(self.h_thread_handle)
                self.b_thread_closed = False
            if self.b_thread_closed_detect:
                Stop_thread(self.h_thread_handle_detect)
                self.b_thread_closed_detect = False
            ret = self.obj_cam.IMV_Close()
            if ret != 0:
                return ret

        # ch:销毁句柄 | Destroy handle
        if not self.obj_cam:
            return IMV_ERROR
        self.obj_cam.IMV_DestroyHandle()
        self.b_open_device = False
        self.b_start_grabbing = False
        # self.b_exit = True
        logging.info("close device successfully!")

        return IMV_OK
    
    def convertImageByCv(self,cam,frame):
        stPixelConvertParam=IMV_PixelConvertParam()

        # 给转码所需的参数赋值

        if IMV_EPixelType.gvspPixelMono8==frame.frameInfo.pixelFormat:
            nDstBufSize=frame.frameInfo.width * frame.frameInfo.height
        else:
            nDstBufSize=frame.frameInfo.width * frame.frameInfo.height*3
        
        pDstBuf=(c_ubyte*nDstBufSize)()
        memset(byref(stPixelConvertParam), 0, sizeof(stPixelConvertParam))
        
        stPixelConvertParam.nWidth = frame.frameInfo.width
        stPixelConvertParam.nHeight = frame.frameInfo.height
        stPixelConvertParam.ePixelFormat = frame.frameInfo.pixelFormat
        # GB8
        stPixelConvertParam.pSrcData = frame.pData
        stPixelConvertParam.nSrcDataLen = frame.frameInfo.size
        stPixelConvertParam.nPaddingX = frame.frameInfo.paddingX
        stPixelConvertParam.nPaddingY = frame.frameInfo.paddingY
        stPixelConvertParam.eBayerDemosaic = IMV_EBayerDemosaic.demosaicNearestNeighbor
        stPixelConvertParam.eDstPixelFormat = frame.frameInfo.pixelFormat
        stPixelConvertParam.pDstBuf = pDstBuf
        stPixelConvertParam.nDstBufSize = nDstBufSize
        
        # 释放驱动图像缓存
        # release frame resource at the end of use
        
        # nRet = cam.IMV_ReleaseFrame(frame)
        # if IMV_OK != nRet:
        #     logging.error(f"Release frame failed! ErrorCode[{nRet}]")
        #     sys.exit()
        
        # 如果图像格式是 Mono8 直接使用
        # no format conversion required for Mono8
        if stPixelConvertParam.ePixelFormat == IMV_EPixelType.gvspPixelMono8:
            imageBuff=stPixelConvertParam.pSrcData
            userBuff = c_buffer(b'\0', stPixelConvertParam.nDstBufSize)
        
            memmove(userBuff,imageBuff,stPixelConvertParam.nDstBufSize)
            grayByteArray = bytearray(userBuff)
            
            cvImage = numpy.array(grayByteArray).reshape(stPixelConvertParam.nHeight, stPixelConvertParam.nWidth)
            
        else:
            # 转码 => BGR24
            stPixelConvertParam.eDstPixelFormat=IMV_EPixelType.gvspPixelBGR8
            stPixelConvertParam.nDstBufSize=nDstBufSize

            nRet=cam.IMV_PixelConvert(stPixelConvertParam)
            if IMV_OK!=nRet:
                logging.error(f"image convert to failed! ErrorCode[{nRet}]")
                del pDstBuf
                sys.exit()
            rgbBuff = c_buffer(b'\0', stPixelConvertParam.nDstBufSize)
            memmove(rgbBuff,stPixelConvertParam.pDstBuf,stPixelConvertParam.nDstBufSize)
            colorByteArray = bytearray(rgbBuff)
            cvImage = numpy.array(colorByteArray).reshape(stPixelConvertParam.nHeight, stPixelConvertParam.nWidth, 3)
            if None!=pDstBuf:
                del pDstBuf
        # cv2.imshow('myWindow', cvImage)
        # cv2.imwrite('fileName.jpg', cvImage)

        # if (cv2.waitKey(1) >= 0):
        #     return
        
        # cvImage = cv2.cvtColor(cvImage,cv2.COLOR_BGR2RGB)
        return cvImage

    def getFrameThreadProc(self, winHandle):
        frame = IMV_Frame()
        if self.obj_cam.handle is None:
            return IMV_INVALID_HANDLE

        logging.info("Frame thread started.")
        count = 0
        while not self.stop_grab_event.is_set():
            ret = self.obj_cam.IMV_ExecuteCommandFeature("TriggerSoftware")
            if ret != IMV_OK:
                logging.error(f"Execute TriggerSoftware failed! ErrorCode: {ret}")
                time.sleep(0.1)
                continue

            nRet = self.obj_cam.IMV_GetFrame(frame, 1000)
            if IMV_OK != nRet:
                logging.error(f'get frame failed with errorcode[{nRet}]')
                # 不立即 break，继续重试
                time.sleep(0.05)
                continue

            logging.info(f"Get frame blockId = [{frame.frameInfo.blockId}]")

            cvImage = self.convertImageByCv(cam=self.obj_cam, frame=frame)
            if cvImage is None:
                logging.error("convertImageByCv returned None")
            else:
                # cvImage.shape -> (h, w, ch)
                h, w, ch = cvImage.shape
                # 当不检测时直接显示
                if not self.b_start_detecting:
                    # 显示图片
                    qt_img = QImage(cvImage.data, w, h, ch * w, QImage.Format_BGR888)
                    winHandle.setPixmap(QPixmap.fromImage(qt_img))
                    count = 0
                elif self.b_start_detecting and self.put_image:
                    # 保存图片，并加入待检测队列
                    count += 1
                    try:
                        deviceName = device_dic[self.m_userId.decode('utf-8')]
                    except Exception:
                        deviceName = str(self.m_userId)
                    fileName = f"{current_job}/{deviceName}-{count}张.jpg"
                    logging.debug(f'picture image: [{fileName}]')
                    # 使用 imencode 并写入文件
                    cv2.imencode('.jpg', cvImage)[1].tofile(fileName)
                    # 只放文件名到队列，避免共享大型数组
                    self.image_queue.put(fileName)

            nRet = self.obj_cam.IMV_ReleaseFrame(frame)
            if IMV_OK != nRet:
                logging.error(f"Release frame failed! ErrorCode[{nRet}]")

            # 检查是否应该退出（通过事件）
            if self.stop_grab_event.is_set() or not self.b_start_grabbing:
                break
            # 适当 sleep，避免 100% 占用
            time.sleep(0.02)

        logging.info("Frame thread exiting.")
        return IMV_OK

    def startGrabbing(self, winHandle):
        if not self.obj_cam or not self.obj_cam.handle:
            return IMV_INVALID_HANDLE

        if not self.b_start_grabbing and self.b_open_device:
            ret = self.obj_cam.IMV_StartGrabbing()
            if ret != IMV_OK:
                logging.error(f"start grabbing camera[{self.m_index}] failed with errorcode [{ret}]!")
                return ret
            logging.info(f"start grabbing camera[{self.m_index}] successfully!")
            self.b_start_grabbing = True

            # 清理退出事件，启动线程（非 daemon）
            self.stop_grab_event.clear()
            try:
                self.h_thread_handle = threading.Thread(target=self.getFrameThreadProc, args=(winHandle,))
                # 不要把抓取线程设为 daemon（否则主线程退出时会被强制终止）
                self.h_thread_handle.daemon = False
                self.h_thread_handle.start()
                self.b_thread_closed = True
            except Exception as e:
                logging.error(f"error: unable to start thread with error [{e}]")
                return IMV_ERROR

        return IMV_OK

    def stopGrabbing(self, timeout=2.0):
        if not self.obj_cam or not self.obj_cam.handle:
            return IMV_INVALID_HANDLE

        if self.b_start_grabbing and self.b_open_device:
            # 请求线程退出：通过事件而非强杀
            if self.b_thread_closed and self.h_thread_handle is not None:
                logging.debug("Signaling grab thread to stop...")
                self.stop_grab_event.set()
                # 等待线程退出
                self.h_thread_handle.join(timeout=timeout)
                if self.h_thread_handle.is_alive():
                    logging.warning("grab thread did not exit within timeout")
                self.b_thread_closed = False

            ret = self.obj_cam.IMV_StopGrabbing()
            if ret != 0:
                logging.error(f"stop grabbing camera[{self.m_index}] failed with errorcode [{ret}]!")
                return ret
            logging.info(f"stop grabbing camera[{self.m_index}] successfully!")
            self.b_start_grabbing = False
            return IMV_OK
        else:
            IMV_E_CALLORDER = 0x80000003
            return IMV_E_CALLORDER

    # 检测线程：消费队列并处理图片
    def detect(self, model, job, job_lock, job_results, winHandle):
        global current_job
        global current_device_results
        current_job = job
        logging.info("Detect thread started.")
        current_device_results = []

        while not self.stop_detect_event.is_set() and self.b_start_detecting:
            try:
                # 使用 timeout 防止在退出时永久阻塞
                image_path = self.image_queue.get(timeout=1.0)
            except Empty:
                continue

            if image_path is None:
                logging.debug("Detect thread received sentinel None, exiting loop...")
                self.image_queue.task_done()
                break

            logging.debug(f'detect  image: [{image_path}]')
            try:
                results = detectFrame(model, job, image_path)
            except Exception as e:
                logging.exception(f"detectFrame failed: {e}")
                self.image_queue.task_done()
                continue

            current_device_results.extend(results)

            # 绘图并显示（注意 QImage 参数顺序）
            try:
                plot_result = results[0].plot()
                h, w, ch = plot_result.shape
                qt_img = QImage(plot_result.data, w, h, ch * w, QImage.Format_BGR888)
                winHandle.setPixmap(QPixmap.fromImage(qt_img))
            except Exception as e:
                logging.exception(f"plot/display failed: {e}")

            self.image_queue.task_done()

        logging.info("Detect thread exiting.")
        return IMV_OK

    def startDetecting(self, model, job, job_lock, job_results, winHandle):
        if not self.obj_cam or not self.obj_cam.handle:
            return IMV_INVALID_HANDLE

        if not self.b_start_detecting and self.b_start_grabbing:
            self.b_start_detecting = True
            self.put_image = True
            self.stop_detect_event.clear()
            try:
                self.h_thread_handle_detect = threading.Thread(
                    target=self.detect,
                    args=(model, job, job_lock, job_results, winHandle)
                )
                self.h_thread_handle_detect.daemon = False
                self.h_thread_handle_detect.start()
                self.b_thread_closed_detect = True
            except Exception as e:
                logging.error(f"error: unable to start detect thread with error [{e}]")
                return IMV_ERROR

        return IMV_OK

    def stopDetecting(self, job, job_lock, job_results, winHandle, timeout=3.0):
        if not self.obj_cam or not self.obj_cam.handle:
            return IMV_INVALID_HANDLE

        if self.b_start_detecting and self.b_start_grabbing:

            # 停止继续放图
            self.put_image = False
            logging.info(f'---------------------本次检测任务停止中----------------------------')

            # 等待队列被消费完
            while not self.image_queue.empty():
                logging.info(f'剩余待检测图像：{self.image_queue.qsize()}张，等待本次检测完成..................')
                time.sleep(1)

            # 使用 join() 等待 detect() 完成所有 task_done
            logging.debug("Waiting for image_queue.join()...")
            try:
                self.image_queue.join()
            except Exception:
                pass

            # 发出线程退出信号
            logging.debug("Signaling detect thread to stop...")
            self.b_start_detecting = False
            self.stop_detect_event.set()

            # 放哨兵，让 detect() 从 queue.get() 退出
            try:
                self.image_queue.put_nowait(None)
            except Exception:
                pass

            # 等线程退出
            if self.b_thread_closed_detect and self.h_thread_handle_detect is not None:
                self.h_thread_handle_detect.join(timeout=timeout)
                if self.h_thread_handle_detect.is_alive():
                    logging.warning("detect thread did not exit within timeout")
                self.b_thread_closed_detect = False

            # 将结果汇总回 job_results
            logging.info(f'---------------------本次检测任务完成------------------------------')
            job_lock.acquire()
            job_results.extend(current_device_results)
            job_lock.release()

            return IMV_OK

        else:
            IMV_E_CALLORDER = 0x80000003
            return IMV_E_CALLORDER


    
    def stopGrabbingCallback(self):
        if not self.cam.handle:
            return IMV_INVALID_HANDLE

        return self.cam.IMV_StopGrabbing()

    def onGetFrame(pFrame,pUser):
        if pFrame == None:
            logging.warning("pFrame is None!")
            return
        Frame = cast(pFrame, POINTER(IMV_Frame)).contents

        logging.info(f"Get frame blockID = {Frame.frameInfo.blockId}")
        return
    
    pFrame = POINTER(IMV_Frame)
    FrameInfoCallBack = eval('CFUNCTYPE')(None, pFrame, c_void_p)
    CALL_BACK_FUN = FrameInfoCallBack(onGetFrame)
    
    def startGrabbingCallback(self):
        if not self.cam.handle:
            return IMV_INVALID_HANDLE

        ret = self.obj_cam.IMV_AttachGrabbing(CALL_BACK_FUN,None)
        if ret != IMV_OK:
            logging.error(f"IMV_AttachGrabbing failed. ret:{ret}")

        return self.cam.IMV_StartGrabbing()



    
    # def deviceInfo(self):
    #     index = self.m_index
    #     pDeviceInfo=self.camInfo
    #     strType=""
    #     strVendorName = pDeviceInfo.vendorName.decode("ascii")
    #     strModeName = pDeviceInfo.modelName.decode("ascii")
    #     strSerialNumber = pDeviceInfo.serialNumber.decode("ascii")
    #     strCameraname = pDeviceInfo.cameraName.decode("ascii")
    #     strIpAdress = pDeviceInfo.DeviceSpecificInfo.gigeDeviceInfo.ipAddress.decode("ascii")
    #     if pDeviceInfo.nCameraType == typeGigeCamera:
    #         strType="Gige"
    #     elif pDeviceInfo.nCameraType == typeU3vCamera:
    #         strType="U3V"
    #     deviceStr = "[%d]  %s   %s    %s      %s     %s           %s" % (index, strType,strVendorName,strModeName,strSerialNumber,strCameraname,strIpAdress)
    #     logging.info (deviceStr)
    #     return deviceStr

    def setIntValue(self,pFeatureName,intValue):
        if not self.cam.handle:
            return IMV_INVALID_HANDLE
        return self.cam.IMV_SetIntFeatureValue(pFeatureName, intValue)

    def getIntValue(self,pFeatureName,pIntValue):
        if not self.cam.handle:
            return IMV_INVALID_HANDLE
        return self.cam.IMV_GetIntFeatureValue(pFeatureName, pIntValue)

    def setBoolValue(self,pFeatureName,boolValue):
        if not self.cam.handle:
            return IMV_INVALID_HANDLE
        return self.cam.IMV_SetBoolFeatureValue(pFeatureName, boolValue)

    def getBoolValue(self,pFeatureName,boolValue):
        if not self.cam.handle:
            return IMV_INVALID_HANDLE
        return self.cam.IMV_GetBoolFeatureValue(pFeatureName, boolValue)

    def setDoubleValue(self,pFeatureName,doubleValue):
        if not self.cam.handle:
            return IMV_INVALID_HANDLE
        return self.cam.IMV_SetDoubleFeatureValue(pFeatureName, doubleValue)

    def getDoubleValue(self,pFeatureName,doubleValue):
        if not self.cam.handle:
            return IMV_INVALID_HANDLE
        return self.cam.IMV_GetDoubleFeatureValue(pFeatureName, doubleValue)

    def setStringValue(self,pFeatureName,pStringValue):
        if not self.cam.handle:
            return IMV_INVALID_HANDLE
        return self.cam.IMV_SetStringFeatureValue(pFeatureName, pStringValue)

    def getStringValue(self,pFeatureName,pStringValue):
        if not self.cam.handle:
            return IMV_INVALID_HANDLE
        return self.cam.IMV_GetStringFeatureValue(pFeatureName, pStringValue)

    def setEnumSymbol(self,pFeatureName,pStringValue):
        if not self.cam.handle:
            return IMV_INVALID_HANDLE
        return self.cam.IMV_SetEnumFeatureSymbol(pFeatureName, pStringValue)

    def getEnumSymbol(self,pFeatureName,pStringValue):
        if not self.cam.handle:
            return IMV_INVALID_HANDLE
        return self.cam.IMV_GetEnumFeatureSymbol(pFeatureName, pStringValue)

def testCameras():
    database_yaml = 'config/test-cameras.yaml'
    with open(file=database_yaml, mode='r', encoding='utf-8') as f:
        database_config = f.read()
        yaml_data = yaml.load(stream=database_config, Loader=yaml.FullLoader)
    cameras = yaml_data['cameras']

    return cameras

class DeviceSystem():

    def __init__(self):
        self.m_Device = [CameraDevice() for i in range(16)]
        self.m_DeviceStr = []
        self.m_DeviceNum = 0
    
    def initSystem(self):
        deviceList = IMV_DeviceList()
        interfaceType = IMV_EInterfaceType.interfaceTypeAll

        # 枚举设备
        nRet = MvCamera.IMV_EnumDevices(deviceList, interfaceType)
        if IMV_OK != nRet:
            logging.error(f"Enumeration devices failed! ErrorCode {nRet}")
            sys.exit()
        if deviceList.nDevNum == 0:
            logging.warning("find no device!")
            # sys.exit()

        self.m_DeviceNum = deviceList.nDevNum
        for i in range(0,deviceList.nDevNum):
            self.m_Device[i].init(i,deviceList.pDevInfo[i])
            self.m_DeviceStr.append(self.getDeviceInfo(i,deviceList.pDevInfo[i]))

        self.m_DeviceStr.extend(testCameras())
        logging.info(f"deviceList size: {deviceList.nDevNum}")
        # displayDeviceInfo(deviceList)

    def unInitSystem(self):
        self.m_Device = [0 for i in range(16)]

    def getDeviceInfo(self,index,pDeviceInfo):
        strType=""
        strVendorName = pDeviceInfo.vendorName.decode("ascii")
        strModeName = pDeviceInfo.modelName.decode("ascii")
        strSerialNumber = pDeviceInfo.serialNumber.decode("ascii")
        strCameraname = pDeviceInfo.cameraName.decode("ascii")
        strIpAdress = pDeviceInfo.DeviceSpecificInfo.gigeDeviceInfo.ipAddress.decode("ascii")
        if pDeviceInfo.nCameraType == typeGigeCamera:
            strType="Gige"
        elif pDeviceInfo.nCameraType == typeU3vCamera:
            strType="U3V"
        deviceStr = "[%d]  %s   %s    %s     %s    %s     %s" % (index, strType,strVendorName,strModeName,strSerialNumber,strCameraname,strIpAdress)
        logging.debug (deviceStr)
        return deviceStr