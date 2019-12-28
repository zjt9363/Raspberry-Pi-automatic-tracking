# coding:utf-8

# 加入摄像头模块，让小车实现自动循迹行驶
# 思路为：摄像头读取图像，进行二值化，将白色的赛道凸显出来
# 选择下方的一行像素，黑色为0，白色为255
# 找到白色值的中点
# 目标中点与标准中点（320）进行比较得出偏移量
# 根据偏移量来控制小车左右轮的转速
# 考虑了偏移过多失控->停止;偏移量在一定范围内->高速直行(这样会速度不稳定，已删)

import RPi.GPIO as gpio
import time
import cv2
import numpy as np

# 定义引脚
pin1 = 13
pin2 = 26
pin3 = 5
pin4 = 20
pin5 =19
pin6 =16
pin7 =6
pin8 =21
# 设置GPIO口为BOARD编号规范
gpio.setmode(gpio.BCM)

# 设置GPIO口为输出
gpio.setup(pin1, gpio.OUT)
gpio.setup(pin2, gpio.OUT)
gpio.setup(pin3, gpio.OUT)
gpio.setup(pin4, gpio.OUT)
gpio.setup(pin5, gpio.OUT)
gpio.setup(pin6, gpio.OUT)
gpio.setup(pin7, gpio.OUT)
gpio.setup(pin8, gpio.OUT)
# 设置PWM波,频率为500Hz
pwm1 = gpio.PWM(pin1, 500)
pwm2 = gpio.PWM(pin2, 500)
pwm3 = gpio.PWM(pin3, 500)
pwm4 = gpio.PWM(pin4, 500)
pwm5 = gpio.PWM(pin5, 500)
pwm6 = gpio.PWM(pin6, 500)
pwm7 = gpio.PWM(pin7, 500)
pwm8 = gpio.PWM(pin8, 500)
# pwm波控制初始化
pwm1.start(0)
pwm2.start(0)
pwm3.start(0)
pwm4.start(0)
pwm5.start(0)
pwm6.start(0)
pwm7.start(0)
pwm8.start(0)

# center定义
center = 320
# 打开摄像头，图像尺寸640*480（长*高），opencv存储值为480*640（行*列）
cap = cv2.VideoCapture(0)
while (1):
    ret, frame = cap.read()
    # 转化为灰度图
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # 大津法二值化
    retval, dst = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU)
    # 膨胀，白区域变大
    #dst = cv2.dilate(dst, None, iterations=2)
    # # 腐蚀，白区域变小
    dst = cv2.erode(dst, None, iterations=6)

    # 单看第400行的像素值
    color = dst[300]
    # 找到白色的像素点个数
    white_count = np.sum(color == 255)
    # 找到白色的像素点索引
    white_index = np.where(color == 255)

    # 防止white_count=0的报错
    if white_count == 0:
        white_count = 1

    # 找到白色像素的中心点位置
    center = (white_index[0][white_count - 1] + white_index[0][0]) / 2

    # 计算出center与标准中心点的偏移量
    direction = center - 320

    print(direction)

    # 停止
    if abs(direction) > 250:
        pwm1.ChangeDutyCycle(0)
        pwm2.ChangeDutyCycle(0)
        pwm3.ChangeDutyCycle(0)
        pwm4.ChangeDutyCycle(0)
        pwm5.ChangeDutyCycle(0)
        pwm6.ChangeDutyCycle(0)
        pwm7.ChangeDutyCycle(0)
        pwm8.ChangeDutyCycle(0)

    # 右转
    elif direction >= 0:
        # 限制在70以内
        kkk=0
        if direction > 50:
            kkk=min(50,direction-50)
            direction = 50
        pwm1.ChangeDutyCycle(50 + direction)
        pwm2.ChangeDutyCycle(50 + direction)
        pwm3.ChangeDutyCycle(50 - kkk)
        pwm4.ChangeDutyCycle(50 - kkk)
        pwm5.ChangeDutyCycle(0)
        pwm6.ChangeDutyCycle(0)
        pwm7.ChangeDutyCycle(0)
        pwm8.ChangeDutyCycle(0)

    # 左转
    elif direction < 0:
        ppp=-direction
        kkk = 0
        if ppp > 50:
            kkk=min(50,ppp-50)
            ppp =50
        pwm1.ChangeDutyCycle(50 - kkk)
        pwm2.ChangeDutyCycle(50 - kkk)
        pwm3.ChangeDutyCycle(50 + ppp)
        pwm4.ChangeDutyCycle(50 + ppp)
        pwm5.ChangeDutyCycle(0)
        pwm6.ChangeDutyCycle(0)
        pwm7.ChangeDutyCycle(0)
        pwm8.ChangeDutyCycle(0)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 释放清理
cap.release()
cv2.destroyAllWindows()
pwm1.stop()
pwm2.stop()
pwm3.stop()
pwm4.stop()
gpio.cleanup()