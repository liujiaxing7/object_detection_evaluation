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


# DBManager_Deleted().merge("/home/fandong/Code/object_detection_evaluation/src/database/core.db")

