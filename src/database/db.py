import os

from PyQt5.QtSql import QSqlQuery,QSqlDatabase,QSqlQueryModel
import matplotlib
matplotlib.use("Qt5Agg")  # 声明使用QT5
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
class MyFigure(FigureCanvas):
    def __init__(self,width=10, height=8, dpi=100):

        self.fig = Figure(figsize=(width, height), dpi=dpi)

        super(MyFigure,self).__init__(self.fig)

class DBManager():
    def __init__(self):
        self.db = QSqlDatabase.addDatabase("QSQLITE",'sqlite') #select database type
        db_path= os.getcwd()+'/src/database/core.db'
        self.db.setDatabaseName(db_path) # set database name
        self.db.open()  #connect to or create database
        self.query = QSqlQuery() #sql handler
        self.queryModel = QSqlQueryModel()

#id, model_name, dataset, class, [f1, fp, tp, fn, map, prec, recall], threshold(best select by f1)
    def add_item(self,model_name,dataset_name,class_name,tp,fp,fn,F1,ap,map,prec,recall,thre):
        model_name="\""+model_name+"\""
        dataset_name="\""+dataset_name+"\""
        class_name = "\"" + class_name + "\""
        id=self.get_max_id()+1
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
    def search_classes(self,name):
        classes=[]
        self.db.open()
        query = QSqlQuery()
        if query.exec(
                'select id ,model_name,dataset_name,class_name,TP,FP,FN,F1,Ap,Map,Precision,Recall,Threshold from metric'):
            while query.next():
                value = [query.value(i) for i in range(13)]
                id, model_name, dataset_name, class_name, tp, fp, fn, f1, Ap, Map, prec, rec, Threshold = value
                if dataset_name==name or model_name==name:
                    if class_name in classes:
                        continue
                    else:
                        classes.append(class_name)
                print(id, model_name, dataset_name, class_name, tp, fp, fn, f1, Ap, Map, prec, rec, Threshold)
        return classes
    def get_max_id(self):
        self.db.open()
        id_all=[]
        query = QSqlQuery()
        if query.exec('select id from metric'):
            while query.next():
                id = query.value(0)
                id_all.append(id)
        if len(id_all)==0:
            return 0
        return max(id_all)
    def draw_by_data(self,datasets,classses):
        map,ap,recall,Precision,F1_,index,TP,FP,FN,Thre = [],[],[],[],[],[],[],[],[],[]

        self.db.open()
        query = QSqlQuery()
        if query.exec('select id ,model_name,dataset_name,class_name,TP,FP,FN,F1,Ap,Map,Precision,Recall,Threshold from metric'):
            while query.next():
                value=[query.value(i) for i in range(13)]
                id,model_name,dataset_name,class_name,tp,fp,fn,f1,Ap,Map,prec,rec,Threshold = value
                if dataset_name==datasets and class_name==classses:

                    index.append(model_name)
                    map.append(float(Map))
                    ap.append(float(Ap))
                    recall.append(float(rec))
                    Precision.append(float(prec))
                    F1_.append(float(f1))
                    TP.append(tp)
                    FP.append(fp)
                    FN.append(fn)
                    Thre.append(float(Threshold))

        F1 = MyFigure(width=10, height=5, dpi=100)
        F1.fig.suptitle("Metric comparison")
        F1.fig.subplots_adjust(wspace=0.3,hspace=0.5)
        F1.axes0 = F1.fig.add_subplot(258)
        F1.axes1 = F1.fig.add_subplot(256)
        F1.axes2 = F1.fig.add_subplot(255)
        F1.axes3 = F1.fig.add_subplot(251)
        F1.axes4 = F1.fig.add_subplot(252)
        F1.axes5 = F1.fig.add_subplot(253)
        F1.axes6 = F1.fig.add_subplot(254)
        F1.axes7 = F1.fig.add_subplot(257)
        F1.axes8 = F1.fig.add_subplot(259)
        # F1.axes9 = F1.fig.add_subplot(260)
        F1.axes0.bar(index, map)
        F1.axes1.bar(index, recall)
        F1.axes2.bar(index, Precision)
        F1.axes3.bar(index, F1_)
        F1.axes4.bar(index, TP)
        F1.axes5.bar(index, FP)
        F1.axes6.bar(index, FN)
        F1.axes7.bar(index, ap)
        F1.axes8.bar(index, Thre)
        # F1.axes9.bar(index, FN)
        # F1.axes.legend()
        # F1.axes4.xlabel("model")
        F1.axes0.set_title("Map")
        F1.axes1.set_title("recall")
        F1.axes2.set_title("Prediction")
        F1.axes3.set_title("F1")
        F1.axes4.set_title("TP")
        F1.axes5.set_title("FP")
        F1.axes6.set_title("FN")
        F1.axes7.set_title("Ap")
        F1.axes8.set_title("Threshold")

        return F1

    def draw_by_model(self,models,classses):
        map,ap,recall,Precision,F1_,index,TP,FP,FN,Thre = [],[],[],[],[],[],[],[],[],[]

        self.db.open()
        query = QSqlQuery()
        if query.exec('select id ,model_name,dataset_name,class_name,TP,FP,FN,F1,Ap,Map,Precision,Recall,Threshold from metric'):
            while query.next():
                value=[query.value(i) for i in range(13)]
                id,model_name,dataset_name,class_name,tp,fp,fn,f1,Ap,Map,prec,rec,Threshold = value
                if model_name==models and class_name==classses:

                    index.append(dataset_name)
                    map.append(float(Map))
                    ap.append(float(Ap))
                    recall.append(float(rec))
                    Precision.append(float(prec))
                    F1_.append(float(f1))
                    TP.append(tp)
                    FP.append(fp)
                    FN.append(fn)
                    Thre.append(float(Threshold))

        F1 = MyFigure(width=10, height=5, dpi=100)
        F1.fig.suptitle("Metric comparison")
        F1.fig.subplots_adjust(wspace=0.3,hspace=0.5)
        F1.axes0 = F1.fig.add_subplot(258)
        F1.axes1 = F1.fig.add_subplot(256)
        F1.axes2 = F1.fig.add_subplot(255)
        F1.axes3 = F1.fig.add_subplot(251)
        F1.axes4 = F1.fig.add_subplot(252)
        F1.axes5 = F1.fig.add_subplot(253)
        F1.axes6 = F1.fig.add_subplot(254)
        F1.axes7 = F1.fig.add_subplot(257)
        F1.axes8 = F1.fig.add_subplot(259)
        # F1.axes9 = F1.fig.add_subplot(260)
        F1.axes0.bar(index, map)
        F1.axes1.bar(index, recall)
        F1.axes2.bar(index, Precision)
        F1.axes3.bar(index, F1_)
        F1.axes4.bar(index, TP)
        F1.axes5.bar(index, FP)
        F1.axes6.bar(index, FN)
        F1.axes7.bar(index, ap)
        F1.axes8.bar(index, Thre)
        # F1.axes9.bar(index, FN)
        # F1.axes.legend()
        # F1.axes4.xlabel("model")
        F1.axes0.set_title("Map")
        F1.axes1.set_title("recall")
        F1.axes2.set_title("Prediction")
        F1.axes3.set_title("F1")
        F1.axes4.set_title("TP")
        F1.axes5.set_title("FP")
        F1.axes6.set_title("FN")
        F1.axes7.set_title("Ap")
        F1.axes8.set_title("Threshold")

        return F1


