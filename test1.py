import csv
import os

from PyQt5 import QtSql

from src.database.db import DBManager

result_csv = []

db_text = os.getcwd() + '/src/database/core'

# 添加一个sqlite数据库连接并打开
db = QtSql.QSqlDatabase.addDatabase('QSQLITE')
db.setDatabaseName('{}.db'.format(db_text))
db.open()
DB = DBManager()
with open('result_2021-10-09_18-52-24.csv', 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        result_csv.append(row)

# each class
class_name = result_csv[4] 
model_name = 'yolov3_best'
dataset_name = 'subDataset'
AP_class, F1_class, prec_class, rec_class, threshold_class, TP_class, FP_class, FN_class = result_csv[
                                                                                               6] , result_csv[7] , \
                                                                                           result_csv[8], \
                                                                                           result_csv[
                                                                                               9] , \
                                                                                           result_csv[
                                                                                               10]  \
    , result_csv[11] , result_csv[12] , result_csv[13] 

TP_all, FP_all, FN_all = 0, 0, 0

for i, name_cl in enumerate(class_name):
    if name_cl == 'class_names ' or name_cl == '':
        continue
    else:
        map_cl = 0
        ap_cl, tp_cl, fp_cl, fn_cl, F1_cl, prec_cl, rec_cl, thre_cl = AP_class[i], TP_class[i], FP_class[i], \
                                                                      FN_class[i], F1_class[i], prec_class[
                                                                          i], rec_class[i], threshold_class[
                                                                          i]
        TP_all += int(tp_cl)
        FP_all += int(fp_cl)
        FN_all += int(fn_cl)

    DB.add_item(model_name, dataset_name, name_cl, tp_cl, fp_cl, fn_cl, F1_cl, ap_cl, map_cl, prec_cl,
                rec_cl, thre_cl)
