import os
import pickle
from collections import defaultdict

from PyQt5 import QtSql
from PyQt5.QtSql import QSqlQuery, QSqlDatabase, QSqlQueryModel
import matplotlib
from tqdm import tqdm

matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class MyFigure(FigureCanvas):
    def __init__(self, width=10, height=8, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)

        super(MyFigure, self).__init__(self.fig)


class DBManager_Changed():
    def __init__(self):
        # pass
        self.db = None

    def merge(self,  database2):
        db1 = QSqlDatabase.addDatabase("QSQLITE", 'sqlite')
        db1.setDatabaseName(database2)
        db1.open()
        # sql handler

        query = QSqlQuery(db1)
        queryModel = QSqlQueryModel()
        value_metric_ = []
        value_metric = []
        value_idmax = []
        value_error = []
        if db1.open():
            print(1)
            # if query.exec(
            #         'update id ,model_name,dataset_name,class_name,TP,FP,FN,F1,Ap,Map,Precision,Recall,Threshold from metric_'):
            #     while query.next():
            #         value_metric_ .append( [query.value(i) for i in range(13)])
            # if query.exec(
            #     'update id ,model_name,dataset_name,class_name,TP,FP,FN,F1,Ap,Map,Precision,Recall,Threshold from metric'):
            #     while query.next():
            #         value_metric.append( [query.value(i) for i in range(13)])
            # if query.exec(
            #         'update id ,model_name,dataset_name,class_name,ID_max from id_max'):
            #     while query.next():
            #         value_idmax.append( [query.value(i) for i in range(5)])
            # if query.exec(
            #         'update id ,model_name,dataset_name,error_file from error'):
            #     while query.next():
            #         value_error.append([query.value(i) for i in range(4)])
            if query.exec(
                    'update metric_ set dataset_name = "20210612" where model_name = "prune_0.5" dataset_name="coco"'):
                while query.next():
                    value_metric_.append([query.value(i) for i in range(13)])
            if query.exec(
                    'update metric set dataset_name = "20210612" where model_name = "prune_0.5" dataset_name="coco"'):
                while query.next():
                    value_metric.append([query.value(i) for i in range(13)])
            if query.exec(
                    'update id_max set dataset_name = "20210612" where model_name = "prune_0.5" dataset_name="coco"'):
                while query.next():
                    value_idmax.append([query.value(i) for i in range(5)])
            if query.exec(
                    'update error set dataset_name = "20210612" where model_name = "prune_0.5" dataset_name="coco"'):
                while query.next():
                    value_error.append([query.value(i) for i in range(4)])
        db1.close()

class DBManager_Deleted():
    def __init__(self):
        # pass
        self.db = None

    def merge(self,  database2):
        db1 = QSqlDatabase.addDatabase("QSQLITE", 'sqlite')
        db1.setDatabaseName(database2)
        db1.open()
        # sql handler

        query = QSqlQuery(db1)
        queryModel = QSqlQueryModel()
        value_metric_ = []
        value_metric = []
        value_idmax = []
        value_error = []
        if db1.open():
            # if query.exec(
            #         'update id ,model_name,dataset_name,class_name,TP,FP,FN,F1,Ap,Map,Precision,Recall,Threshold from metric_'):
            #     while query.next():
            #         value_metric_ .append( [query.value(i) for i in range(13)])
            # if query.exec(
            #     'update id ,model_name,dataset_name,class_name,TP,FP,FN,F1,Ap,Map,Precision,Recall,Threshold from metric'):
            #     while query.next():
            #         value_metric.append( [query.value(i) for i in range(13)])
            # if query.exec(
            #         'update id ,model_name,dataset_name,class_name,ID_max from id_max'):
            #     while query.next():
            #         value_idmax.append( [query.value(i) for i in range(5)])
            # if query.exec(
            #         'update id ,model_name,dataset_name,error_file from error'):
            #     while query.next():
            #         value_error.append([query.value(i) for i in range(4)])
            if query.exec(
                    'delete from metric_ where model_name="yolov3_best"'):
                while query.next():
                    value_metric_.append([query.value(i) for i in range(13)])
            if query.exec(
                    'delete from metric where model_name="yolov3_best"'):
                 while query.next():
                     print(1)

            if query.exec(
                    'delete from id_max where  model_name="yolov3_best"'):
                while query.next():
                    value_idmax.append([query.value(i) for i in range(5)])
            if query.exec(
                    'delete from error where  model_name="yolov3_best"'):
                while query.next():
                    value_error.append([query.value(i) for i in range(4)])
        db1.close()


class DBManager_Deleted_singal():
    def __init__(self):
        # pass
        self.db = None

    def merge(self,  database2):
        db1 = QSqlDatabase.addDatabase("QSQLITE", 'sqlite')
        db1.setDatabaseName(database2)
        db1.open()
        # sql handler

        query = QSqlQuery(db1)
        queryModel = QSqlQueryModel()
        value_metric_ = []
        value_metric = []
        value_idmax = []
        value_error = []
        if db1.open():
            if query.exec(
                'select id ,model_name,dataset_name,class_name,TP,FP,FN,F1,Ap,Map,Precision,Recall,Threshold from metric'):
                while query.next():
                    value_metric.append( [query.value(i) for i in range(13)])
        for j in value_metric:
            if int(j[0])>2000:
                value_idmax.append("\""+j[3]+"\"")

        for m in value_idmax:
            print(m)
            print('delete from metric where class_name='+str(m))
            if query.exec(
                    'delete from metric where class_name='+m):
                 while query.next():
                     print(1)



            # #
                #     value_metric.append([query.value(i) for i in range(13)])
            # if query.exec(
            #         'delete from id_max where model_name = "yolov3_last_v1031" and dataset_name="20210924-escalator"'):
            #     while query.next():
            #         value_idmax.append([query.value(i) for i in range(5)])
            # if query.exec(
            #         'delete from error where model_name = "yolov3_last_v1031" and dataset_name="20210924-escalator"'):
            #     while query.next():
            #         value_error.append([query.value(i) for i in range(4)])
        db1.close()


# DBManager_Deleted().merge("/home/fandong/Code/object_detection_evaluation/src/database/core.db")

