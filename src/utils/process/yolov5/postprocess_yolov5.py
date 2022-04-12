#!/usr/bin/python3 python
# encoding: utf-8
'''
@author: 焦子傲
@contact: jiao1943@qq.com
@file: postprocess.py
@time: 2021/4/9 13:56
@desc:
'''
from yacs.config import CfgNode as CN

import cv2

IMAGE_SIZE_YOLOV5 = 448
IMAGE_SIZE_YOLOV5x = 640
PIXEL_MEAN = [123, 117, 104]
THRESHOLD_YOLOV5 = 0.25

MODEL = CN()
MODEL.CENTER_VARIANCE = 0.1
MODEL.SIZE_VARIANCE = 0.2

import numpy as np

NMS_THRESHOLD = 0.45
# CONFIDENCE_THRESHOLD = 0.01
MAX_PER_CLASS = -1
MAX_PER_IMAGE = 100
# MAX_PER_IMAGE = 2
BACKGROUND_ID = 0
import time
from src.utils.nms import boxesNms

def xywh2xyxy(x):
    # Convert nx4 boxes from [x, y, w, h] to [x1, y1, x2, y2] where xy1=top-left, xy2=bottom-right
    y = np.copy(x)
    y[:, 0] = x[:, 0] - x[:, 2] / 2  # top left x
    y[:, 1] = x[:, 1] - x[:, 3] / 2  # top left y
    y[:, 2] = x[:, 0] + x[:, 2] / 2  # bottom right x
    y[:, 3] = x[:, 1] + x[:, 3] / 2  # bottom right y
    return y

def boxIou(box1, box2):
    # https://github.com/pytorch/vision/blob/master/torchvision/ops/boxes.py
    """
    Return intersection-over-union (Jaccard index) of boxes.
    Both sets of boxes are expected to be in (x1, y1, x2, y2) format.
    Arguments:
        box1 (Tensor[N, 4])
        box2 (Tensor[M, 4])
    Returns:
        iou (Tensor[N, M]): the NxM matrix containing the pairwise
            IoU values for every element in boxes1 and boxes2
    """

    def boxArea(box):
        # box = 4xn
        return (box[2] - box[0]) * (box[3] - box[1])

    area1 = boxArea(box1.T)
    area2 = boxArea(box2.T)

    # inter(N,M) = (rb(N,M,2) - lt(N,M,2)).clamp(0).prod(2)
    inter = (np.minimum(box1[:, None, 2:], box2[:, 2:]) - np.maximum(box1[:, None, :2], box2[:, :2])).clamp(0).prod(2)
    return inter / (area1[:, None] + area2 - inter)  # iou = inter / (area1 + area2 - inter)

