#!/usr/bin/python3 python
# encoding: utf-8
'''
@author: 孙昊
@contact: smartadpole@163.com
@file: ssd.py
@time: 2021/2/23 上午10:23
@desc: 
'''
from .utils.box import Locations2Boxes, Center2Corner
from yacs.config import CfgNode as CN
from ...utils import Softmax
import cv2

IMAGE_SIZE_SSD = 320
PIXEL_MEAN = [123, 117, 104]
THRESHOLD = [1, 1, 1, 0.1, 0.1, 1, 1, 0.15, 1, 1, 1]

MODEL = CN()
MODEL.CENTER_VARIANCE = 0.1
MODEL.SIZE_VARIANCE = 0.2

MODEL.PRIORS = CN()
MODEL.PRIORS.FEATURE_MAPS = [20, 10, 5, 3, 2, 1]
MODEL.PRIORS.STRIDES = [16, 32, 64, 100, 150, 300]
MODEL.PRIORS.MIN_SIZES = [30, 105, 150, 195, 240, 285]
MODEL.PRIORS.MAX_SIZES = [40, 150, 195, 240, 285, 330]
MODEL.PRIORS.ASPECT_RATIOS = [[2, 3], [2, 3], [2, 3], [2, 3], [2, 3], [2, 3]]
# When has 1 aspect ratio, every location has 4 boxes, 2 ratio 6 boxes.
# #boxes = 2 + #ratio * 2
MODEL.PRIORS.BOXES_PER_LOCATION = [6, 6, 6, 6, 6, 6]  # number of boxes per feature map location
MODEL.PRIORS.CLIP = True
NUM_CLASSES = 1

from .utils.nms import boxes_nms
from ...utils import TopK
import numpy as np

NMS_THRESHOLD = 0.45
CONFIDENCE_THRESHOLD = 0.25
MAX_PER_CLASS = -1
MAX_PER_IMAGE = 100
# MAX_PER_IMAGE = 2
BACKGROUND_ID = 0

def Filter(width, height, batches_scores: np.ndarray, batches_boxes:np.ndarray):
    batch_size = batches_scores.shape[0]
    result_batch = []

    for batch_id in range(batch_size):
        result = []
        per_img_scores, per_img_boxes = batches_scores[batch_id], batches_boxes[batch_id]  # (N, #CLS) (N, 4)

        for class_id in range(BACKGROUND_ID+1, per_img_scores.shape[1]):
            scores = per_img_scores[:, class_id]
            mask = scores > CONFIDENCE_THRESHOLD
            scores = scores[mask]
            if scores.shape[0] == 0:
                continue
            boxes = per_img_boxes[mask, :]
            boxes[:, 0::2] *= width
            boxes[:, 1::2] *= height

            keep = boxes_nms(boxes, scores, NMS_THRESHOLD, MAX_PER_CLASS)

            nmsed_boxes = boxes[keep, :]
            nmsed_labels = np.array([class_id] * keep.shape[0])
            nmsed_scores = scores[keep]

            if len(result) > MAX_PER_IMAGE > 0: #TODO
                processed_scores, keep = TopK(nmsed_scores, K=MAX_PER_IMAGE)
                nmsed_boxes = nmsed_boxes[keep, :]
                nmsed_labels = nmsed_labels[keep]
                nmsed_scores = nmsed_scores[keep]
            result.append(np.concatenate((nmsed_boxes, nmsed_labels[::, np.newaxis], nmsed_scores[::, np.newaxis]), axis=1))

        result = np.concatenate(result, axis=0) if len(result) > 0 else []
        result_batch.append(result)


    return result_batch

def PostProcessor_SSD(cls_logits, bbox_pred, priors):
    scores = Softmax(cls_logits, axis=2)
    boxes = Locations2Boxes(bbox_pred, priors, MODEL.CENTER_VARIANCE, MODEL.SIZE_VARIANCE)
    boxes = Center2Corner(boxes)
    detections = Filter(IMAGE_SIZE_SSD, IMAGE_SIZE_SSD, scores, boxes)
    return detections

def getPredictionSSD(boxes,oriX,oriY):
    box_es = []
    labels = []
    scores = []
    for result in boxes:
        if len(result) > 0:
            # result = result.tolist()
            for i in result:
                box_es.append([i[0] * oriX/320, i[1] * oriY/320, i[2] * oriX/320, i[3] * oriY/320])
                labels.append(i[4]-1)
                scores.append(i[5])
    prediction = {'boxes': box_es, 'labels': labels, 'scores': scores}
    return prediction