#!/usr/bin/python3 pyssdthon
# encoding: utf-8
'''
@author: 孙昊
@contact: smartadpole@163.com
@file: image_process.py
@time: 2020/12/4 上午10:35
@desc: 
'''
import cv2
from random import uniform, randint
import numpy as np

__all__ = ['cropForeground', 'randomAffine', 'transparent',
           'add_noise', 'add_gaussian_noise', 'addSaltNoise',
           'augment', 'toTransparent', 'haveColor', 'getGray']

def transparent(img):
    return  4 == img.shape[2]

def cropForeground(img):
    if transparent(img):
        h, w, c = img.shape
        gray = img[:, :, 3]
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (min(30, max(w//10, 2)), min(30, max(h//10, 2))))
        gray = cv2.dilate(gray, kernel)
        gray = cv2.copyMakeBorder(gray, 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=0)
        contours, hierarchy = cv2.findContours(gray, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
        # cv2.drawContours(img, contours,-1,(0,255,0),5)

        if len(contours) == 0:  # why
            return img

        x, y, w, h = cv2.boundingRect(contours[0])
        img_valid = img[y:y+h, x:x+w, :]
        return img_valid
    else:
        return img

def randomAffine(img, crop=True, plain=False):
    w, h, c = img.shape
    top_left = (uniform(0, 0.3), uniform(0, 0.3))
    bottom_left = (uniform(0, 0.3), uniform(0.6, 1))
    min_left = max(max(bottom_left[0], top_left[0]) +0.3, 0.6)
    top_right = (uniform(min_left, 1), uniform(0, min(bottom_left[1]-0.3, 0.4)))
    min_top = max(max(top_right[1], top_left[1])+0.3, 0.6)
    bottom_right = (uniform(min_left, 1), uniform(min_top, 1))
    if transparent(img):
        mode = cv2.BORDER_REPLICATE
    else:
        mode = cv2.BORDER_CONSTANT

    if plain:
        M = cv2.getAffineTransform(np.float32([(0,0), (w-1, 0), (0, h-1)]),
                                   np.float32([(w*top_left[0], h*top_left[1]),
                                               (w*top_right[0], h*top_right[1]),
                                               (w * bottom_left[0], h * bottom_left[1])]))
        affine = cv2.warpAffine(img, M, (w, h), borderMode=mode)
    else:
        M = cv2.getPerspectiveTransform(np.float32([(0,0), (w-1, 0), (0, h-1), (w-1, h-1)]),
                                        np.float32([(w*top_left[0], h*top_left[1]),
                                                    (w*top_right[0], h*top_right[1]),
                                                    (w*bottom_left[0], h*bottom_left[1]),
                                                    (w * bottom_right[0], h * bottom_right[1])]))
        affine = cv2.warpPerspective(img, M, (w, h), borderMode=mode)

    if crop:
        affine = cropForeground(affine)

    return affine

def randomSetPixel(img, n, value):
    n = int(n)
    w, h, c = img.shape

    for i in range(n):
        i, j = randint(0, w-1), randint(0, h-1)
        img[i, j, :] = value

def addSaltNoise(img, rate=0.5):
    h, w, c = img.shape
    n = max(w*h*rate, 20)
    out = img.copy()

    randomSetPixel(out, n, randint(0, 255))
    randomSetPixel(out, n, randint(0, 255))

    if transparent(img):
        out[:, :, 3] = img[:, :, 3]

    return out

def add_gaussian_noise(img, mean=0, var=0.001, gray=0.5):
    if uniform(0, 1) < gray:
        noise = np.random.normal(mean, var ** 0.5, (img.shape[0], img.shape[1])) * 60
        noise = np.tile(noise[:, :, np.newaxis], (1, 1, img.shape[2]))
    else:
        noise = np.random.normal(mean, var ** 0.5, img.shape) * 60
    img = img.astype(np.int16)
    noise = noise.astype(np.int16)
    if transparent(img):
        noise[:, :, 3] = img[:, :, 3]

    img = cv2.add(img, noise)
    img = np.clip(img, 0, 255)
    img = img.astype(np.uint8)

    return img

def add_noise(img, salt_rate=0.5, gaussian_rate=1):
    if uniform(0, 1) < gaussian_rate:
        img = add_gaussian_noise(img, mean=uniform(0.1, 2), var=uniform(0.002, 0.1), gray=1)
    if uniform(0, 1) < salt_rate:
        img = addSaltNoise(img, uniform(0.05, 0.3))

    return img

def augment(img, salt_rate=0.5, gaussian_rate=1):

    img = cv2.copyMakeBorder(img, 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=0)
    target = randomAffine(img)
    i = 0
    while not valid(target):
        if i > 5:
            target = img
            break
        target = randomAffine(img)
        i += 1
    target = add_noise(target, salt_rate, gaussian_rate)

    return target

def valid(img):
    h, w, c = img.shape
    if h < 20 or w < 20:
        return False

    if transparent(img):
        mask = img[:, :, 3]
        count = np.count_nonzero(mask)
        if count / (h * w) < 0.15:
            return False

    return True

def toTransparent(img):
    if img.shape[2] == 3:
        img = img.repeat((1, 1, 2), 2)
        img[:, :, 3] = 255
        img = cv2.copyMakeBorder(img, 1, 1, 1, 1, cv2.BORDER_CONSTANT)

    return img

def haveColor(image):
    diff = image[:, :, 2] - image[:, :, 1]
    diff = np.sum(diff)

    if diff > 50:
        return True
    else:
        return False

def getGray(image):
    color = haveColor(image)

    if color:
        if transparent(image):
            gray = cv2.cvtColor(image[:, :, 0:3], cv2.COLOR_BGR2GRAY)
            gray = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
            gray = np.concatenate((gray, image[:,:, 3, np.newaxis]), 2)
        else:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            gray = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    else:
        gray = image

    return gray