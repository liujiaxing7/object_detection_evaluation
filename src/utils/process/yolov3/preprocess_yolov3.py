#!/usr/bin/python3 python
# encoding: utf-8
'''
@author: 刘家兴
@contact: ljx0ml@163.com
@file: model.py
@time: 2021/8/3 12:02
@desc:
'''

import numpy as np
import cv2
IMAGE_SIZE_YOLOV3=416

def pre_process(inp_img):
    gray = inp_img[:, :, 0]
    gray = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
    image = cv2.resize(gray, (IMAGE_SIZE_YOLOV3, IMAGE_SIZE_YOLOV3), interpolation=cv2.INTER_LINEAR)

    img = np.half(image)
    img /= 255.0
    if img.shape[-1] == 3:
        img = np.expand_dims(img, 0)
    img = np.transpose(img, (0, 3, 1, 2)).astype(np.float32)

    return img.astype(np.float32)