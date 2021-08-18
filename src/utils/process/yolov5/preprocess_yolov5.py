#!/usr/bin/python3 python
# encoding: utf-8
'''
@author: 焦子傲
@contact: jiao1943@qq.com
@file: model.py
@time: 2021/4/11 15:56
@desc:
'''

import numpy as np
from cv2 import cv2
IMAGE_SIZE_YOLOV5=640

def pre_process(inp_img):
    gray = inp_img[:, :, 0]
    gray = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
    image = cv2.resize(gray, (IMAGE_SIZE_YOLOV5, IMAGE_SIZE_YOLOV5), interpolation=cv2.INTER_LINEAR)

    img = np.half(image)
    img /= 255.0
    if img.shape[-1] == 3:
        img = np.expand_dims(img, 0)
    img = np.transpose(img, (0, 3, 1, 2)).astype(np.float32)

    return img.astype(np.float32)