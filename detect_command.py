# -- coding: utf-8 --

import time
import time
from camera.device import *
from ctypes import *
from camera.picture_thred import *
import argparse

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

    return nRet


# python detect_main.py --mode track
parser = argparse.ArgumentParser()
parser.add_argument("-m", "--mode", default='detect', help="检测模式：track、detect")
args = parser.parse_args()

if __name__ == "__main__":

    print(c_char_p(0))

    SysDevice = DeviceSystem()
    SysDevice.initSystem()
    threads = []
    images = {}
    image_queue = queue.Queue()
    job = f'mark_pics/job_{time.strftime("%Y-%m-%d_%H点%M分%S秒", time.localtime())}'
    
    for cameraIndex in range(0, SysDevice.m_DeviceNum):
        device = SysDevice.m_Device[cameraIndex]
        ret = device.openDevicebyKey()
        if ret != IMV_OK:
            print("open camera[%d] failed[%d]"% (cameraIndex, ret))
            break

        # width = c_int(0)
        # ret = SysDevice.m_Device[cameraIndex].getIntValue("Width", width)
        # if ret != IMV_OK:
        #     print("getIntValue camera[%d] failed[%d]"% (cameraIndex, ret))
        #     break

        # ret = SysDevice.m_Device[cameraIndex].setIntValue("Width", width.value)
        # if ret != IMV_OK:
        #     print("setIntValue camera[%d] failed[%d]"% (cameraIndex, ret))
        #     break

        setSoftTriggerConf(device.cam)

        ret = device.startGrabbing()
        if ret != IMV_OK:
            print("start grabbing camera[%d] failed[%d]"% (cameraIndex, ret))
            break

        try:
            thread = pictureThread(cameraIndex, device.m_userId.decode('utf-8'), device, job, image_queue)
            thread.start()
            threads.append(thread)
        except:
            print(f"error: unable to start thread {thread.name}")
    
    time.sleep(5)
    # if cv2.waitKey(1) & 0xFF == ord("q"):
    #     for thread in threads:
    #         images.update(thread.pictured_images)
    #         thread.g_isExitThread = True
    #         thread.join()
    #         ret = thread.device.stopGrabbing()
    #         if ret != IMV_OK:
    #             print("stop grabbing camera[%d] failed[%d]"% (thread.device.m_userId, ret))
    #             break
    #         thread.device.closeDevice()
    
    # SysDevice.unInitSystem()
    
    for thread in threads:
        images.update(thread.pictured_images)
        thread.g_isExitThread = True
        thread.join()
        ret = thread.device.stopGrabbing()
        if ret != IMV_OK:
            print("stop grabbing camera[%d] failed[%d]"% (thread.device.m_userId, ret))
            break
        thread.device.closeDevice()
    
    SysDevice.unInitSystem()

    from task.detect_image import detect, track
    if args.mode == 'track':
        fps = 24
        width = 5120
        height = 5120
        # video = cv2.VideoWriter('ss.mp4', cv2.VideoWriter_fourcc(*"mp4v"), fps, (width,height)) #创建视频流对象-格式一
        if not os.path.exists(f'{job}'):
            os.makedirs(f'{job}')
        video = cv2.VideoWriter(f'{job}/beam-body.avi', cv2.VideoWriter_fourcc('I','4','2','0'), fps, (width,height)) #创建视频流对象-格式一
        for name,img in images.items():
            video.write(img)  # 向视频文件写入一帧--只有图像，没有声音
        track(source=f'{job}')
        # cv2.waitKey()
    else:
        
        if not os.path.exists(f'{job}'):
            os.makedirs(f'{job}')
        for name,img in images.items():
            # todo: fileName
            cv2.imencode('.jpg', img)[1].tofile(name)
        detect(source=job)

    
    print(f'{job} 检测完成')