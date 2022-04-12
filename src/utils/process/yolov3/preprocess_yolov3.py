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
def preProcessPadding(inp_img):
    if len(inp_img.shape)==3:
        gray = inp_img[:, :, 0]
    else:gray = inp_img[:, :]
    gray = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
    # image = cv2.resize(gray, (IMAGE_SIZE_YOLOV3, IMAGE_SIZE_YOLOV3), interpolation=cv2.INTER_LINEAR)
    image,ratio, dw, dh=letterBox(gray,new_shape=416, mode='square')

    img = np.half(image)
    img /= 255.0
    if img.shape[-1] == 3:
        img = np.expand_dims(img, 0)
    img = np.transpose(img, (0, 3, 1, 2)).astype(np.float32)

    return img.astype(np.float32)

def preProcess(inp_img):
    if len(inp_img.shape)==3:
        gray = inp_img[:, :, 0]
    else:gray = inp_img[:, :]
    gray = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
    image = cv2.resize(gray, (IMAGE_SIZE_YOLOV3, IMAGE_SIZE_YOLOV3), interpolation=cv2.INTER_LINEAR)
    # image,ratio, dw, dh=letterBox(gray,new_shape=416, mode='square')

    img = np.half(image)
    img /= 255.0
    if img.shape[-1] == 3:
        img = np.expand_dims(img, 0)
    img = np.transpose(img, (0, 3, 1, 2)).astype(np.float32)

    return img.astype(np.float32)


def preProcessMmdetection(inp_img):
    
    if len(inp_img.shape)==3:
        gray = inp_img[:, :, 0]
    else:gray = inp_img[:, :]
    gray = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
    image = cv2.resize(gray, (IMAGE_SIZE_YOLOV3, IMAGE_SIZE_YOLOV3), interpolation=cv2.INTER_LINEAR)

    img = image.copy().astype(np.float32)
    mean = np.float64(np.array([0, 0, 0]).reshape(1, -1))
    stdinv = 1 / np.float64(np.array([255., 255., 255.]).reshape(1, -1))

    cv2.subtract(img, mean, img)  # inplace
    cv2.multiply(img, stdinv, img)  # inplace

    if img.shape[-1] == 3:
        img = np.expand_dims(img, 0)
    img = np.transpose(img, (0, 3, 1, 2)).astype(np.float32)

    return img.astype(np.float32)