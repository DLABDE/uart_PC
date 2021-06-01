#_*_coding:utf-8_*_

import pyqtgraph as pg
import array
import serial
import threading
import numpy as np
from queue import Queue
import re,keyboard
import serial.tools.list_ports

ti=0
#缓存通道
back_t = Queue(maxsize=0)
tar_t=Queue(maxsize=0)

historyLength = 150  # 横坐标长度
#缓存输出区
data_back= array.array('i')  # 可动态改变数组的大小,double型数组
data_tar = array.array('i')
data_back = np.zeros(historyLength).__array__('d')  # 把数组长度定下来
data_tar = np.zeros(historyLength).__array__('d')

def face_print():
    print("#"*10,'串口上位机调试','#'*10)
    usblist = list_usb()
    if (len(usblist) > 1):
        com = input('输入想链接的串口：')
        bsp = input('串口波特率:')
        ser = conect_usb(com, bsp)
    else:
        ser = conect_usb(str(usblist[0])[:4], 115200)
    return ser

#串口列表查询与返回
def list_usb():
    try:
        port_list = list(serial.tools.list_ports.comports())
        if len(port_list) == 0:
            print('无可用串口！')
            return 1
        else:
            print('可用串口列表如下：')
            for i in range(0, len(port_list)):
                print(port_list[i])
        return (port_list)
    except Exception as e:
        print("串口异常",e)
        pass
#串口链接，返回串口对象
def conect_usb(portx,bps):
    timex = 0.5
    try:
        ser = serial.Serial(portx, bps, timeout=timex)# 打开串口，并得到串口对象
        print('串口链接成功！--',ser.port)
        return ser
    except Exception as e:
        print("---串口异常---：", e)
#关闭串口
def exitusb(ser):
    ser.close()  # 关闭串口
    print('串口以关闭--',ser.port)
#读取一行串口数据
def usbline(ser):
    return str(ser.readline(), 'ascii').replace('\n', '').split(';')

#获取串口数据并写缓存通道
def Serial():
    global back_t,tar_t
    pattern = '\S+='
    while (True):
        n = ser.inWaiting()
        if (n):
            try:
                dat = usbline(ser)
                for i in dat:
                    the_re = re.compile(pattern)
                    match = re.search(the_re, i)
                    var = match.group(0)[:-1]
                    if var == 'back':
                        back_t.put(int(i.replace(match.group(0), '')))
                    if var == 'target':
                        tar_t.put(int(i.replace(match.group(0), '')))
            except Exception as e:
                #print("读取异常",e)
                pass


#更新输出区，并绘制
h = 0
def plotData():
    global h
    if h < historyLength:
        data_back[h] = back_t.get()
        data_tar[h] = tar_t.get()
        h = h+1
    else:
        data_back[:-1] = data_back[1:]
        data_back[h-1] = back_t.get()

        data_tar[:-1] = data_tar[1:]
        data_tar[h - 1] = tar_t.get()
    curve_back.setData(data_back)
    curve_tar.setData(data_tar)


if __name__ == "__main__":
    ser = face_print()
    while (1):
        print('\n0.退出该串口')
        print('1.显示波形')
        k = int(input('选项：'))
        if (0 == k):
            exitusb(ser)
            ser = face_print()
        elif (1 == k):
            app = pg.mkQApp()  # 建立app
            win = pg.GraphicsWindow()  # 建立窗口
            #win.setWindowTitle(u'pyqtgraph逐点画波形图')
            #win.resize(800, 500)  # 小窗口大小
            p = win.addPlot()  # 把图p加入到窗口中
            p.showGrid(x=True, y=True)  # 把X和Y的表格打开
            curve_back = p.plot()  # 绘制一个图形
            curve_tar = p.plot()  # 绘制一个图形

            th1 = threading.Thread(target=Serial)#打开串口读取线程
            th1.start()

            timer = pg.QtCore.QTimer()
            timer.timeout.connect(plotData)  # 定时刷新数据显示
            timer.start(ti)  # 多少ms调用一次
            app.exec_()

        elif (2 == k):
            pass
