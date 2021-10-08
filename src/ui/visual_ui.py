# -*- coding: utf-8 -*-
'''
@author: 刘家兴
@contact: ljx0ml@163.com
@file: model.py
@time: 2021/8/24 18.46
@desc:
'''
from decimal import Decimal
import time, threading

from PyQt5 import QtGui, QtCore, QtWidgets, QtSql
from PyQt5.QtCore import Qt, QRect, QThread, pyqtSignal
from PyQt5.QtSql import QSqlQuery
from PyQt5.QtWidgets import *

import os
import sys
from cv2 import cv2
import onnx
import numpy as np
import matplotlib
from tqdm import tqdm

# matplotlib.use("Qt5Agg")
from src.database.db import DBManager

class EmptyDelegate(QItemDelegate):
    def __init__(self, parent):
        super(EmptyDelegate, self).__init__(parent)

    def createEditor(self, QWidget, QStyleOptionViewItem, QModelIndex):
        return None


def nanstr(a, i):
    if a is None:
        return 0.0
    elif type(a) == float:
        return np.nan_to_num(a)
    elif a[i] is None:
        return 0.0
    else:
        return a[i]


class Ui_Window(QTabWidget):
    def __init__(self, parent=None):
        super(Ui_Window, self).__init__(parent)
        # set window size
        self.setGeometry(300, 300, 1380, 800)

        self.current_directory = os.path.dirname(os.path.realpath(__file__))
        # Define error msg dialog
        self.msgBox = QMessageBox()

        # Default values
        self.dir_model_gt = None
        self.dir_images_gt = None
        self.filepath_classes_gt = None
        self.dir_dets = None
        self.filepath_classes_det = None
        self.dir_save_results = None
        self.ret = ''
        self.process_method = ''
        self.result_csv = None
        self.result = None
        self.class_name_draw = None

        self.center_screen()
        # sys.stdout = Stream(newText=self.onUpdateText)
        
        db_text = os.getcwd() + '/src/database/core'

        # 添加一个sqlite数据库连接并打开
        db = QtSql.QSqlDatabase.addDatabase('QSQLITE')
        db.setDatabaseName('{}.db'.format(db_text))
        db.open()
        self.DBManager = DBManager()

        self.tab1 = QtWidgets.QWidget()
        self.tab2 = QtWidgets.QWidget()
        self.tab3 = QtWidgets.QWidget()
        self.tab4 = QtWidgets.QWidget()
        self.addTab(self.tab1, "Detection Metrics")
        self.addTab(self.tab2, "Visual Comparsion")
        self.addTab(self.tab3, "Show Database")
        self.addTab(self.tab4, "Error File Preview")
        self.tab1UI()
        self.tab2UI()
        self.tab3UI()
        self.tab4UI()
        self.setWindowTitle("Object Detection Metrics")

    def tab1UI(self):
        layout = QFormLayout()

        gt = QHBoxLayout()
        font = QtGui.QFont()
        font.setBold(True)
        font.setPixelSize(25)
        gt_label = QLabel("Ground truth")
        gt.addWidget(gt_label, 1, Qt.AlignCenter)

        gt_label.setFont(font)
        layout.addRow(gt)

        h1 = QHBoxLayout()
        h1.addWidget(QLabel("Model:       "))
        self.txb_gt_dir = QLineEdit()
        self.txb_gt_dir.setReadOnly(True)
        h1.addWidget(self.txb_gt_dir)
        self.load_model_dir = QPushButton("...")
        h1.addWidget(self.load_model_dir)
        self.load_model_dir.clicked.connect(self.btn_gt_dir_clicked)
        layout.addRow(h1)

        h2 = QHBoxLayout()
        h2.addWidget(QLabel("Images:     "))
        self.txb_gt_images_dir = QLineEdit()
        self.txb_gt_images_dir.setReadOnly(True)
        h2.addWidget(self.txb_gt_images_dir)
        self.load_images_dir = QPushButton("...")
        h2.addWidget(self.load_images_dir)
        self.load_images_dir.clicked.connect(self.btn_gt_images_dir_clicked)
        layout.addRow(h2)

        h3 = QHBoxLayout()
        h3.addWidget(QLabel("Classes(*):"))
        self.txb_classes_gt = QLineEdit()
        self.txb_classes_gt.setReadOnly(True)
        h3.addWidget(self.txb_classes_gt)
        self.load_class_dir = QPushButton("...")
        h3.addWidget(self.load_class_dir)
        self.load_class_dir.clicked.connect(self.btn_gt_classes_clicked)
        layout.addRow(h3)
        layout.addRow(QLabel("                     * required for yolo (.txt) format only."))
        layout.addRow(QLabel(''))

        h4 = QVBoxLayout()
        format_w = QWidget()
        frame = QFrame(format_w)
        frame.setMinimumSize(2000, 100)
        frame.setStyleSheet("background-color: #feeeed")

        h4_1 = QHBoxLayout()
        gt_format = QLabel("Coordinates format:")
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        gt_format.setFont(font)
        h4_1.addWidget(gt_format)
        h4.addLayout(h4_1)

        h4_2 = QHBoxLayout()
        self.rad_gt_format_coco_json = QRadioButton("COCO (.json)")
        self.rad_gt_format_pascalvoc_xml = QRadioButton("PASCAL VOC (.xml)")
        self.rad_gt_format_labelme_xml = QRadioButton("Label Me (.xml)")
        self.rad_gt_format_yolo_text = QRadioButton("(*) YOLO (.txt)")
        h4_2.addWidget(self.rad_gt_format_coco_json)
        h4_2.addWidget(self.rad_gt_format_pascalvoc_xml)
        h4_2.addWidget(self.rad_gt_format_labelme_xml)
        h4_2.addWidget(self.rad_gt_format_yolo_text)
        h4.addLayout(h4_2)

        format_w.setLayout(h4)
        layout.addWidget(format_w)
        layout.addRow(QLabel(' '))

        h5 = QHBoxLayout()
        h5.addWidget(QLabel("Onnx Model Type:"), 1, Qt.AlignLeft)
        self.combobox_process = QComboBox()
        h5.addWidget(self.combobox_process, 5, Qt.AlignLeft)
        self.combobox_process.addItems(['', 'yolov3', 'yolov5', 'yolov3_tiny3'])
        self.combobox_process.setMinimumSize(200, 27)
        self.combobox_process.currentIndexChanged.connect(self.comboSelectionChanged)
        btn_save = QPushButton("save")
        h5.addWidget(btn_save, 1, Qt.AlignRight)
        btn_save.setMinimumSize(60, 27)
        btn_save.clicked.connect(self.btn_save_clicked)
        layout.addRow(h5)

        self.process = QTextEdit()
        layout.addRow(self.process)

        [layout.addRow(QLabel('')) for i in range(10)]

        h6 = QHBoxLayout()
        self.btn_run = QPushButton("RUN")
        self.btn_run.clicked.connect(self.btn_run_clicked)
        h6.addWidget(self.btn_run)
        self.btn_run.setStyleSheet(
            '''QPushButton{background:#afb4db;border-radius:5px;}QPushButton:hover{background:#9b95c9;}''')

        layout.addRow(h6)

        self.tab1.setLayout(layout)

    def tab2UI(self):
        layout = QFormLayout()

        gt = QHBoxLayout()
        font = QtGui.QFont()
        font.setBold(True)
        font.setPixelSize(25)
        gt_label = QLabel("Visual Comparsion")
        gt.addWidget(gt_label, 1, Qt.AlignCenter)
        gt_label.setFont(font)
        layout.addRow(gt, )
        layout.addRow(QLabel(''))

        h2 = QHBoxLayout()
        h2.addWidget(QLabel("Load classes:"), 1, Qt.AlignLeft)
        self.combobox_classes = QComboBox()
        self.combobox_classes.setMinimumSize(200, 27)
        self.combobox_classes.currentIndexChanged.connect(self.comboSelectionChanged1)
        h2.addWidget(self.combobox_classes, 5, Qt.AlignLeft)
        self.load_class_dir = QPushButton("Load ...")
        self.load_class_dir.setMinimumSize(60, 27)
        h2.addWidget(self.load_class_dir, 1, Qt.AlignRight)
        self.load_class_dir.clicked.connect(self.btn_show_classes_clicked)
        self.btn_draw = QPushButton("Draw")
        self.btn_draw.setMinimumSize(80, 27)
        h2.addWidget(self.btn_draw, 1, Qt.AlignRight)
        self.btn_draw.clicked.connect(self.btn_draw_clicked)
        layout.addRow(h2)

        h1 = QGridLayout()
        group_box = QtWidgets.QGroupBox('Model')
        self.group_box_layout = QtWidgets.QHBoxLayout()
        group_box.setLayout(self.group_box_layout)

        group_box.setMinimumSize(100, 10)
        h1.addWidget(group_box, 0, 0, 1, 2)

        group_box1 = QtWidgets.QGroupBox('Datasets')
        self.group_box_layout1 = QtWidgets.QVBoxLayout()
        group_box1.setLayout(self.group_box_layout1)

        group_box1.setMaximumSize(130, 1000)
        # layout.addChildLayout(h1)
        h1.addWidget(group_box1, 1, 0)
        self.btn_load_md()

        self.draw_grid = QWidget()
        groupBox = QGroupBox(self.draw_grid)
        self.gridlayout = QGridLayout(groupBox)
        self.draw_grid.setLayout(self.gridlayout)
        self.draw_grid.setVisible(False)
        h1.addWidget(self.draw_grid, 1, 1)
        layout.addRow(h1)

        self.tab2.setLayout(layout)

    def tab3UI(self):

        layout = QFormLayout()
        gt = QHBoxLayout()
        font = QtGui.QFont()
        font.setBold(True)
        font.setPixelSize(25)
        gt_label = QLabel("Show Database")
        gt.addWidget(gt_label, 1, Qt.AlignCenter)
        gt_label.setFont(font)
        layout.addRow(gt)
        layout.addRow(QLabel(''))

        h1 = QHBoxLayout()
        h1.addWidget(QLabel("Datasets name："))
        self.data_line_ui3 = QLineEdit()
        h1.addWidget(self.data_line_ui3)
        search_by_data = QPushButton("Search by Data")
        h1.addWidget(search_by_data)
        search_by_data.clicked.connect(self.btn_search_by_data)
        h1.addWidget(QLabel(" Models name："))
        self.model_line_ui3 = QLineEdit()
        h1.addWidget(self.model_line_ui3)
        search_by_model = QPushButton("Search by Model")
        h1.addWidget(search_by_model)
        search_by_model.clicked.connect(self.btn_search_by_model)
        h1.addWidget(QLabel(" Filter condition："))
        self.filter_line_ui3 = QLineEdit()
        h1.addWidget(self.filter_line_ui3)
        search_by_filter = QPushButton("Search by condition")
        h1.addWidget(search_by_filter)
        search_by_filter.clicked.connect(self.btn_search_by_filter1)
        refresh = QPushButton("Refresh")
        h1.addWidget(refresh)
        refresh.clicked.connect(self.btn_refresh)
        layout.addRow(h1)

        h3 = QGridLayout()
        self.table_widget = QtWidgets.QTableView()
        self.table_widget.setFixedSize(1340, 600)

        query = QSqlQuery()
        self.value = []
        if query.exec(
                'select id ,model_name,dataset_name,class_name,TP,FP,FN,F1,Ap,Map,Precision,Recall,Threshold from metric_'):
            while query.next():
                value_ = [query.value(i) for i in range(13)]
                self.value.append(value_)

        self.model = QtGui.QStandardItemModel()

        self.table_widget.setModel(self.model)
        # self.table_widget.setColumnWidth(0, 50)
        self.table_widget.setSortingEnabled(True)

        self.model.itemChanged.connect(self.QStandardModelItemChanged)
        self.table_widget.doubleClicked.connect(self.doubleClicked)
        if len(self.value) != 0:
            self.btn_refresh()
        for i in range(12):
            self.table_widget.setItemDelegateForColumn(i, EmptyDelegate(self))
        self.table_widget.setEditTriggers(QAbstractItemView.AllEditTriggers)

        h3.addWidget(self.table_widget)
        layout.addRow(h3)

        self.tab3.setLayout(layout)

    def tab4UI(self):

        layout = QFormLayout()
        gt = QHBoxLayout()
        font = QtGui.QFont()
        font.setBold(True)
        font.setPixelSize(25)
        gt_label = QLabel("Error File")
        gt.addWidget(gt_label, 1, Qt.AlignCenter)
        gt_label.setFont(font)
        layout.addRow(gt)
        layout.addRow(QLabel(''))

        h1 = QHBoxLayout()
        h1.addWidget(QLabel("Datasets name："))
        self.data_line_ui4 = QLineEdit()
        h1.addWidget(self.data_line_ui4)
        search_by_data = QPushButton("Search by Data")
        h1.addWidget(search_by_data)
        search_by_data.clicked.connect(self.btn_search_by_data_error)
        h1.addWidget(QLabel(" Models name："))
        self.model_line_ui4 = QLineEdit()
        h1.addWidget(self.model_line_ui4)
        search_by_model = QPushButton("Search by Model")
        h1.addWidget(search_by_model)
        search_by_model.clicked.connect(self.btn_search_by_model_error)
        h1.addWidget(QLabel(" Filter condition："))
        self.filter_line_ui4 = QLineEdit()
        h1.addWidget(self.filter_line_ui4)
        search_by_filter = QPushButton("Search by condition")
        h1.addWidget(search_by_filter)
        search_by_filter.clicked.connect(self.btn_search_by_filter_error)
        refresh = QPushButton("Refresh")
        h1.addWidget(refresh)
        refresh.clicked.connect(self.btn_refresh_error)
        layout.addRow(h1)

        h2 = QGridLayout()
        self.table_widget1 = QtWidgets.QTableView()
        self.table_widget1.setFixedSize(1370, 600)
        db_text = os.getcwd() + '/src/database/core'

        # 实例化一个可编辑数据模型
        self.model1 = QtSql.QSqlTableModel()

        self.table_widget1.setModel(self.model1)
        self.table_widget1.setSortingEnabled(True)
        self.table_widget1.doubleClicked.connect(self.show_error_file)

        self.model1.setTable('error')  # 设置数据模型的数据表
        self.model1.setEditStrategy(False)  # 允许字段更改
        self.model1.select()  # 查询所有数据
        # 设置表格头
        self.model1.setHeaderData(0, QtCore.Qt.Horizontal, 'ID')
        self.model1.setHeaderData(1, QtCore.Qt.Horizontal, 'Model')
        self.model1.setHeaderData(2, QtCore.Qt.Horizontal, 'dataset')
        self.model1.setHeaderData(3, QtCore.Qt.Horizontal, 'Error file')
        self.table_widget1.setColumnWidth(3, 1035)
        for i in range(4):
            self.table_widget.setItemDelegateForColumn(i, EmptyDelegate(self))
        h2.addWidget(self.table_widget1)
        layout.addRow(h2)

        self.tab4.setLayout(layout)

    def doubleClicked(self, index):
        self.table_widget.openPersistentEditor(index)

    def onUpdateText(self, text):
        """Write console output to text widget."""
        cursor = self.process.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.process.setTextCursor(cursor)
        self.process.ensureCursorVisible()

    def center_screen(self):
        size = self.size()
        desktopSize = QtWidgets.QDesktopWidget().screenGeometry()
        top = (desktopSize.height() / 2) - (size.height() / 2)
        left = (desktopSize.width() / 2) - (size.width() / 2)
        self.move(left, top)

    def closeEvent(self, event):
        conf = self.show_popup('Are you sure you want to close the program?',
                               'Closing',
                               buttons=QMessageBox.Yes | QMessageBox.No,
                               icon=QMessageBox.Question)
        if conf == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def show_popup(self,
                   message,
                   title,
                   buttons=QMessageBox.Ok | QMessageBox.Cancel,
                   icon=QMessageBox.Information):
        self.msgBox.setIcon(icon)
        self.msgBox.setText(message)
        self.msgBox.setWindowTitle(title)
        self.msgBox.setStandardButtons(buttons)
        return self.msgBox.exec()

    def comboSelectionChanged(self, index):
        text = self.combobox_process.itemText(index)
        if text == 'yolov3':
            self.process_method = 'yolov3'
        elif text == 'yolov5':
            self.process_method = 'yolov5'
        elif text == 'yolov3_tiny3':
            self.process_method = 'yolov3_tiny3'

    def comboSelectionChanged1(self, index):
        text = self.combobox_classes.itemText(index)
        if text == '':
            print(1)
        else:
            self.class_name_draw = text
            self.btn_draw_clicked()

    def load_annotations_gt(self):

        if self.rad_gt_format_coco_json.isChecked():
            self.ret = 'coco'
        elif self.rad_gt_format_pascalvoc_xml.isChecked():
            self.ret = 'voc'
        elif self.rad_gt_format_yolo_text.isChecked():
            self.ret = 'darknet'
        if self.ret == '':
            print("no format select")
            exit(-1)

    def btn_gt_statistics_clicked(self):
        pass

    def btn_gt_dir_clicked(self):
        if self.txb_gt_dir.text() == '':
            txt = self.current_directory
        else:
            txt = self.txb_gt_dir.text()
        directory = QFileDialog.getOpenFileName(
            self, 'Choose file with onnx model', txt)
        if directory == '':
            return
        file_path = directory[0]
        if os.path.isfile(file_path):
            self.txb_gt_dir.setText(file_path)
            self.dir_model_gt = file_path
        else:
            self.dir_model_gt = None
            self.txb_gt_dir.setText('')

    def btn_gt_classes_clicked(self):
        filepath = QFileDialog.getOpenFileName(self, 'Choose a file with a list of classes',
                                               self.current_directory,
                                               "Image files (*.txt *.names)")
        filepath = filepath[0]
        if os.path.isfile(filepath):
            self.txb_classes_gt.setText(filepath)
            self.filepath_classes_gt = filepath
        else:
            self.filepath_classes_gt = None

    def btn_gt_images_dir_clicked(self):
        if self.txb_gt_images_dir.text() == '':
            txt = self.current_directory
        else:
            txt = self.txb_gt_images_dir.text()
        directory = QFileDialog.getExistingDirectory(self,
                                                     'Choose directory with ground truth images',
                                                     txt)
        if directory != '':
            self.txb_gt_images_dir.setText(directory)
            self.dir_images_gt = directory

    def btn_det_classes_clicked(self):
        filepath = QFileDialog.getOpenFileName(self, 'Choose a file with a list of classes',
                                               self.current_directory,
                                               "Image files (*.txt *.names)")
        filepath = filepath[0]
        if os.path.isfile(filepath):
            self.txb_classes_det.setText(filepath)
            self.filepath_classes_det = filepath
        else:
            self.filepath_classes_det = None
            self.txb_classes_det.setText('')

    def btn_det_dir_clicked(self):
        if self.txb_det_dir.text() == '':
            txt = self.current_directory
        else:
            txt = self.txb_det_dir.text()
        directory = QFileDialog.getExistingDirectory(self, 'Choose directory with detections', txt)
        if directory == '':
            return
        if os.path.isdir(directory):
            self.txb_det_dir.setText(directory)
            self.dir_dets = directory
        else:
            self.dir_dets = None

    def btn_output_dir_clicked(self):
        if self.txb_output_dir.text() == '':
            txt = self.current_directory
        else:
            txt = self.txb_output_dir.text()
        directory = QFileDialog.getExistingDirectory(self, 'Choose directory to save the results',
                                                     txt)
        if os.path.isdir(directory):
            self.txb_output_dir.setText(directory)
            self.dir_save_results = directory
        else:
            self.dir_save_results = None

    def btn_save_clicked(self):
        if self.result_csv is None:
            print("error")
        else:
            DB = DBManager()
            result_csv = self.result_csv.split("\n")

            # each class
            class_name = result_csv[4].split(",")
            model_name = os.path.splitext(os.path.split(self.dir_model_gt)[1])[0]
            dataset_name = os.path.splitext(os.path.split(self.dir_images_gt)[1])[0]
            AP_class, F1_class, prec_class, rec_class, threshold_class, TP_class, FP_class, FN_class = result_csv[
                                                                                                           6].split(
                ","), result_csv[7].split(","), \
                                                                                                       result_csv[
                                                                                                           8].split(
                                                                                                           ","), \
                                                                                                       result_csv[
                                                                                                           9].split(
                                                                                                           ","), \
                                                                                                       result_csv[
                                                                                                           10].split(
                                                                                                           ",") \
                , result_csv[11].split(","), result_csv[12].split(","), result_csv[13].split(",")

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
                DB.add_item_(model_name, dataset_name, name_cl, tp_cl, fp_cl, fn_cl, F1_cl, ap_cl, map_cl, prec_cl,
                             rec_cl, thre_cl)

            # save all classes metric
            result_metric = result_csv[2].split(",")

            map = float(result_metric[0])
            Precision, recall, F1_ = self.get_metric(TP_all, FP_all, FN_all)
            print(model_name, dataset_name, "all", TP_all, FP_all, FN_all, F1_, 0, map, Precision, recall, thre_cl)
            DB.add_item(model_name, dataset_name, "all", TP_all, FP_all, FN_all, F1_, 0, map, Precision, recall,
                        thre_cl)
            DB.add_item_(model_name, dataset_name, "all", TP_all, FP_all, FN_all, F1_, 0, map, Precision, recall,
                         thre_cl)

            id_max = []
            for m in range(len(self.result['tp_'])):
                value = []
                id_max.append([model_name, dataset_name, class_name[m + 1], np.nan_to_num(self.result['id'][m])])
                for i in range(len(self.result['tp_'][m])):
                    value.append([model_name, dataset_name, class_name[m + 1], self.result['tp_'][m][i],
                                  self.result['fp_'][m][i], int(nanstr(self.result['fn_'][m], i)),
                                  nanstr(self.result['f1_'][m], i + 1), nanstr(self.result['ap'][m], i), 0,
                                  nanstr(self.result['prec_'][m], i), nanstr(self.result['rec_'][m], i),
                                  nanstr(self.result['score_'][m], i)])

                if len(self.result['tp_'][m]) > 0 and self.result['prec_'][m] is not None and self.result['rec_'][m] is not None:
                    a = np.array(value)[:, 11]
                    a = a.tolist()

                    b = np.array(id_max)[:, 3]
                    b = b.tolist()

                    value_save = []
                    for t in tqdm(np.arange(-1., 0.001, 0.001)):
                        t = abs(t)
                        index = self.index_number(a, float(t))
                        if value[index] not in value_save:
                            value_save.append(value[index])

                    a_s = np.array(value_save)[:, 11]
                    a_s = a_s.tolist()
                    # fff1 = np.array(value_save)[:, 7]
                    # fff1 = fff1.tolist()
                    # fff1.sort()
                    #
                    # fff_t = False
                    # if float(fff1[-1]) == 0.0:
                    #     fff_t = True
                    #
                    # if int(float(b[m]))==len(value):
                    #     index_max=int(float(b[m]))-1
                    index_max = int(float(b[m]))

                    index1 = self.index_number(a_s, float(value[index_max][11]))

                    if value[index_max] not in value_save :
                        if float(value[index_max][11]) > float(a_s[index1]):
                            value_save.insert(index1 + 1, value[index_max])
                            id_max[m][3] = index1 + 2
                        else:
                            value_save.insert(index1, value[index_max])
                            id_max[m][3] = index1 + 1
                    # elif fff_t:
                    #     print('')
                    else:
                        id_max[m][3] = index1 + 1

                    DB.add_item_id(str(id_max[m][0]), str(id_max[m][1]), str(id_max[m][2]), int(id_max[m][3]))
                    for i in range(len(value_save)):
                        DB.add_item_(str(value_save[i][0]), str(value_save[i][1]), str(value_save[i][2]),
                                     int(value_save[i][3]),
                                     int(value_save[i][4]), int(value_save[i][5]), float(value_save[i][6]),
                                     float(value_save[i][7]),
                                     float(value_save[i][8]),
                                     float(value_save[i][9]), float(value_save[i][10]), float(value_save[i][11]))
                else:
                    DB.add_item_id(str(id_max[m][0]), str(id_max[m][1]), str(id_max[m][2]), int(id_max[m][3]))

                # for i1,b1 in enumerate(b):
                #     index1=self.index_number(a_s,float(b1))
                #     if value[int(b[int(i1)])] not in value_save:
                #         value_save.insert(index1+1,value[int(b[int(i1)])])
                #         id_max[i1][3]=index1+1
                #     else:
                #         id_max[i1][3]=index1

            # for m in range(len(self.result['tp_'])):
            #     DB.add_item_id(id_max[m][0],id_max[m][1],id_max[m][2],id_max[m][3])
            #     for i in range(len(self.result['tp_'][m])):
            #
            #         DB.add_item_(value_save[i][0],value_save[i][1],value_save[i][2],value_save[i][3],value_save[i][4],value_save[i][5],value_save[i][6],value_save[i][7],value_save[i][8],
            #                      value_save[i][9],value_save[i][10],value_save[i][11])

            for j in range(len(self.result['error'])):
                DB.add_erro_file(model_name, dataset_name, self.result['error'][j])

    def get_metric(self, tp, fp, fn):
        if tp + fp == 0 or tp + fn == 0:
            return 0, 0, 0

        prec = tp / (tp + fp)
        rec = tp / (tp + fn)
        f1 = 2 / (1 / prec + 1 / rec)
        return prec, rec, f1

    def btn_run_clicked(self):

        self.thead1 = threading.Thread(target=self.btn_run_real)
        self.thead1.start()



    def btn_run_real(self):
        if self.rad_gt_format_coco_json.isChecked():
            self.ret = 'coco'
        elif self.rad_gt_format_pascalvoc_xml.isChecked() or self.rad_gt_format_labelme_xml.isChecked():
            self.ret = 'voc'
        elif self.rad_gt_format_yolo_text.isChecked():
            self.ret = 'darknet'
        if self.ret == '':
            print("no format select")
            exit(-1)

        evaluation = onnx.ONNX(self.dir_model_gt, 64, self.dir_images_gt, self.filepath_classes_gt, self.ret,
                               self.process_method)
        self.result_csv, self.result = evaluation.evaluate()
        # threading.Thread._Thread__stop(self.thead1)
        self.btn_save_clicked()
        print("保存成功")

    def btn_draw_by_model(self, model, datasets):
        self.draw_grid.setVisible(True)

        plt = self.DBManager.draw_by_model(model, datasets, self.class_name_draw)
        self.gridlayout.addWidget(plt, 0, 2)

    def btn_draw_by_data(self, model, data):
        self.draw_grid.setVisible(True)

        plt = self.DBManager.draw_by_data(model, data, self.class_name_draw)
        self.gridlayout.addWidget(plt, 0, 2)

    def btn_draw_clicked(self):
        data = []
        for i in range(len(self.checkdatasets)):
            if self.checkdatasets[i].isChecked():
                data.append(self.datasets[i])
        model = []
        for j in range(len(self.checkmodels)):
            if self.checkmodels[j].isChecked():
                model.append(self.models[j])

        if len(data) == 1:
            self.btn_draw_by_model(model, data[0])
        elif len(model) == 1:
            self.btn_draw_by_data(model[0], data)
        else:
            print("ui2 erroe")

    def btn_search_by_model(self):
        text = self.model_line_ui3.text()
        self.model.clear()
        self.model.itemChanged.disconnect(self.QStandardModelItemChanged)
        try:
            self.model.itemChanged.disconnect(self.QStandardModelItemChanged)
        except:
            pass

        id_max1, class_name1, datasets = self.DBManager.search_id()

        for key, value in id_max1.items():
            model_n = key.split('_')[0]
            if not model_n == text:
                continue
            data_name = key.split('_')[1]
            id_max = value
            class_name = class_name1[key]
            id_max.append(0)
            class_name.append('all')

            data = []
            for i in range(len(self.value)):
                if self.value[i][1] == model_n and self.value[i][2] == data_name:
                    data.append(self.value[i])

            class_num = len(class_name)
            list = [[]] * class_num
            for i in range(len(data)):
                for l in range(class_num):
                    if data[i][3] == class_name[l]:
                        if len(list[l]) == 0:
                            list[l] = [data[i]]
                        else:
                            list[l].append(data[i])

            row_ = self.model.rowCount()
            for m in range(class_num):
                row = row_ + m
                for n in range(13):
                    # item=QtGui.QStandardItem()
                    a = list[m]
                    if n > 5:
                        self.model.setItem(row, n, QtGui.QStandardItem(str(a[id_max[m]][n])[0:5]))
                    else:
                        self.model.setItem(row, n, QtGui.QStandardItem(str(a[id_max[m]][n])))

        self.model.itemChanged.connect(self.QStandardModelItemChanged)

    def btn_search_by_data(self):
        text = self.data_line_ui3.text()
        self.model.clear()
        self.model.itemChanged.disconnect(self.QStandardModelItemChanged)
        try:
            self.model.itemChanged.disconnect(self.QStandardModelItemChanged)
        except:
            pass

        id_max1, class_name1, datasets = self.DBManager.search_id()

        for key, value in id_max1.items():
            model_n = key.split('_')[0]
            data_name = key.split('_')[1]
            if not data_name == text:
                continue
            id_max = value
            class_name = class_name1[key]
            id_max.append(0)
            class_name.append('all')

            data = []
            for i in range(len(self.value)):
                if self.value[i][1] == model_n and self.value[i][2] == data_name:
                    data.append(self.value[i])

            class_num = len(class_name)
            list = [[]] * class_num
            for i in range(len(data)):
                for l in range(class_num):
                    if data[i][3] == class_name[l]:
                        if len(list[l]) == 0:
                            list[l] = [data[i]]
                        else:
                            list[l].append(data[i])

            row_ = self.model.rowCount()
            for m in range(class_num):
                row = row_ + m
                for n in range(13):
                    # item=QtGui.QStandardItem()
                    a = list[m]
                    if n > 5:
                        self.model.setItem(row, n, QtGui.QStandardItem(str(a[id_max[m]][n])[0:5]))
                    else:
                        self.model.setItem(row, n, QtGui.QStandardItem(str(a[id_max[m]][n])))

        self.model.itemChanged.connect(self.QStandardModelItemChanged)

    def btn_search_by_filter(self):
        text = self.filter_line_ui3.text()
        text_model = text.split('_')[0]
        text_datasets = text.split('_')[1]
        self.model.clear()
        self.model.itemChanged.disconnect(self.QStandardModelItemChanged)
        try:
            self.model.itemChanged.disconnect(self.QStandardModelItemChanged)
        except:
            pass

        id_max1, class_name1, datasets = self.DBManager.search_id()

        for key, value in id_max1.items():
            model_n = key.split('_')[0]
            data_name = key.split('_')[1]
            if model_n == text_model and data_name == text_datasets:

                id_max = value
                class_name = class_name1[key]
                id_max.append(0)
                class_name.append('all')

                data = []
                for i in range(len(self.value)):
                    if self.value[i][1] == model_n and self.value[i][2] == data_name:
                        data.append(self.value[i])

                class_num = len(class_name)
                list = [[]] * class_num
                for i in range(len(data)):
                    for l in range(class_num):
                        if data[i][3] == class_name[l]:
                            if len(list[l]) == 0:
                                list[l] = [data[i]]
                            else:
                                list[l].append(data[i])

                row_ = self.model.rowCount()
                for m in range(1):
                    row = row_ + m
                    for n in range(13):
                        # item=QtGui.QStandardItem()
                        a = list[m]
                        if n > 5:
                            self.model.setItem(row, n, QtGui.QStandardItem(str(a[id_max[m]][n])[0:5]))
                        else:
                            self.model.setItem(row, n, QtGui.QStandardItem(str(a[id_max[m]][n])))

        self.model.itemChanged.connect(self.QStandardModelItemChanged)

    def btn_search_by_filter1(self):
        text = self.filter_line_ui3.text()

        self.model.clear()
        self.model.setHorizontalHeaderLabels(['ID', 'Model', 'dataset', 'class', 'TP', 'FP'
                                                 , 'FN', 'F1', 'Ap', 'Map', 'Precision', 'Recall', 'Threshold'])
        self.model.itemChanged.disconnect(self.QStandardModelItemChanged)
        try:
            self.model.itemChanged.disconnect(self.QStandardModelItemChanged)
        except:
            pass

        id_max1, class_name1, datasets = self.DBManager.search_id()

        for key, value in id_max1.items():
            model_n = key.split('_')[0]
            data_name = key.split('_')[1]

            id_max = value
            class_name = class_name1[key]
            id_max.append(0)
            class_name.append('all')

            data = []
            for i in range(len(self.value)):
                if self.value[i][1] == model_n and str(self.value[i][2]) == data_name and self.value[i][3] == text:
                    data.append(self.value[i])

            class_num = len(class_name)
            list = [[]] * class_num
            for i in range(len(data)):
                for l in range(class_num):
                    if data[i][3] == class_name[l]:
                        if len(list[l]) == 0:
                            list[l] = [data[i]]
                        else:
                            list[l].append(data[i])

            # row_ = self.model.rowCount()
            # m=class_name.index(text)
            # row = row_ + m
            if len(list[class_name.index(text)]) > 0:
                row_ = self.model.rowCount()

                row = row_ + 0
                for n in range(13):
                    # item=QtGui.QStandardItem()
                    a = list[class_name.index(text)]
                    if n > 5:
                        self.model.setItem(row, n, QtGui.QStandardItem(str(a[id_max[class_name.index(text)]][n])[0:5]))
                    else:
                        self.model.setItem(row, n, QtGui.QStandardItem(str(a[id_max[class_name.index(text)]][n])))
            else:
                pass

        self.model.itemChanged.connect(self.QStandardModelItemChanged)

    def btn_refresh(self):
        self.model.clear()
        self.model.setHorizontalHeaderLabels(['ID', 'Model', 'dataset', 'class', 'TP', 'FP'
                                                 , 'FN', 'F1', 'Ap', 'Map', 'Precision', 'Recall', 'Threshold'])
        self.model.itemChanged.disconnect(self.QStandardModelItemChanged)

        id_max1, class_name1, datasets = self.DBManager.search_id()

        for key, value in id_max1.items():
            model_n = key.split('_')[0]
            data_name = key.split('_')[1]
            id_max = value
            class_name = class_name1[key]
            id_max.append(0)
            class_name.append('all')

            data = []
            for i in range(len(self.value)):
                if self.value[i][1] == model_n and str(self.value[i][2]) == data_name:
                    data.append(self.value[i])

            class_num = len(class_name)
            list = [[]] * class_num
            for i in range(len(data)):
                for l in range(class_num):
                    if data[i][3] == class_name[l]:
                        if len(list[l]) == 0:
                            list[l] = [data[i]]
                        else:
                            list[l].append(data[i])

            row_ = self.model.rowCount()
            for m in range(class_num):
                row = row_ + m
                for n in range(13):
                    if n > 5:
                        self.model.setItem(row, n, QtGui.QStandardItem(str(list[m][id_max[m]][n])[0:5]))
                    else:
                        self.model.setItem(row, n, QtGui.QStandardItem(str(list[m][id_max[m]][n])))

        self.model.itemChanged.connect(self.QStandardModelItemChanged)

    def index_number(self, li, defaultnumber):
        select = Decimal(str(defaultnumber)) - Decimal(str(li[0]))
        index = 0
        for i in range(1, len(li) - 1):
            select2 = Decimal(str(defaultnumber)) - Decimal(str(li[i]))
            if (abs(select) > abs(select2)):
                select = select2
                index = i
        return index

    def QStandardModelItemChanged(self, item):

        self.model.itemChanged.disconnect(self.QStandardModelItemChanged)

        a = []
        b = []
        r = self.table_widget.currentIndex().row()  # 获取行号

        model = self.model.item(r, 1).text()
        data = self.model.item(r, 2).text()
        class_ = self.model.item(r, 3).text()
        thre = self.model.item(r, 12).text()

        for i in range(len(self.value)):
            if self.value[i][1] == model and str(self.value[i][2]) == data and self.value[i][3] == class_:
                a.append(self.value[i][12])
                b.append(self.value[i])
        index = self.index_number(a, float(thre))

        for j in range(13):
            if j > 5:
                self.model.setItem(r, j, QtGui.QStandardItem(str(b[index][j])[0:5]))
            else:
                self.model.setItem(r, j, QtGui.QStandardItem(str(b[index][j])))

        self.model.itemChanged.connect(self.QStandardModelItemChanged)

    def btn_search_by_model_error(self):
        text = self.model_line_ui4.text()
        text = "\"" + text + "\""
        print('model_name=' + str(text))
        self.model1.setFilter('model_name=' + str(text))

    def btn_search_by_data_error(self):
        text = self.data_line_ui4.text()
        text = "\"" + text + "\""
        print('dataset_name=' + str(text))
        self.model1.setFilter('dataset_name=' + str(text))

    def btn_search_by_filter_error(self):
        text = self.filter_line_ui4.text()
        self.model1.setFilter(str(text))

    def btn_refresh_error(self):
        self.model1.setFilter('')

    def show_error_file(self, index):
        row = index.row()
        text = self.model1.data(self.model1.index(row, 3))
        # text=self.result['error'][qModelIndex.row()]
        image_path = text.split('---')[0]
        img = cv2.imread(image_path)
        cv2.imshow("Image", img)

    def btn_load_md(self):

        models, datasets = self.DBManager.search_model_datasets()
        self.models, self.datasets = models, datasets

        self.checkmodels = models.copy()
        self.checkdatasets = datasets.copy()
        for i in range(len(models)):
            self.checkmodels[i] = QCheckBox(str(models[i]))
            self.checkmodels[i].stateChanged.connect(self.btn_draw_clicked)
            self.group_box_layout.addWidget(self.checkmodels[i])
        for i in range(len(datasets)):
            self.checkdatasets[i] = QCheckBox(str(datasets[i]))
            self.checkdatasets[i].stateChanged.connect(self.btn_draw_clicked)
            self.group_box_layout1.addWidget(self.checkdatasets[i])

    def btn_show_classes_clicked(self):
        name = None
        for i in range(len(self.checkdatasets)):
            if self.checkdatasets[i].isChecked():
                name = self.datasets[i]
        class_names = self.DBManager.search_classes(name)
        self.combobox_classes.clear()
        self.combobox_classes.addItems(class_names)
