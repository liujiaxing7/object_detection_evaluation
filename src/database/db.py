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
        self.db = QSqlDatabase.addDatabase("QSQLITE") #select database type
        self.db.setDatabaseName("/home/fandong/Code/object_detection_evaluation/src/database/core.db") # set database name
        self.db.open()  #connect to or create database
        self.query = QSqlQuery() #sql handler
        self.queryModel = QSqlQueryModel()

    def add_item(self,model_name,map,recall,prec,F1,tp,fp,fn):
        model_name="\""+model_name+"\""
        id=self.get_max_id()+1
        if self.db.open():
            query = QSqlQuery()
            query.exec_("create table metric(id int primary key, model_name str ,  Map float ,Recall float ,Precision float ,F1 float,TP int,FP int,FN int )")

            query.exec_("insert into metric values("+str(id)+","+model_name+","+str(map)+","+str(recall)+","+str(prec)+","+str(F1)+","+str(tp)+","+str(fp)+","+str(fn)+")")

            # insert_sql = 'insert into student metric (?,?,?)'
            # query.prepare(insert_sql)
            # query.addBindValue(4)
            # query.addBindValue('test3')
            # query.addBindValue(1)
            self.db.close()
    def search_item(self):
        self.db.open()
        query = QSqlQuery()
        if query.exec('select id ,model_name,Map,Recall,Precision,F1,TP,FP,FN from metric'):
            while query.next():
                id = query.value(0)
                name = query.value(1)
                map = query.value(2)
                rec = query.value(3)
                prec = query.value(4)
                f1 = query.value(5)
                tp = query.value(5)
                fp = query.value(5)
                fn = query.value(5)
                print(id, name, map,rec,prec,f1,tp,fp,fn)

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
    def draw(self):
        map = []
        recall = []
        Precision = []
        F1_ = []
        index = []
        TP=[]
        FP=[]
        FN=[]
        self.db.open()

        query = QSqlQuery()
        if query.exec('select id ,model_name,Map,Recall,Precision,F1,TP,FP,FN from metric'):
            while query.next():
                id = query.value(0)
                name = query.value(1)
                index.append(name)
                map1 = query.value(2)
                map.append(float(map1))
                rec = query.value(3)
                recall.append(float(rec))
                prec = query.value(4)
                Precision.append(float(prec))
                f1 = query.value(5)
                F1_.append(float(f1))
                tp=query.value(6)
                TP.append(tp)
                fp=query.value(7)
                FP.append(fp)
                fn=query.value(8)
                FN.append(fn)
                print(id, name, map,rec,prec,f1,tp,fp,fn)

        F1 = MyFigure(width=10, height=5, dpi=100)
        F1.fig.suptitle("Metric comparison")
        F1.fig.subplots_adjust(wspace=0.3,hspace=0.5)
        F1.axes0 = F1.fig.add_subplot(244)
        F1.axes1 = F1.fig.add_subplot(243)
        F1.axes2 = F1.fig.add_subplot(242)
        F1.axes3 = F1.fig.add_subplot(241)
        F1.axes4 = F1.fig.add_subplot(245)
        F1.axes5 = F1.fig.add_subplot(246)
        F1.axes6 = F1.fig.add_subplot(247)
        F1.axes0.bar(index, map)
        F1.axes1.bar(index, recall)
        F1.axes2.bar(index, Precision)
        F1.axes3.bar(index, F1_)
        F1.axes4.bar(index, TP)
        F1.axes5.bar(index, FP)
        F1.axes6.bar(index, FN)
        # F1.axes.legend()
        # F1.axes4.xlabel("model")
        F1.axes0.set_title("Map")
        F1.axes1.set_title("recall")
        F1.axes2.set_title("Prediction")
        F1.axes3.set_title("F1")
        F1.axes4.set_title("TP")
        F1.axes5.set_title("FP")
        F1.axes6.set_title("FN")

        return F1


