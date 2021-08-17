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

def pre_process(inp_img):

    img = np.half(inp_img)  # uint8 to fp16/32
    img /= 255.0  # 0 - 255 to 0.0 - 1.0
    if img.shape[-1] == 3:
        img = np.expand_dims(img, 0)

    img = np.transpose(img, [0, 3, 1, 2])

    return img.astype(np.float32)