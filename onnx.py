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

from tqdm import tqdm

from src.utils.process.yolov3.preprocess_yolov3 import pre_process as yoloPreProcess_yolov3
from src.utils.process.yolov5.preprocess_yolov5 import pre_process as yoloPreProcess_yolov5
from src.utils.process.yolov3.postprocess_yolov3 import  THRESHOLD_YOLOV3, post_processing,\
    load_class_names,get_prediction_yolov3
from src.utils.process.yolov3_tiny3.postprocess_yolov3_tiny3 import post_processing_tiny3
from src.utils.process.yolov5.postprocess_yolov5 import PostProcessor_YOLOV5,IMAGE_SIZE_YOLOV5, THRESHOLD_YOLOV5,get_prediction_yolov5
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
    def __init__(self, file,batch_size,data_dir,classes,ret,process_method):
        if os.path.isfile(file):
            self.session = onnxruntime.InferenceSession(file)
            self.predictions=[]
            self.datasets=None
            self.batch_size=batch_size
            self.data_dir=data_dir
            self.classes_path=classes
            self.format=ret
            self.process_method=process_method

        else:
            raise IOError("no such file {}".format(file))

    def forward(self, image):
        oriY = image.shape[0]
        oriX = image.shape[1]

        if self.process_method=='yolov3' or self.process_method=='yolov3_tiny3':
            image = yoloPreProcess_yolov3(image)
        elif self.process_method=='yolov5':
            image = yoloPreProcess_yolov5(image)


        input_name = self.session.get_inputs()[0].name
        outputs = self.session.run(None, {input_name: image})

        if self.process_method=='yolov3':
            boxes = post_processing(image, THRESHOLD_YOLOV3, 0.6, outputs)
            prediction=get_prediction_yolov3(boxes,oriX,oriY)
            self.predictions.append(prediction)

        elif self.process_method=='yolov5':
            boxes = PostProcessor_YOLOV5(outputs)
            prediction=get_prediction_yolov5(boxes,oriX,oriY)
            self.predictions.append(prediction)

        elif self.process_method=='yolov3_tiny3':
            boxes=post_processing_tiny3(image, THRESHOLD_YOLOV3, 0.6, outputs)
            prediction = get_prediction_yolov3(boxes, oriX, oriY)
            self.predictions.append(prediction)

    def evaluate(self):
        self.classes=load_class_names(self.classes_path)

        # create_list.voctodark(self.data_dir,self.classes)
        print('begin')
        self.datasets = src.build_dataset(self.classes, 'Dataset', self.data_dir,
                                          None, None, None, True)

        output_dir='./result/'+self.process_method
        batch_size=len(open(os.path.join(self.data_dir, "ImageSets", "Main", "test.txt" )).readlines())
        batch_size=200
        for i in tqdm(range(batch_size)):
            image_id, annotation = self.datasets.get_file(i)
            image = np.array(Image.open(image_id))

            self.forward(image)

        if self.format=='voc':
            result_csv,result=xml.evaluation(self.datasets, self.predictions, output_dir, False, None, None,batch_size)
        if self.format=='coco':
            result_csv,result=xml.evaluation_coco(self.datasets, self.predictions, output_dir, False, None, None,batch_size)
        if self.format=='darknet':
            result_csv,result=xml.evaluation_darknet(self.datasets, self.predictions,output_dir,False, None, None,batch_size)
        return result_csv,result

