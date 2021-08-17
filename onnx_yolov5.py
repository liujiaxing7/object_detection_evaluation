#!/usr/bin/python3 python
# encoding: utf-8
'''
@author: 刘家兴
@contact: ljx0ml@163.com
@file: model.py
@time: 2021/8/3 12.02
@desc:
'''
import os
from src.utils.preprocess_yolov5 import pre_process as yoloPreProcess
from src.utils.postprocess_yolov5 import PostProcessor_YOLOV5 as post_processing
import cv2
import onnxruntime
from src.evaluation import *
import src
import cv2
from PIL import Image
import numpy as np
from PIL import Image
import numpy as np

class ONNX(object):
    def __init__(self, file='./yolov5.onnx'):
        if os.path.isfile(file):
            self.session = onnxruntime.InferenceSession(file)
            self.predictions=[]
            self.datasets=None
        else:
            raise IOError("no such file {}".format(file))

    def forward(self, image):
        oriY = image.shape[0]
        oriX = image.shape[1]
        image = cv2.resize(image, (640, 640), interpolation=cv2.INTER_LINEAR)
        image = yoloPreProcess(image)
        input_name = self.session.get_inputs()[0].name
        outputs = self.session.run(None, {input_name: image})
        boxes = post_processing(outputs)

        box_es=[]
        labels=[]
        scores=[]
        for i in boxes[0]:
            box_es.append([i[0]/640*oriX,i[1]/640*oriY,i[2]/640*oriX,i[3]/640*oriY])
            labels.append(i[5])
            scores.append(i[4])
        prediction={'boxes':box_es,'labels':labels,'scores':scores}
        self.predictions.append(prediction)

    def a(self):
        with open('./datapig1/trainval.txt', 'r') as fi:
            data_list = fi.read().splitlines()  # These are all cleaned out
            fi.close()

        self.datasets = src.build_dataset(data_list, 'VOCDataset', "/home/fandong/Code/Evaluation-procedure/datapig1",
                                          None, None, None, True)
        for i in range(100):
            image_id, annotation = self.datasets.get_file_darknet(i)
            image = np.array(Image.open(image_id))
            # size = image.size()
            # s = image.bits().asstring(size.width() * size.height() * image.depth() // 8)  # format 0xffRRGGBB
            # image = np.fromstring(s, dtype=np.uint8).reshape((size.height(), size.width(), image.depth() // 8))
            gray = image[:, :, 0]
            gray = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
            self.forward(gray)
        xml.evaluation_coco(self.datasets, self.predictions, "./", False, None, None)

a=ONNX()
a.a()
