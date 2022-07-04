import os
from collections import defaultdict

from PyQt5.QtSql import QSqlQuery,QSqlDatabase,QSqlQueryModel
import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class MyFigure(FigureCanvas):
    def __init__(self,width=10, height=8, dpi=100):

        self.fig = Figure(figsize=(width, height), dpi=dpi)

        super(MyFigure,self).__init__(self.fig)

classNames=["all","person","escalator","escalator_handrails","person_dummy","escalator_model","escalator_handrails_model",'__background__', 'shoes', 'bin', 'pedestal', 'wire', 'socket','robot','i18R-DVT','i18R-EVT','rbn100-EVT']

class DBManager():
    def __init__(self):
        # self.db = QSqlDatabase.addDatabase("QSQLITE",'sqlite') #select database type
        self.db = QSqlDatabase.addDatabase("QSQLITE") #select database type
        db_path= os.getcwd()+'/src/database/core.db'
        self.db.setDatabaseName(db_path) # set database name
        self.db.open()  #connect to or create database
        self.query = QSqlQuery() #sql handler
        self.queryModel = QSqlQueryModel()
        self.first_metric = True
        self.first_metric_ = True
        self.first_id = True
        self. first_error = True

        self. count_metric = 0
        self. count_metric_ = 0
        self. count_id = 0
        self. count_error = 0

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
        if str(class_name) not in classNames:
            return
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
        if str(error_file) in classNames:
            return
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

    def searchClasses(self,name):
        classes=[]
        self.db.open()
        query = QSqlQuery()
        if query.exec(
                'select id ,model_name,dataset_name,class_name,TP,FP,FN,F1,Ap,Map,Precision,Recall,Threshold from metric'):
            while query.next():
                value = [query.value(i) for i in range(13)]
                id, model_name, dataset_name, class_name, tp, fp, fn, f1, Ap, Map, prec, rec, Threshold = value
                if model_name=='yolov3_prune' or model_name=='yolov3_best':
                    continue
                if dataset_name==name or model_name==name:
                    if class_name in classes:
                        continue
                    else:
                        classes.append(class_name)
                # print(id, model_name, dataset_name, class_name, tp, fp, fn, f1, Ap, Map, prec, rec, Threshold)
        return classes

    def searchAllClasses(self):
        classes=[]
        self.db.open()
        query = QSqlQuery()
        if query.exec(
                'select id ,model_name,dataset_name,class_name,TP,FP,FN,F1,Ap,Map,Precision,Recall,Threshold from metric'):
            while query.next():
                value = [query.value(i) for i in range(13)]
                id, model_name, dataset_name, class_name, tp, fp, fn, f1, Ap, Map, prec, rec, Threshold = value
                if model_name=='yolov3_prune' or model_name=='yolov3_best':
                    continue
                if class_name == 'all':
                    break
                if class_name in classes:
                    continue
                else:
                    classes.append(class_name)
                # print(id, model_name, dataset_name, class_name, tp, fp, fn, f1, Ap, Map, prec, rec, Threshold)
        return classes

    def searchModelDatasets(self):
        models=[]
        datasets=[]
        self.db.open()
        query = QSqlQuery()
        if query.exec(
                'select id ,model_name,dataset_name,class_name,TP,FP,FN,F1,Ap,Map,Precision,Recall,Threshold from metric'):
            while query.next():

                value = [query.value(i) for i in range(13)]
                id, model_name, dataset_name, class_name, tp, fp, fn, f1, Ap, Map, prec, rec, Threshold = value
                if model_name=='yolov3_prune' or model_name=='yolov3_best':
                    continue
                tmp_model_flag = 0
                tmp_dataset_flag = 0
                for index_model in models:
                    if model_name == index_model:
                        tmp_model_flag = 1
                        break
                if tmp_model_flag == 0:
                    models.append(model_name)
                for index_dataset in datasets:
                    if str(dataset_name) == index_dataset:
                        tmp_dataset_flag = 1
                        break
                if tmp_dataset_flag == 0:
                    datasets.append(str(dataset_name))


                # print(id, model_name, dataset_name, class_name, tp, fp, fn, f1, Ap, Map, prec, rec, Threshold)
        return models,datasets

    def searchId(self):
        id_list=defaultdict(list)
        class_num=defaultdict(list)
        datasets=[]
        self.db.open()
        query = QSqlQuery()
        if query.exec(
                'select id ,model_name,dataset_name,class_name,ID_max from id_max'):
            while query.next():
                value = [query.value(i) for i in range(5)]
                id, model_name, dataset_name, class_name, id1 = value

                id_list[str(model_name)+'$'+str(dataset_name)].append(id1)
                if not class_name in class_num:
                    class_num[str(model_name)+'$'+str(dataset_name)].append(class_name)
                if not str(dataset_name) in datasets:
                    datasets.append(str(dataset_name))
                # print(id, model_name, dataset_name, class_name, tp, fp, fn, f1, Ap, Map, prec, rec, Threshold)
        return id_list,class_num,datasets

    def searchMatchedModelsDatasetsClasses(self):
        model_dataset_dict = defaultdict(list)
        model_classes_dict = defaultdict(list)
        self.db.open()
        query = QSqlQuery()
        if query.exec(
                'select id ,model_name,dataset_name,class_name,ID_max from id_max'):
            while query.next():
                value = [query.value(i) for i in range(5)]
                id, model_name, dataset_name, class_name, id1 = value
                if model_name not in model_dataset_dict:
                    model_dataset_dict[model_name] = []
                if not str(dataset_name) in model_dataset_dict[model_name]:
                    model_dataset_dict[model_name].append(str(dataset_name))
                if model_name not in model_classes_dict:
                    model_classes_dict[model_name] = []
                if not class_name in model_classes_dict[model_name]:
                    model_classes_dict[model_name].append(class_name)
        return model_dataset_dict, model_classes_dict

    def searchError(self):
        error_dic = defaultdict(list)
        eror_id = defaultdict(list)
        self.db.open()
        query = QSqlQuery()
        if query.exec(
                'select id ,model_name,dataset_name,error_file from error'):
            while query.next():
                value = [query.value(i) for i in range(4)]
                id, model_name, dataset_name, file = value
                error_dic[str(model_name)+'$'+str(dataset_name)].append(file)
                eror_id[str(model_name)+'$'+str(dataset_name)].append(id)
        return eror_id, error_dic

    def getMaxId(self):
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

    def getMaxId_(self):
        self.db.open()
        id_all=[]
        query = QSqlQuery()
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
        query = QSqlQuery()
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
        query = QSqlQuery()
        if query.exec('select id from error'):
            while query.next():
                id = query.value(0)
                id_all.append(id)
        if len(id_all)==0:
            return 0
        return max(id_all)

    def drawByModel(self,models,datasets,classses):
        map,ap,recall,Precision,F1_,index,TP,FP,FN,Thre = [],[],[],[],[],[],[],[],[],[]

        self.db.open()
        query = QSqlQuery()
        if query.exec('select id ,model_name,dataset_name,class_name,TP,FP,FN,F1,Ap,Map,Precision,Recall,Threshold from metric'):
            while query.next():
                value=[query.value(i) for i in range(13)]
                id,model_name,dataset_name,class_name,tp,fp,fn,f1,Ap,Map,prec,rec,Threshold = value
                if model_name in models and class_name==classses and dataset_name==datasets:

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

        for a, b, i in zip(index, map, range(len(index))):  # zip 函数
            F1.axes0.text(a, b - map[i] / 10, "%.2f" % map[i], ha='center', fontsize=10)  # plt.text 函数
        for a, b, i in zip(index, recall, range(len(index))):  # zip 函数
            F1.axes1.text(a, b - recall[i] / 10, "%.2f" % recall[i], ha='center', fontsize=10)  # plt.text 函数
        for a, b, i in zip(index, Precision, range(len(index))):  # zip 函数
            F1.axes2.text(a, b - Precision[i] / 10, "%.2f" % Precision[i], ha='center',
                                fontsize=10)  # plt.text 函数
        for a, b, i in zip(index, F1_, range(len(index))):  # zip 函数
            F1.axes3.text(a, b - F1_[i] / 10, "%.2f" % F1_[i], ha='center', fontsize=10)  # plt.text 函数
        for a, b, i in zip(index, TP, range(len(index))):  # zip 函数
            F1.axes4.text(a, b - TP[i] / 10, "%.2f" % TP[i], ha='center', fontsize=10)  # plt.text 函数
        for a, b, i in zip(index, FP, range(len(index))):  # zip 函数
            F1.axes5.text(a, b - FP[i] / 10, "%.2f" % FP[i], ha='center', fontsize=10)  # plt.text 函数
        for a, b, i in zip(index, FN, range(len(index))):  # zip 函数
            F1.axes6.text(a, b - FN[i] / 10, "%.2f" % FN[i], ha='center', fontsize=10)  # plt.text 函数
        for a, b, i in zip(index, ap, range(len(index))):  # zip 函数
            F1.axes7.text(a, b - ap[i] / 10, "%.2f" % ap[i], ha='center', fontsize=10)  # plt.text 函数
        for a, b, i in zip(index, Thre, range(len(index))):  # zip 函数
            F1.axes8.text(a, b - Thre[i] / 10, "%.2f" % Thre[i], ha='center', fontsize=10)  # plt.text 函数
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

    def drawByData(self,models,datasets,classses):
        map,ap,recall,Precision,F1_,index,TP,FP,FN,Thre = [],[],[],[],[],[],[],[],[],[]

        self.db.open()
        query = QSqlQuery()
        if query.exec('select id ,model_name,dataset_name,class_name,TP,FP,FN,F1,Ap,Map,Precision,Recall,Threshold from metric'):
            while query.next():
                value=[query.value(i) for i in range(13)]
                id,model_name,dataset_name,class_name,tp,fp,fn,f1,Ap,Map,prec,rec,Threshold = value
                if dataset_name in datasets and class_name==classses and model_name==models:

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

        for a, b, i in zip(index, map, range(len(index))):  # zip 函数
            F1.axes0.text(a, b - map[i] / 10, "%.2f" % map[i], ha='center', fontsize=10)  # plt.text 函数
        for a, b, i in zip(index, recall, range(len(index))):  # zip 函数
            F1.axes1.text(a, b - recall[i] / 10, "%.2f" % recall[i], ha='center', fontsize=10)  # plt.text 函数
        for a, b, i in zip(index, Precision, range(len(index))):  # zip 函数
            F1.axes2.text(a, b - Precision[i] / 10, "%.2f" % Precision[i], ha='center',
                                fontsize=10)  # plt.text 函数
        for a, b, i in zip(index, F1_, range(len(index))):  # zip 函数
            F1.axes3.text(a, b - F1_[i] / 10, "%.2f" % F1_[i], ha='center', fontsize=10)  # plt.text 函数
        for a, b, i in zip(index, TP, range(len(index))):  # zip 函数
            F1.axes4.text(a, b - TP[i] / 10, "%.2f" % TP[i], ha='center', fontsize=10)  # plt.text 函数
        for a, b, i in zip(index, FP, range(len(index))):  # zip 函数
            F1.axes5.text(a, b - FP[i] / 10, "%.2f" % FP[i], ha='center', fontsize=10)  # plt.text 函数
        for a, b, i in zip(index, FN, range(len(index))):  # zip 函数
            F1.axes6.text(a, b - FN[i] / 10, "%.2f" % FN[i], ha='center', fontsize=10)  # plt.text 函数
        for a, b, i in zip(index, ap, range(len(index))):  # zip 函数
            F1.axes7.text(a, b - ap[i] / 10, "%.2f" % ap[i], ha='center', fontsize=10)  # plt.text 函数
        for a, b, i in zip(index, Thre, range(len(index))):  # zip 函数
            F1.axes8.text(a, b - Thre[i] / 10, "%.2f" % Thre[i], ha='center', fontsize=10)  # plt.text 函数

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


