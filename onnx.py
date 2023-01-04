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

from src.utils.process.ssd.ssd import PostProcessor_SSD, getPredictionSSD
from src.utils.process.ssd.preprocess import pre_process as SSD_preProcess
from src.utils.process.yolov3.preprocess_yolov3 import preProcess as yoloPreProcessYolov3
from src.utils.process.yolov3.preprocess_yolov3 import preProcessMmdetection as yoloPreProcessYolov3Mmdetection
from src.utils.process.yolov3.preprocess_yolov3 import preProcessPadding as yoloPreProcessYolov3Padding
from src.utils.process.yolov5.preprocess_yolov5 import preProcessPadding as yoloPreProcessYolov5
from src.utils.process.yolov3.postprocess_yolov3 import THRESHOLD_YOLOV3, postProcessing, \
    loadClassNames, getPredictionYolov3,getPredictionYolov3Mmdetection
from src.utils.process.yolov3_tiny3.postprocess_yolov3_tiny3 import postProcessingTiny3
from src.utils.process.yolov5.postprocess_yolov5 import postProcessorYOLOV5, IMAGE_SIZE_YOLOV5, THRESHOLD_YOLOV5, \
    getPredictionYolov5, postProcessorYOLOV5x, getPredictionYolov5x


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
    def __init__(self, file, batch_size, data_dir, classes, ret, process_method):
        if os.path.isfile(file):
            self.session = onnxruntime.InferenceSession(file)
            self.predictions = []
            self.datasets = None
            self.batch_size = batch_size
            self.data_dir = data_dir
            self.classes_path = classes
            self.format = ret
            self.process_method = process_method
            self.img_size_yolov3 = [416, 416]
            self.img_size_yolov5s = [320, 320]
            self.img_size_yolov5x = [640, 640]
            self.conf = 0.45

        else:
            raise IOError("no such file {}".format(file))

    def forward(self, image):
        oriY = image.shape[0]
        oriX = image.shape[1]

        if self.process_method == 'yolov3' or self.process_method == 'yolov3_tiny3':
            image = yoloPreProcessYolov3(image)
        elif self.process_method == 'yolov3_padding' or self.process_method == 'yolov3_tiny3_padding':
            image = yoloPreProcessYolov3Padding(image)
        elif self.process_method == 'yolov3_mmdetection':
            image=yoloPreProcessYolov3Mmdetection(image)
        elif self.process_method == 'yolov5':
            image = yoloPreProcessYolov5(image,self.img_size_yolov5s[0])
        elif self.process_method == 'yolov5x':
            image = yoloPreProcessYolov5(image, self.img_size_yolov5x[0])
        elif self.process_method == 'ssd':
            image = SSD_preProcess(image)


        input_name = self.session.get_inputs()[0].name
        outputs = self.session.run(None, {input_name: image})

        if self.process_method == 'yolov3_padding':
            boxes = postProcessing(image, THRESHOLD_YOLOV3, self.conf, outputs)
            prediction = getPredictionYolov3(boxes, self.img_size_yolov3[0], self.img_size_yolov3[1])
            self.predictions.append(prediction)

        elif self.process_method == 'yolov3':
            boxes = postProcessing(image, THRESHOLD_YOLOV3, self.conf, outputs)
            prediction = getPredictionYolov3(boxes, oriX, oriY)
            self.predictions.append(prediction)

        elif self.process_method == 'yolov5':
            boxes = postProcessorYOLOV5x(outputs,14)
            prediction = getPredictionYolov5(boxes, oriX, oriY)
            self.predictions.append(prediction)

        elif self.process_method == 'yolov5x':
            boxes = postProcessorYOLOV5x(outputs)
            prediction = getPredictionYolov5x(boxes, oriX, oriY)
            self.predictions.append(prediction)

        elif self.process_method == 'yolov3_tiny3':
            boxes = postProcessingTiny3(image, THRESHOLD_YOLOV3, self.conf, outputs)
            prediction = getPredictionYolov3(boxes, oriX, oriY)
            self.predictions.append(prediction)

        elif self.process_method == 'yolov3_tiny3_padding':
            boxes = postProcessingTiny3(image, THRESHOLD_YOLOV3, self.conf, outputs)
            prediction = getPredictionYolov3(boxes, self.img_size_yolov3[0], self.img_size_yolov3[1])
            self.predictions.append(prediction)

        elif self.process_method == 'yolov3_mmdetection':
            boxes = postProcessing(image, THRESHOLD_YOLOV3, 0.6, outputs)
            prediction = getPredictionYolov3Mmdetection(boxes, oriX, oriY)
            self.predictions.append(prediction)

        elif self.process_method == 'ssd':
            boxes = PostProcessor_SSD(outputs[0], outputs[1], outputs[2])
            prediction = getPredictionSSD(boxes, oriX, oriY)
            self.predictions.append(prediction)

    def evaluate(self):
        self.classes = loadClassNames(self.classes_path)

        # create_list.voctodark(self.data_dir,self.classes)
        print('begin')
        self.datasets = src.buildDataset(self.classes, 'Dataset', self.data_dir, self.format,
                                          None, None, None, True)

        output_dir = './result/' + self.process_method
        if self.format == 'darknet':
            batch_size = len(open(os.path.join(self.data_dir, "val_images.txt")).readlines())
        else:
            batch_size = len(open(os.path.join(self.data_dir, "ImageSets", "Main", "test.txt")).readlines())
        for i in tqdm(range(batch_size)):
            if self.format == 'darknet':
                image_id, annotation = self.datasets.getFileTxtDarknet(i)
            else:
                image_id, annotation = self.datasets.getFile(i)
            # image = cv2.imread(image_id,cv2.IMREAD_GRAYSCALE)
            # image=cv2.equalizeHist(image)
            try:
               image = np.array(Image.open(image_id))
            except:
               print(image_id)

            self.forward(image)

        if self.format == 'voc':
            result_csv, result = xml.evaluation(self.datasets, self.predictions, output_dir, False, None, None,
                                                batch_size)
        elif self.format == 'xml':
            result_csv, result = xml.evaluationXml(self.datasets, self.predictions, output_dir, False, None, None,
                                                    batch_size)
        elif self.format == 'coco':
            result_csv, result = xml.evaluationCoco(self.datasets, self.predictions, output_dir, False, None, None,
                                                     batch_size)
        elif self.format == 'darknet' and self.process_method == 'yolov3_padding' or self.process_method == 'yolov3_tiny3_padding':
            result_csv, result = xml.evaluationDarknetPadding(self.datasets, self.predictions, output_dir, False,
                                                                None, None, batch_size)
        elif self.format == 'darknet':
            result_csv, result = xml.evaluationDarknet(self.datasets, self.predictions, output_dir, False, None, None,
                                                        batch_size)
        return result_csv, result
