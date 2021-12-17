import csv
import os
import matplotlib.pyplot as plt
import seaborn
import numpy as np
import matplotlib
# matplotlib.use("Qt5Agg")  # 声明使用QT5
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


class MyFigure(FigureCanvas):
    def __init__(self, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)

        super(MyFigure, self).__init__(self.fig)


path = "/home/fandong/Code/object_detection_evaluation/result"


def drawAll(path):
    path = "/home/fandong/Code/object_detection_evaluation/result"
    """
    draw map f1 recall prediction
    """
    # total_metric_path=path+"/yolov5"
    total_model_path = os.listdir(path)
    total_model_path.sort()
    map = []
    recall = []
    Precision = []
    F1_ = []
    index = [i for i in total_model_path]
    epoch = []
    for i in range(len(total_model_path)):
        model_path = path + "/" + total_model_path[i]
        csv_path = [i for i in os.listdir(model_path) if i.endswith(".csv")]
        csv_path = model_path + "/" + csv_path[0]
        with open(csv_path, 'r') as f:
            reader = csv.reader(f)
            each_metric = []
            for row in reader:
                each_metric.append(row)
            map.append(float(each_metric[2][0]))
            recall.append(float(each_metric[2][1]))
            F1_.append(float(each_metric[2][2]))
            Precision.append(float(each_metric[2][3]))
            epoch.append(i)

    F1 = MyFigure(width=5, height=4, dpi=100)
    F1.fig.suptitle("Figure")
    F1.axes0 = F1.fig.add_subplot(224)
    F1.axes1 = F1.fig.add_subplot(223)
    F1.axes2 = F1.fig.add_subplot(222)
    F1.axes3 = F1.fig.add_subplot(221)
    F1.axes0.bar(index, map)
    F1.axes1.bar(index, recall)
    F1.axes2.bar(index, Precision)
    F1.axes3.bar(index, F1_)
    # F1.axes.legend()
    # F1.axes4.xlabel("model")
    F1.axes0.set_title("Map")
    F1.axes1.set_title("recall")
    F1.axes2.set_title("Prediction")
    F1.axes3.set_title("F1")

    # F1.axes4.show()

    return F1
