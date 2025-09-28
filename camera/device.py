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
    print("Idx  Type   Vendor              Model           S/N                 DeviceUserID    IP Address")
    print("------------------------------------------------------------------------------------------------")
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
        print ("[%d]  %s   %s    %s      %s     %s           %s" % (i+1, strType,strVendorName,strModeName,strSerialNumber,strCameraname,strIpAdress))

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
                print("Create devHandle failed! ErrorCode", nRet)
                return nRet

            # 打开相机
            nRet = self.obj_cam.IMV_Open()
            if IMV_OK != nRet:
                print("Open devHandle failed! ErrorCode", nRet)
                self.obj_cam.IMV_DestroyHandle()
                return nRet
            else:
                print(f"open device[{self.m_index}] successfully!")
                self.b_open_device = True
                self.b_thread_closed = False
            return IMV_OK

    def openDevicebyKey(self):
        if not self.b_open_device:
            self.obj_cam = MvCamera()
            nRet = self.obj_cam.IMV_CreateHandle(IMV_ECreateHandleMode.modeByCameraKey, self.m_Key)
            if IMV_OK != nRet:
                print("Create devHandle failed! ErrorCode", nRet)
                return nRet

            # 打开相机
            nRet = self.obj_cam.IMV_Open()
            if IMV_OK != nRet:
                print("Open devHandle failed! ErrorCode", nRet)
                self.obj_cam.IMV_DestroyHandle()
                return nRet
            else:
                print(f"open device[{self.m_index}] successfully!")
                self.b_open_device = True
                self.b_thread_closed = False
            return IMV_OK
            
        # if not self.b_open_device:
        #     self.obj_cam = MvCamera()
        #     nRet = self.obj_cam.IMV_CreateHandle(IMV_ECreateHandleMode.modeByCameraKey, self.m_Key)
        #     if IMV_OK != nRet:
        #         print("Create devHandle by CameraKey failed! Key is [%s], ErrorCode[%d]", self.m_Key, nRet)
        #         sys.exit()

        #     # 打开相机
        #     nRet = self.obj_cam.IMV_Open()
        #     if IMV_OK != nRet:
        #         print("Open devHandle failed! ErrorCode", nRet)
        #         self.obj_cam.IMV_DestroyHandle()
        #     sys.exit()

        # return nRet

    def openDevicebyUserId(self):

        nRet = self.cam.IMV_CreateHandle(IMV_ECreateHandleMode.modeByDeviceUserID, self.m_userId.encode("ascii"))
        if IMV_OK != nRet:
            print("Create devHandle by device user id failed! User id is [%s], ErrorCode[%d]", self.m_userId, nRet)
            sys.exit()

        # 打开相机
        nRet = self.cam.IMV_Open()
        if IMV_OK != nRet:
            print("Open devHandle failed! ErrorCode", nRet)
            self.cam.IMV_DestroyHandle()
            sys.exit()

    def closeDevice(self):
        # # 关闭相机
        # nRet = self.cam.IMV_Close()
        # if IMV_OK != nRet:
        #     print("Close camera failed! ErrorCode", nRet)
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
        self.obj_cam.IMV_DestroyHandle()
        self.b_open_device = False
        self.b_start_grabbing = False
        # self.b_exit = True
        print("close device successfully!")

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
        #     print("Release frame failed! ErrorCode[%d]"% nRet)
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
                print("image convert to failed! ErrorCode[%d]" % nRet)
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

    def getFrameThreadProc(self,winHandle):
            frame = IMV_Frame()
            if self.obj_cam.handle == None:
                return IMV_INVALID_HANDLE
            count = 0
            while True:
                ret = self.obj_cam.IMV_ExecuteCommandFeature("TriggerSoftware")
                if ret != IMV_OK:
                    print("Execute TriggerSoftware failed! ErrorCode:",ret)
                    continue
                nRet = self.obj_cam.IMV_GetFrame(frame, 1000)
                if IMV_OK != nRet:
                    print(f'get fram failed with errorcode[{nRet}]')
                    # break
                    continue

                print("Get frame blockId = [%d]" % frame.frameInfo.blockId)
                # self.st_frame_info = frame.frameInfo

                pic = winHandle
                cvImage = self.convertImageByCv(cam=self.obj_cam,frame=frame)
                if not self.b_start_detecting:
                    # 显示图片
                    h, w, ch = cvImage.shape
                    qt_img = QImage(cvImage, # 数据源
                                h ,  # 宽度
                                w,	# 高度
                                ch * w, # 行字节数
                                QImage.Format_BGR888)
                    pic.setPixmap(QPixmap.fromImage(qt_img))
                    count = 0
                elif self.b_start_detecting and self.put_image:
                    # 保存图片，并加入待检测队列
                    global current_job
                    count += 1
                    deviceName = device_dic[self.m_userId.decode('utf-8')]
                    fileName = f"{current_job}/{deviceName}-{count}张.jpg"
                    print(f'picture image: [{fileName}]')
                    cv2.imencode('.jpg', cvImage)[1].tofile(fileName)
                    # self.image_queue.put((fileName,cvImage))
                    self.image_queue.put(fileName)
                
                # image = Image.fromarray(cvImage)  
                # pic.setImage(cv2.cvtColor(cvImage,cv2.COLOR_BayerBG))
                # pic.setImage(cvImage)
                # pic.setImage(numpy.array(image))
                # time.sleep(10)
                nRet = self.obj_cam.IMV_ReleaseFrame(frame)
                if IMV_OK != nRet:
                    print("Release frame failed! ErrorCode[%d]" % nRet)
                
                # 是否退出
                if not self.b_start_grabbing:
                    # if self.buf_save_image is not None:
                    #     del self.buf_save_image
                    break
                time.sleep(2)
            # return IMV_OK

    def startGrabbing(self,winHandle):
        if not self.obj_cam.handle:
            return IMV_INVALID_HANDLE
        
        if not self.b_start_grabbing and self.b_open_device:
            # self.b_exit = False
            ret = self.obj_cam.IMV_StartGrabbing()
            if ret != IMV_OK:
                print(f"start grabbing camera[{self.m_index}] failed with errorcode [{ret}]!")
            else:
                print(f"start grabbing camera[{self.m_index}] successfully!")
                self.b_start_grabbing = True
            # return ret
        
            try:
                thread_id = self.m_index
                self.h_thread_handle = threading.Thread(target=CameraDevice.getFrameThreadProc, args=(self, winHandle))
                print(f'starting thread: {self.h_thread_handle}')
                self.h_thread_handle.start()
                self.b_thread_closed = True
            except Exception as e:
                print(f"error: unable to start thread with error [{e}]")
        # return MV_E_CALLORDER
        

    def stopGrabbing(self):
        if not self.obj_cam.handle:
            return IMV_INVALID_HANDLE
        
        # self.b_start_grabbing = False
        # self.b_exit = True
        # return self.cam.IMV_StopGrabbing()
    

        if self.b_start_grabbing and self.b_open_device:
            # 退出线程
            if self.b_thread_closed:
                Stop_thread(self.h_thread_handle)
                self.b_thread_closed = False
            ret = self.obj_cam.IMV_StopGrabbing()
            if ret != 0:
                print(f"stop grabbing camera[{self.m_index}] failed with errorcode [{ret}]!")
                return ret
            print(f"stop grabbing camera[{self.m_index}] successfully!")
            self.b_start_grabbing = False
            # self.b_exit = True
            return IMV_OK
        else:
            IMV_E_CALLORDER                               = 0x80000003  # < \~chinese 函数调用顺序错误         \~english Function calling order error
            return IMV_E_CALLORDER

    def detect(self,model,job,job_lock,job_results,winHandle):
        global current_job
        global current_device_results
        current_job = job
        current_device_results = []
        
        while True:
            image = self.image_queue.get()
            print(f'detect  image: [{image}]')
            # cv2.imencode('.jpg', image[1])[1].tofile(image[0])
            # results = detectFrame(model,job,image[0])
            results = detectFrame(model,job,image)
            current_device_results.extend(results)

            # for result in results:
            plot_result = results[0].plot()

            pic = winHandle
            h, w, ch = plot_result.shape
            qt_img = QImage(plot_result, # 数据源
                        h ,  # 宽度
                        w,	# 高度
                        ch * w, # 行字节数
                        QImage.Format_BGR888)
            pic.setPixmap(QPixmap.fromImage(qt_img))
            # 发送当前图像已检测信号
            self.image_queue.task_done()
            # # 等待4s测试消费速度小于生产速度的情景
            # time.sleep(4)

            # 是否退出
            if not self.b_start_detecting:
                # if self.buf_save_image is not None:
                #     del self.buf_save_image
                self.b_start_detecting = False
                break
        # return IMV_OK


    def startDetecting(self,model,job,job_lock,job_results,winHandle):
        if not self.obj_cam.handle:
            return IMV_INVALID_HANDLE
        
        if not self.b_start_detecting and self.b_start_grabbing:
            # self.b_exit = False
            # ret = self.obj_cam.IMV_StartGrabbing()
            # if ret != IMV_OK:
            #     print(f"start grabbing camera[{self.m_index}] failed with errorcode [{ret}]!")
            # else:
            #     print(f"start grabbing camera[{self.m_index}] successfully!")
            #     self.b_start_grabbing = True
            # # return ret
            self.b_start_detecting = True
            self.put_image = True
            try:
                thread_id = self.m_index
                self.h_thread_handle_detect = threading.Thread(target=CameraDevice.detect, args=(self, model, job, job_lock, job_results, winHandle))
                print(f'starting thread: {self.h_thread_handle_detect}')
                self.h_thread_handle_detect.start()
                self.b_thread_closed_detect = True
            except Exception as e:
                print(f"error: unable to start thread with error [{e}]")
        
        pass
    
    def stopDetecting(self,job,job_lock,job_results,winHandle):
        if not self.obj_cam.handle:
            return IMV_INVALID_HANDLE
    
        if self.b_start_detecting and self.b_start_grabbing:
            self.put_image = False
            print(f'---------------------本次检测任务停止中----------------------------')
            while not self.image_queue.empty():
                print(f'剩余待检测图像：{self.image_queue.qsize()}张，等待本次检测完成..................')
                time.sleep(2)
                continue
            # 阻塞等待队列中所有图像检测完成
            self.image_queue.join()
            # 退出线程
            print(f'---------------------本次检测任务完成------------------------------')
            job_lock.acquire()
            job_results.extend(current_device_results)
            job_lock.release()
            # self.put_image = False
            if self.b_thread_closed_detect:
                Stop_thread(self.h_thread_handle_detect)
                self.b_thread_closed_detect = False
            self.b_start_detecting = False
            # self.b_exit = True
            return IMV_OK
        else:
            IMV_E_CALLORDER                               = 0x80000003  # < \~chinese 函数调用顺序错误         \~english Function calling order error
            return IMV_E_CALLORDER

    
    def stopGrabbingCallback(self):
        if not self.cam.handle:
            return IMV_INVALID_HANDLE

        return self.cam.IMV_StopGrabbing()

    def startGrabbingCallback(self):
        if not self.cam.handle:
            return IMV_INVALID_HANDLE

        ret = self.obj_cam.IMV_AttachGrabbing(CALL_BACK_FUN,None)
        if ret != IMV_OK:
            print("IMV_AttachGrabbing failed. ret:%d"% ret)

        return self.cam.IMV_StartGrabbing()

    pFrame = POINTER(IMV_Frame)
    FrameInfoCallBack = eval('CFUNCTYPE')(None, pFrame, c_void_p)

    def onGetFrame(pFrame,pUser):
        if pFrame == None:
            print("pFrame is None!")
            return
        Frame = cast(pFrame, POINTER(IMV_Frame)).contents

        print("Get frame blockID = ", Frame.frameInfo.blockId)
        return

    CALL_BACK_FUN = FrameInfoCallBack(onGetFrame)
    
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
    #     print (deviceStr)
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
            print("Enumeration devices failed! ErrorCode", nRet)
            sys.exit()
        if deviceList.nDevNum == 0:
            print("find no device!")
            sys.exit()

        self.m_DeviceNum = deviceList.nDevNum
        for i in range(0,deviceList.nDevNum):
            self.m_Device[i].init(i,deviceList.pDevInfo[i])
            self.m_DeviceStr.append(self.getDeviceInfo(i,deviceList.pDevInfo[i]))

        print("deviceList size is", deviceList.nDevNum)
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
        print (deviceStr)
        return deviceStr