def nonMaxSuppression(prediction, conf_thres=0.25, iou_thres=0.45, classes=None, agnostic=False, multi_label=False,
                        labels=()):
    """Runs Non-Maximum Suppression (NMS) on inference results

    Returns:
         list of detections, on (n,6) tensor per image [xyxy, conf, cls]
    """

    nc = prediction.shape[2] - 5  # number of classes
    xc = prediction[..., 4] > conf_thres  # candidates

    # Settings
    min_wh, max_wh = 2, 4096  # (pixels) minimum and maximum box width and height
    max_det = 300  # maximum number of detections per image
    max_nms = 30000  # maximum number of boxes into torchvision.ops.nms()
    time_limit = 10.0  # seconds to quit after
    redundant = True  # require redundant detections
    multi_label &= nc > 1  # multiple labels per box (adds 0.5ms/img)
    merge = False  # use merge-NMS

    t = time.time()
    output = [np.zeros((0, 6))] * prediction.shape[0]
    for xi, x in enumerate(prediction):  # image index, image inference
        # Apply constraints
        # x[((x[..., 2:4] < min_wh) | (x[..., 2:4] > max_wh)).any(1), 4] = 0  # width-height
        x = x[xc[xi]]  # confidence

        # Cat apriori labels if autolabelling
        if labels and len(labels[xi]):
            l = labels[xi]
            v = np.zeros((len(l), nc + 5))
            v[:, :4] = l[:, 1:5]  # box
            v[:, 4] = 1.0  # conf
            v[range(len(l)), l[:, 0].long() + 5] = 1.0  # cls
            x = np.concatenate((x, v), 0)

        # If none remain process next image
        if not x.shape[0]:
            continue

        # Compute conf
        x[:, 5:] *= x[:, 4:5]  # conf = obj_conf * cls_conf

        # Box (center x, center y, width, height) to (x1, y1, x2, y2)
        box = xywh2xyxy(x[:, :4])

        # Detections matrix nx6 (xyxy, conf, cls)
        if multi_label:
            i, j = (x[:, 5:] > conf_thres).nonzero(as_tuple=False).T
            x = np.concatenate((box[i], x[i, j + 5, None], j[:, None].astype(np.float32)), 1)
        else:  # best class only
            # conf, j = x[:, 5:].max(1, keepdim=True)
            conf = np.expand_dims(x[:, 5:].max(1), 1)
            j = np.expand_dims(x[:, 5:].argmax(1), 1)

            x = np.concatenate((box, conf, j.astype(np.float32)), 1)[conf.reshape(-1) > conf_thres]

        # Filter by class
        if classes is not None:
            x = x[(x[:, 5:6] == np.array(classes)).any(1)]

        # Apply finite constraint
        # if not torch.isfinite(x).all():
        #     x = x[torch.isfinite(x).all(1)]

        # Check shape
        n = x.shape[0]  # number of boxes
        if not n:  # no boxes
            continue
        elif n > max_nms:  # excess boxes
            x = x[x[:, 4].argsort(descending=True)[:max_nms]]  # sort by confidence

        # Batched NMS
        c = x[:, 5:6] * (0 if agnostic else max_wh)  # classes
        boxes, scores = x[:, :4] + c, x[:, 4]  # boxes (offset by class), scores
        i = boxesNms(boxes, scores, iou_thres)  # NMS
        if i.shape[0] > max_det:  # limit detections
            i = i[:max_det]
        if merge and (1 < n < 3E3):  # Merge NMS (boxes merged using weighted mean)
            # update boxes as boxes(i,4) = weights(i,n) * boxes(n,4)
            iou = boxIou(boxes[i], boxes) > iou_thres  # iou matrix
            weights = iou * scores[None]  # box weights
            x[i, :4] = np.multiply(weights, x[:, :4]).float() / weights.sum(1, keepdim=True)  # merged boxes
            if redundant:
                i = i[iou.sum(1) > 1]  # require redundancy

        output[xi] = x[i]
        if (time.time() - t) > time_limit:
            print(f'WARNING: NMS time limit {time_limit}s exceeded')
            break  # time limit exceeded

    return output

def makeGrid(nx=20, ny=20):
    xv, yv = np.meshgrid(np.arange(ny), np.arange(nx))
    return np.stack((xv, yv), 2).reshape((1, 1, ny, nx, 2)).astype(np.float32)

def sigmoid(x):
    return 1/(1+np.exp(-x))

def postProcessorYOLOV5(x):

    # grid = [np.zeros(1)] * 3  # init grid
    # z = []  # inference output
    # stride = [8, 16, 32]
    #
    # for i in range(3):
    #     bs, _, ny, nx, _ = x[i].shape  # x(bs,255,20,20) to x(bs,3,20,20,85)
    #
    #     if grid[i].shape[2:4] != x[i].shape[2:4]:
    #         grid[i] = makeGrid(nx, ny)
    #
    #     y = sigmoid(x[i])       # sigmoid is defined above with NumPy
    #
    #     y[..., 0:2] = (y[..., 0:2] * 2. - 0.5 + grid[i]) * stride[i]  # xy
    #
    #     anchors = [[10, 13, 16, 30, 33, 23],            # P3/8
    #                 [30, 61, 62, 45, 59, 119],          # P4/16
    #                 [116, 90, 156, 198, 373, 326]]      # P5/32
    #
    #     anchors = np.array(anchors)
    #     anchor_grid = anchors.copy().reshape(len(anchors), 1, -1, 1, 1, 2)
    #     y[..., 2:4] = (y[..., 2:4] * 2) ** 2 * anchor_grid[i]  # wh
    #     z.append(y.reshape(bs, -1, 85))
    #
    # output = np.concatenate(z, 1)
    pred = nonMaxSuppression(x, 0.25, 0.45, classes=None, agnostic=False)

    return pred

