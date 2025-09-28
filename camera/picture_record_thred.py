# -- coding: utf-8 --

import threading
import time
import sys
import time
import threading
from camera.device import *
import numpy
# import cv2
import os
# from ctypes import *

device_dic = {'xy-01-01':'1面-1排',
              'xy-01-02':'1面-2排',
              'xy-01-03':'1面-3排',
              'xy-02-01':'2面-1排',
              'xy-02-02':'2面-2排',
              'xy-02-03':'2面-3排'}
exitFlag = 0

def saveImageByCv(cam,frame,fileName):
    stPixelConvertParam=IMV_PixelConvertParam()

    if  None==byref(frame) :
        print("pFrame is NULL!")
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
    #     print("Release frame failed! ErrorCode[%d]\n", nRet)
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
        # convert to BGR24
        stPixelConvertParam.eDstPixelFormat=IMV_EPixelType.gvspPixelBGR8
        #stPixelConvertParam.nDstBufSize=nDstBufSize

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
            pass
    # --- end if ---
    # # cv2.imshow('myWindow', cvImage)
    # t1 = time.time()
    # # cv2.imwrite('fileName.png', cvImage)
    # height = cvImage.shape[0]
    # cv2.imencode('.jpg', cvImage)[1].tofile(fileName)
    # t2 = time.time()
    # print('运行时间:%s毫秒' % ((t2 - t1) * 1000))
    # # gc.collect()
    return cvImage

class pictureThread (threading.Thread):
    def __init__(self, threadID, name, device, job):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.job = job
        self.g_isExitThread = False
        self.device = device
        self.pictured_images = []
    def run(self):
        print ("开启线程：" + self.name)
        self.picture()
        print ("退出线程：" + self.name)

    def picture(self):
        devHandle = self.device.cam.handle
        frame = IMV_Frame()
        if None == devHandle:
            return

        pictureOrder = 0
        while not self.g_isExitThread:
            ret = self.device.cam.IMV_ExecuteCommandFeature("TriggerSoftware")
            if ret != IMV_OK:
                print("Execute TriggerSoftware failed! ErrorCode:",ret)
                continue

            self.device.getFrame(frame, 500)

            pictureOrder += 1
            
            # 图片保存路径
            if not os.path.exists(f'{self.job}'):
                os.makedirs(f'{self.job}')
            deviceName = device_dic[self.device.m_userId.decode('utf-8')]
            fineName = f"{self.job}/{deviceName}-{pictureOrder}张.jpg"
            print(f'fineName: {fineName}')
            image = saveImageByCv(self.device.obj_cam, frame, fineName)
            self.pictured_images.append(image)
            self.device.releaseFrame(frame)

            #通过睡眠时间来调节帧率(单位/秒)
            time.sleep(2)
