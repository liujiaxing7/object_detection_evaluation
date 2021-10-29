import os
import pickle
from collections import defaultdict

from PyQt5 import QtSql
from PyQt5.QtSql import QSqlQuery,QSqlDatabase,QSqlQueryModel
import matplotlib
from tqdm import tqdm

matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
class MyFigure(FigureCanvas):
    def __init__(self,width=10, height=8, dpi=100):

        self.fig = Figure(figsize=(width, height), dpi=dpi)

        super(MyFigure,self).__init__(self.fig)

class DBManager_Changed():
    def __init__(self):
        # pass
        self.db=None
    def merge(self,database1,database2):
        db1=QSqlDatabase.addDatabase("QSQLITE",'sqlite')
        db1.setDatabaseName(database2)
        db1.open()
          # sql handler

        query = QSqlQuery(db1)
        queryModel = QSqlQueryModel()
        value_metric_=[]
        value_metric=[]
        value_idmax=[]
        value_error=[]
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
                     'update metric_ set dataset_name = "20210821-escalator" where dataset_name = "20210821_escalator"'):
                while query.next():
                    value_metric_ .append( [query.value(i) for i in range(13)])
            if query.exec(
                 'update metric set dataset_name = "20210821-escalator" where dataset_name = "20210821_escalator"'):
                while query.next():
                    value_metric.append( [query.value(i) for i in range(13)])
            if query.exec(
                     'update id_max set dataset_name = "20210821-escalator" where dataset_name = "20210821_escalator"'):
                while query.next():
                    value_idmax.append( [query.value(i) for i in range(5)])
            if query.exec(
                    'update error set dataset_name = "20210821-escalator" where dataset_name = "20210821_escalator"'):
                while query.next():
                    value_error.append([query.value(i) for i in range(4)])
        db1.close()
    #     self.add_database(database1,value_metric_,value_metric,value_idmax,value_error)
    # def add_database(self,database1,value_metric_,value_metric,value_idmax,value_error):
    #     self.db = QSqlDatabase.addDatabase("QSQLITE", 'sqlite')
    #     self.db.setDatabaseName(database1)
    #     self.db.open()
    #     query = QSqlQuery(self.db) #sql handler
    #     queryModel = QSqlQueryModel()
    #     if self.db.open():
    #         for i in tqdm(value_metric_):
    #             self.add_item_(i[1],i[2],i[3],i[4],i[5],i[6],i[7],
    #                            i[8],i[9],i[10],i[11],i[12])
    #         for j in tqdm(value_metric):
    #             self.add_item(j[1],j[2],j[3],j[4],j[5],j[6],j[7],
    #                            j[8],j[9],j[10],j[11],j[12])
    #         for m in tqdm(value_idmax):
    #             self.add_item_id(m[1],m[2],m[3],m[4])
    #         for n in tqdm(value_error):
    #             self.add_erro_file(n[1],n[2],n[3])
    #
    # def add_item(self, model_name, dataset_name, class_name, tp, fp, fn, F1, ap, map, prec, recall, thre):
    #     model_name = "\"" + model_name + "\""
    #     dataset_name = "\"" + dataset_name + "\""
    #     class_name = "\"" + class_name + "\""
    #     id = self.get_max_id() + 1
    #     query = QSqlQuery(self.db)
    #     if self.db.open():
    #
    #         query.exec_(
    #             "create table metric(id int primary key, model_name str , dataset_name str,class_name str,"
    #             " TP int,FP int,FN int,F1 float,Ap float ,Map float ,Precision float ,Recall float,Threshold float  )")
    #
    #         query.exec_("insert into metric values(" + str(
    #             id) + "," + model_name + "," + dataset_name + "," + class_name + "," + str(tp) + "," + str(
    #             fp) + "," + str(fn) + "," + str(F1) + "," + str(ap) + "," + str(map) + "," + str(
    #             prec) + "," + str(recall) + "," + str(thre) + ")")
    #
    #         # insert_sql = 'insert into student metric (?,?,?)'
    #         # query.prepare(insert_sql)
    #         # query.addBindValue(4)
    #         # query.addBindValue('test3')
    #         # query.addBindValue(1)
    #         self.db.close()
    #
    # def add_item_(self, model_name, dataset_name, class_name, tp, fp, fn, F1, ap, map, prec, recall, thre):
    #     model_name = "\"" + model_name + "\""
    #     dataset_name = "\"" + dataset_name + "\""
    #     class_name = "\"" + class_name + "\""
    #     id = self.get_max_id_() + 1
    #     query = QSqlQuery(self.db)
    #     if self.db.open():
    #         # query = QSqlQuery()
    #         query.exec_(
    #             "create table metric_(id int primary key, model_name str , dataset_name str,class_name str,"
    #             " TP int,FP int,FN int,F1 float,Ap float ,Map float ,Precision float ,Recall float,Threshold float  )")
    #
    #         query.exec_("insert into metric_ values(" + str(
    #             id) + "," + model_name + "," + dataset_name + "," + class_name + "," + str(tp) + "," + str(
    #             fp) + "," + str(fn) + "," + str(F1) + "," + str(ap) + "," + str(map) + "," + str(
    #             prec) + "," + str(recall) + "," + str(thre) + ")")
    #
    #         # insert_sql = 'insert into student metric (?,?,?)'
    #         # query.prepare(insert_sql)
    #         # query.addBindValue(4)
    #         # query.addBindValue('test3')
    #         # query.addBindValue(1)
    #         self.db.close()
    #
    # def add_item_id(self, model_name, dataset_name, class_name, id_):
    #     model_name = "\"" + model_name + "\""
    #     dataset_name = "\"" + dataset_name + "\""
    #     class_name = "\"" + class_name + "\""
    #     id = self.get_max_id_id() + 1
    #     query = QSqlQuery(self.db)
    #     if self.db.open():
    #         # query = QSqlQuery()
    #         query.exec_(
    #             "create table id_max(id int primary key, model_name str , dataset_name str,class_name str,ID_max int)")
    #
    #         query.exec_("insert into id_max values(" + str(
    #             id) + "," + model_name + "," + dataset_name + "," + class_name + "," + str(id_) + ")")
    #
    #         # insert_sql = 'insert into student metric (?,?,?)'
    #         # query.prepare(insert_sql)
    #         # query.addBindValue(4)
    #         # query.addBindValue('test3')
    #         # query.addBindValue(1)
    #         self.db.close()
    #
    # def add_erro_file(self, model_name, dataset_name, error_file):
    #     model_name = "\"" + model_name + "\""
    #     dataset_name = "\"" + dataset_name + "\""
    #     error_file = "\"" + error_file + "\""
    #     id = self.get_max_id_error() + 1
    #     query = QSqlQuery(self.db)
    #     if self.db.open():
    #         # query = QSqlQuery()
    #         query.exec_(
    #             "create table error(id int primary key, model_name str , dataset_name str,error_file str)")
    #
    #         query.exec_("insert into error values(" + str(
    #             id) + "," + model_name + "," + dataset_name + "," + error_file + ")")
    #
    #         # insert_sql = 'insert into student metric (?,?,?)'
    #         # query.prepare(insert_sql)
    #         # query.addBindValue(4)
    #         # query.addBindValue('test3')
    #         # query.addBindValue(1)
    #         self.db.close()
    #
    # def get_max_id(self):
    #     self.db.open(self.db)
    #     id_all=[]
    #     query = QSqlQuery()
    #     if query.exec('select id from metric'):
    #         while query.next():
    #             id = query.value(0)
    #             id_all.append(id)
    #     if len(id_all)==0:
    #         return 0
    #     return max(id_all)
    #
    # def get_max_id_(self):
    #     self.db.open()
    #     id_all=[]
    #     query = QSqlQuery(self.db)
    #     if query.exec('select id from metric_'):
    #         while query.next():
    #             id = query.value(0)
    #             id_all.append(id)
    #     if len(id_all)==0:
    #         return 0
    #     return max(id_all)
    #
    # def get_max_id_id(self):
    #     self.db.open()
    #     id_all=[]
    #     query = QSqlQuery(self.db)
    #     if query.exec('select id from id_max'):
    #         while query.next():
    #             id = query.value(0)
    #             id_all.append(id)
    #     if len(id_all)==0:
    #         return 0
    #     return max(id_all)
    #
    # def get_max_id_error(self):
    #     self.db.open()
    #     id_all=[]
    #     query = QSqlQuery(self.db)
    #     if query.exec('select id from error'):
    #         while query.next():
    #             id = query.value(0)
    #             id_all.append(id)
    #     if len(id_all)==0:
    #         return 0
    #     return max(id_all)

# DBManager_Changed().merge("/home/fandong/Code/weights/1/core.db","/home/fandong/Code/weights/core.db")