def postProcessorYOLOV5x(x):

    grid = [np.zeros(1)] * 3  # init grid
    z = []  # inference output
    stride = [8, 16, 32]

    for i in range(3):
        bs, _, ny, nx, _ = x[i].shape  # x(bs,255,20,20) to x(bs,3,20,20,85)

        if grid[i].shape[2:4] != x[i].shape[2:4]:
            grid[i] = makeGrid(nx, ny)

        y = sigmoid(x[i])       # sigmoid is defined above with NumPy

        y[..., 0:2] = (y[..., 0:2] * 2. - 0.5 + grid[i]) * stride[i]  # xy

        anchors = [[10, 13, 16, 30, 33, 23],            # P3/8
                    [30, 61, 62, 45, 59, 119],          # P4/16
                    [116, 90, 156, 198, 373, 326]]      # P5/32

        anchors = np.array(anchors)
        anchor_grid = anchors.copy().reshape(len(anchors), 1, -1, 1, 1, 2)
        y[..., 2:4] = (y[..., 2:4] * 2) ** 2 * anchor_grid[i]  # wh
        z.append(y.reshape(bs, -1, 95))

    output = np.concatenate(z, 1)
    pred = nonMaxSuppression(output, 0.25, 0.45, classes=None, agnostic=False)

    return pred

def getPredictionYolov5(boxes,oriX,oriY):
    box_es = []
    labels = []
    scores = []
    for result in boxes:
        if len(result) > 0:
            result = result.tolist()
            result = [r for r in result if r[4] > THRESHOLD_YOLOV5]

            for i in result:
                x, y, x2, y2, score, label = i

                w = IMAGE_SIZE_YOLOV5 / max(oriX, oriY)

                y = (y - (IMAGE_SIZE_YOLOV5 - w * oriY) / 2) / w
                y2 = (y2 - (IMAGE_SIZE_YOLOV5 - w * oriY) / 2) / w
                x = (x - (IMAGE_SIZE_YOLOV5 - w * oriX) / 2) / w
                x2 = (x2 - (IMAGE_SIZE_YOLOV5 - w * oriX) / 2) / w

                box_es.append([x, y,
                               x2, y2])
                labels.append(i[5])
                scores.append(i[4])
    prediction = {'boxes': box_es, 'labels': labels, 'scores': scores}
    return prediction


def getPredictionYolov5x(boxes, oriX, oriY):
    box_es = []
    labels = []
    scores = []
    for result in boxes:
        if len(result) > 0:
            result = result.tolist()
            result = [r for r in result if r[4] > THRESHOLD_YOLOV5]

            for i in result:
                x, y, x2, y2, score, label = i

                w = IMAGE_SIZE_YOLOV5x / max(oriX, oriY)

                y = (y - (IMAGE_SIZE_YOLOV5x - w * oriY) / 2) / w
                y2 = (y2 - (IMAGE_SIZE_YOLOV5x - w * oriY) / 2) / w
                x = (x - (IMAGE_SIZE_YOLOV5x - w * oriX) / 2) / w
                x2 = (x2 - (IMAGE_SIZE_YOLOV5x - w * oriX) / 2) / w

                box_es.append([x, y,
                               x2, y2])
                labels.append(i[5])
                scores.append(i[4])
    prediction = {'boxes': box_es, 'labels': labels, 'scores': scores}
    return prediction