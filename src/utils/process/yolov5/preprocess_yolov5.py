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

def letterBox(img, new_shape=416, color=(128, 128, 128), mode='auto', interp=cv2.INTER_AREA):
    # Resize a rectangular image to a 32 pixel multiple rectangle
    # https://github.com/ultralytics/yolov3/issues/232
    shape = img.shape[:2] # current shape [height, width]
    if isinstance(new_shape, int):
        r = float(new_shape) / max(shape) # ratio = new / old
    else:
        r = max(new_shape) / max(shape)
    ratio = r, r # width, height ratios
    new_unpad = (int(round(shape[1] * r)), int(round(shape[0] * r)))
    # Compute padding https://github.com/ultralytics/yolov3/issues/232
    if mode is 'auto': # minimum rectangle
        dw = np.mod(new_shape - new_unpad[0], 32) / 2 # width padding
        dh = np.mod(new_shape - new_unpad[1], 32) / 2 # height padding
    elif mode is 'square': # square
        dw = (new_shape - new_unpad[0]) / 2 # width padding
        dh = (new_shape - new_unpad[1]) / 2 # height padding
    elif mode is 'rect': # square
        dw = (new_shape[1] - new_unpad[0]) / 2 # width padding
        dh = (new_shape[0] - new_unpad[1]) / 2 # height padding
    elif mode is 'scaleFill':
        dw, dh = 0.0, 0.0
        new_unpad = (new_shape, new_shape)
        ratio = new_shape / shape[1], new_shape / shape[0] # width, height ratios
    if shape[::-1] != new_unpad: # resize
        img = cv2.resize(img, new_unpad, interpolation=interp) # INTER_AREA is better, INTER_LINEAR is faster
    top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
    left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
    img = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color) # add border
    return img, ratio, dw, dh
def preProcessPadding(inp_img,img_size):
    if inp_img.shape[-1]==1 or len(inp_img.shape)==2:
        inp_img = cv2.cvtColor(inp_img[:,:], cv2.COLOR_GRAY2RGB)
    # image = cv2.resize(gray, (IMAGE_SIZE_YOLOV3, IMAGE_SIZE_YOLOV3), interpolation=cv2.INTER_LINEAR)
    image,ratio, dw, dh=letterBox(inp_img,new_shape=img_size, mode='square')

    img = np.half(image)
    img /= 255.0
    if img.shape[-1] == 3:
        img = np.expand_dims(img, 0)
    img = np.transpose(img, (0, 3, 1, 2)).astype(np.float32)

    return img.astype(np.float32)
def preProcess(inp_img):
    if inp_img.shape[-1]==1 or len(inp_img.shape)==2:
        inp_img = cv2.cvtColor(inp_img[:,:], cv2.COLOR_GRAY2RGB)

    image = cv2.resize(inp_img, (IMAGE_SIZE_YOLOV5, IMAGE_SIZE_YOLOV5), interpolation=cv2.INTER_LINEAR)

    img = np.half(image)
    img /= 255.0
    if img.shape[-1] == 3:
        img = np.expand_dims(img, 0)
    img = np.transpose(img, (0, 3, 1, 2)).astype(np.float32)

    return img.astype(np.float32)