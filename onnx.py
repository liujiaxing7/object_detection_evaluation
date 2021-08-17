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
from src.utils.preprocess import pre_process as yoloPreProcess
from src.utils.postprocess import IMAGE_SIZE_YOLOV3, THRESHOLD_YOLOV3, post_processing,\
    load_class_names
import cv2
import onnxruntime
from src.evaluation import *
import src
import cv2
from PIL import Image
import numpy as np
from PIL import Image
import numpy as np
import src.datasets.voctodarknet as create_list
class ONNX(object):
    def __init__(self, file,batch_size,data_dir,classes,ret):
        if os.path.isfile(file):
            self.session = onnxruntime.InferenceSession(file)
            self.predictions=[]
            self.datasets=None
            self.batch_size=batch_size
            self.data_dir=data_dir
            self.classes_path=classes
            self.format=ret

        else:
            raise IOError("no such file {}".format(file))

    def forward(self, image):
        oriY = image.shape[0]
        oriX = image.shape[1]
        image = cv2.resize(image, (IMAGE_SIZE_YOLOV3, IMAGE_SIZE_YOLOV3), interpolation=cv2.INTER_LINEAR)
        image = yoloPreProcess(image)
        input_name = self.session.get_inputs()[0].name
        outputs = self.session.run(None, {input_name: image})
        boxes = post_processing(image, THRESHOLD_YOLOV3, 0.6, outputs)

        box_es=[]
        labels=[]
        scores=[]
        for i in boxes[0]:
            box_es.append([i[0]*oriX,i[1]*oriY,i[2]*oriX,i[3]*oriY])
            labels.append(i[6])
            scores.append(i[4])
        prediction={'boxes':box_es,'labels':labels,'scores':scores}
        self.predictions.append(prediction)

    def load_class_names(self,namesfile):
        class_names = []
        with open(namesfile, 'r') as fp:
            lines = fp.readlines()
        for line in lines:
            line = line.rstrip()
            class_names.append(line)
        return class_names
    def evaluate(self):
        self.classes=load_class_names(self.classes_path)
        create_list.voctodark(self.data_dir,self.classes)
        with open(self.data_dir+'/trainval.txt', 'r') as fi:
            data_list = fi.read().splitlines()  # These are all cleaned out
            fi.close()

        self.datasets = src.build_dataset(data_list,self.classes, 'Dataset', self.data_dir,
                                          None, None, None, True)
        for i in range(200):
            image_id, annotation = self.datasets.get_file(i)
            image = np.array(Image.open(image_id))
            # size = image.size()
            # s = image.bits().asstring(size.width() * size.height() * image.depth() // 8)  # format 0xffRRGGBB
            # image = np.fromstring(s, dtype=np.uint8).reshape((size.height(), size.width(), image.depth() // 8))
            gray = image[:, :, 0]
            gray = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
            self.forward(gray)

        if self.format=='voc':
            xml.evaluation(self.datasets, self.predictions, "./", False, None, None)
        if self.format=='coco':
            xml.evaluation_coco(self.datasets, self.predictions, "./", False, None, None)
        if self.format=='darknet':
            xml.evaluation_darknet(self.datasets, self.predictions, "./", False, None, None)

