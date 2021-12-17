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

class DBManagerChanged():
    def __init__(self):
        # pass
        self.db=None
        self.first_metric = True
        self.first_metric_ = True
        self.first_id = True
        self. first_error = True

        self. count_metric = 0
        self. count_metric_ = 0
        self. count_id = 0
        self. count_error = 0

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

            if query.exec(
                    'select id ,model_name,dataset_name,class_name,TP,FP,FN,F1,Ap,Map,Precision,Recall,Threshold from metric_'):
                while query.next():
                    value_metric_ .append( [query.value(i) for i in range(13)])
            if query.exec(
                'select id ,model_name,dataset_name,class_name,TP,FP,FN,F1,Ap,Map,Precision,Recall,Threshold from metric'):
                while query.next():
                    value_metric.append( [query.value(i) for i in range(13)])
            if query.exec(
                    'select id ,model_name,dataset_name,class_name,ID_max from id_max'):
                while query.next():
                    value_idmax.append( [query.value(i) for i in range(5)])
            if query.exec(
                    'select id ,model_name,dataset_name,error_file from error'):
                while query.next():
                    value_error.append([query.value(i) for i in range(4)])
        db1.close()
        self.addDatabase(database1,value_metric_,value_metric,value_idmax,value_error[:10])

    def addDatabase(self,database1,value_metric_,value_metric,value_idmax,value_error):
        self.db = QSqlDatabase.addDatabase("QSQLITE", 'sqlite')
        self.db.setDatabaseName(database1)
        self.db.open()
        query = QSqlQuery(self.db) #sql handler
        queryModel = QSqlQueryModel()
        if self.db.open():
            for i in tqdm(value_metric_):
                self.addItem_(i[1],i[2],i[3],i[4],i[5],i[6],i[7],
                               i[8],i[9],i[10],i[11],i[12])
            for j in tqdm(value_metric):
                self.addItem(j[1],j[2],j[3],j[4],j[5],j[6],j[7],
                               j[8],j[9],j[10],j[11],j[12])
            for m in tqdm(value_idmax):
                self.addItemId(m[1],m[2],m[3],m[4])
            for n in tqdm(value_error):
                self.addErrorFile(n[1],n[2],n[3])

    def addItem(self,model_name,dataset_name,class_name,tp,fp,fn,F1,ap,map,prec,recall,thre):
        model_name="\""+model_name+"\""
        dataset_name="\""+dataset_name+"\""
        class_name = "\"" + class_name + "\""
        if self.first_metric:
            id=self.getMaxId()+1
            self.count_metric = id+1
            self.first_metric=False
        else:
            id=self.count_metric
            self.count_metric=id+1
        if self.db.open():
            query = QSqlQuery()
            query.exec_("create table metric(id int primary key, model_name str , dataset_name str,class_name str,"
                        " TP int,FP int,FN int,F1 float,Ap float ,Map float ,Precision float ,Recall float,Threshold float  )")

            query.exec_("insert into metric values("+str(id)+","+model_name+","+dataset_name+","+class_name+","+str(tp)+","+str(fp)+","+str(fn)+","+str(F1)+","+str(ap)+","+str(map)+","+str(prec)+","+str(recall)+","+str(thre)+")")

            # insert_sql = 'insert into student metric (?,?,?)'
            # query.prepare(insert_sql)
            # query.addBindValue(4)
            # query.addBindValue('test3')
            # query.addBindValue(1)
            self.db.close()

    def addItem_(self,model_name,dataset_name,class_name,tp,fp,fn,F1,ap,map,prec,recall,thre):
        model_name="\""+model_name+"\""
        dataset_name="\""+dataset_name+"\""
        class_name = "\"" + class_name + "\""
        if self.first_metric_:
            id = self.getMaxId_() + 1
            self.count_metric_ = id + 1
            self.first_metric_=False
        else:
            id = self.count_metric_
            self.count_metric_ = id + 1
        if self.db.open():
            query = QSqlQuery()
            query.exec_("create table metric_(id int primary key, model_name str , dataset_name str,class_name str,"
                        " TP int,FP int,FN int,F1 float,Ap float ,Map float ,Precision float ,Recall float,Threshold float  )")

            query.exec_("insert into metric_ values("+str(id)+","+model_name+","+dataset_name+","+class_name+","+str(tp)+","+str(fp)+","+str(fn)+","+str(F1)+","+str(ap)+","+str(map)+","+str(prec)+","+str(recall)+","+str(thre)+")")

            # insert_sql = 'insert into student metric (?,?,?)'
            # query.prepare(insert_sql)
            # query.addBindValue(4)
            # query.addBindValue('test3')
            # query.addBindValue(1)
            self.db.close()

    def addItemId(self,model_name,dataset_name,class_name,id_):
        model_name="\""+model_name+"\""
        dataset_name="\""+dataset_name+"\""
        class_name = "\"" + class_name + "\""
        if self.first_id:
            id=self.getMaxIdFromId()+1
            self.count_id = id+1
            self.first_id=False
        else:
            id=self.count_id
            self.count_id=id+1
        if self.db.open():
            query = QSqlQuery()
            query.exec_("create table id_max(id int primary key, model_name str , dataset_name str,class_name str,ID_max int)")

            query.exec_("insert into id_max values("+str(id)+","+model_name+","+dataset_name+","+class_name+","+str(id_)+")")

            # insert_sql = 'insert into student metric (?,?,?)'
            # query.prepare(insert_sql)
            # query.addBindValue(4)
            # query.addBindValue('test3')
            # query.addBindValue(1)
            self.db.close()

    def addErrorFile(self,model_name,dataset_name,error_file):
        model_name="\""+model_name+"\""
        dataset_name="\""+dataset_name+"\""
        error_file = "\"" + error_file + "\""

        if self.first_error:
            id=self.getMaxIdError()+1
            self.count_error = id+1
            self.first_error=False
        else:
            id=self.count_error
            self.count_error=id+1
        if self.db.open():
            # print("保存错误文件")
            query = QSqlQuery()
            query.exec_("create table error(id int primary key, model_name str , dataset_name str,error_file str)")

            # print("insert into error values("+str(id)+","+model_name+","+dataset_name+","+error_file+")")
            query.exec_("insert into error values("+str(id)+","+model_name+","+dataset_name+","+error_file+")")

            # insert_sql = 'insert into student metric (?,?,?)'
            # query.prepare(insert_sql)
            # query.addBindValue(4)
            # query.addBindValue('test3')
            # query.addBindValue(1)
            self.db.close()

    def getMaxId(self):
        self.db.open()
        id_all=[]
        query = QSqlQuery(self.db)
        if query.exec('select id from metric'):
            while query.next():
                id = query.value(0)
                id_all.append(id)
        if len(id_all)==0:
            return 0
        return max(id_all)

    def getMaxId_(self):
        self.db.open()
        id_all=[]
        query = QSqlQuery(self.db)
        if query.exec('select id from metric_'):
            while query.next():
                id = query.value(0)
                id_all.append(id)
        if len(id_all)==0:
            return 0
        return max(id_all)

    def getMaxIdFromId(self):
        self.db.open()
        id_all=[]
        query = QSqlQuery(self.db)
        if query.exec('select id from id_max'):
            while query.next():
                id = query.value(0)
                id_all.append(id)
        if len(id_all)==0:
            return 0
        return max(id_all)

    def getMaxIdError(self):
        self.db.open()
        id_all=[]
        query = QSqlQuery(self.db)
        if query.exec('select id from error'):
            while query.next():
                id = query.value(0)
                id_all.append(id)
        if len(id_all)==0:
            return 0
        return max(id_all)

# DBManagerChanged().merge("/home/fandong/Code/weights/save/main.db","/home/fandong/Code/weights/save/other.db")