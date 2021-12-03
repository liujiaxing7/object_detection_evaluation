# -*- coding: utf-8 -*-
'''
@author: 刘家兴
@contact: ljx0ml@163.com
@file: model.py
@time: 2021/8/24 18.46
@desc:
'''
import random
from decimal import Decimal

from PyQt5 import QtGui, QtCore, QtWidgets, QtSql
from PyQt5.QtCore import Qt, QRect, QThread, pyqtSignal
from PyQt5.QtSql import QSqlQuery
from PyQt5.QtWidgets import *

import os
from cv2 import cv2
import onnx
import numpy as np
from tqdm import tqdm

# matplotlib.use("Qt5Agg")
from src.database.db import DBManager, MyFigure
from src.database.db_concat import DBManager_Changed

global subDBManager, models, datasets, classes
subDBManager = DBManager()
models, datasets = subDBManager.search_model_datasets()
classes = subDBManager.search_all_classes()

global model_selecion, dataset_selection, class_selection, all_model_names, all_dataset_names, all_class_names
all_model_names = models.copy()
all_dataset_names = datasets.copy()
all_class_names = classes.copy()
model_selecion, dataset_selection, class_selection = all_model_names, all_dataset_names, all_class_names
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


class ModelDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Model selection')
        global subDBManager, models, datasets
        self.models, self.datasets = models, datasets
        self.checkmodels = models.copy()
        self.checkdatasets = datasets.copy()

        self.setGeometry(400, 400, 200, 400)
        self.center_screen()
        self.initUI()
        self.show()
        self.memoryUI()

    def initUI(self):
        # 实例化垂直布局
        self.models_box = QGridLayout()
        self.bt_add = QPushButton('add item')
        self.bt_add.setGeometry(QtCore.QRect(0, 0, 20, 20))
        self.bt_add.clicked.connect(self.save_selection)
        # self.hbox.addStretch(5)
        self.all_check_box = QCheckBox('All')
        self.all_check_box.stateChanged.connect(self.All)
        self.models_box.addWidget(self.all_check_box, 0, 0)

        m, n = 1, 0
        for i in range(len(self.models)):
            self.checkmodels[i] = QCheckBox(str(self.models[i]))
            self.checkmodels[i].stateChanged.connect(self.btn_draw_clicked)
            if i > 0 and i % 5 == 0:
                m += 1
                n = 0
            self.models_box.addWidget(self.checkmodels[i], m, n)
            n += 1
        # for i in range(len(self.datasets)):
        #     self.checkdatasets[i] = QCheckBox(str(self.datasets[i]))
        #     self.checkdatasets[i].stateChanged.connect(self.btn_draw_clicked)
        #     self.models_box.addWidget(self.checkdatasets[i])

        self.setLayout(self.models_box)  # 设置窗体布局

    def memoryUI(self):
        global model_selecion
        tmp_model = model_selecion
        for i in range(len(self.models)):
            if str(self.models[i]) in tmp_model:
                self.checkmodels[i].setChecked(True)


    def center_screen(self):
        size = self.size()
        desktopSize = QtWidgets.QDesktopWidget().screenGeometry()
        top = (desktopSize.height() / 2) - (size.height() / 2)
        left = (desktopSize.width() / 2) - (size.width() / 2)
        self.move(left, top)
    def save_selection(self):
        print('')
    def btn_draw_clicked(self):
        # data = []
        # for i in range(len(self.checkdatasets)):
        #     if self.checkdatasets[i].isChecked():
        #         data.append(self.datasets[i])
        model = []
        for j in range(len(self.checkmodels)):
            if self.checkmodels[j].isChecked():
                model.append(self.models[j])
        self.Selectedrow_num = len(model)
        if self.Selectedrow_num == 0:
            self.all_check_box.setCheckState(0)
        elif self.Selectedrow_num == len(self.checkmodels):
            self.all_check_box.setCheckState(2)
        else:
            self.all_check_box.setCheckState(1)
        global model_selecion
        model_selecion = model.copy()

    def All(self, status):
        if status == 2:
            for i in range(len(self.checkmodels)):
                self.checkmodels[i].setChecked(True)
        elif status == 1:
            if self.Selectedrow_num == 0:
                self.all_check_box.setCheckState(2)
        elif status == 0:
            self.clear()
    def clear(self):
        for i in range(len(self.models)):
            self.checkmodels[i].setChecked(False)
        self.all_check_box.setChecked(False)


class DatasetDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Dataset selection')
        global subDBManager, models, datasets
        self.datasets = datasets

        # self.checkmodels = models.copy()
        self.checkdatasets = datasets.copy()

        self.setGeometry(400, 400, 200, 400)
        self.center_screen()
        self.initUI()
        self.show()
        self.memoryUI()

    def initUI(self):
        global dataset_selection
        # 实例化垂直布局
        self.datasets_box = QGridLayout()
        self.bt_add = QPushButton('add item')
        self.bt_add.setGeometry(QtCore.QRect(0, 0, 20, 20))
        self.bt_add.clicked.connect(self.save_selection)
        # self.hbox.addStretch(5)
        self.all_check_box = QCheckBox('All')
        self.all_check_box.stateChanged.connect(self.All)
        self.datasets_box.addWidget(self.all_check_box, 0, 0)

        m, n = 1, 0
        for i in range(len(self.datasets)):
            self.checkdatasets[i] = QCheckBox(str(self.datasets[i]))
            self.checkdatasets[i].stateChanged.connect(self.btn_draw_clicked)
            # if str(self.datasets[i]) in dataset_selection:
            #     self.checkdatasets[i].ser
            if i > 0 and i % 5 == 0:
                m += 1
                n = 0
            self.datasets_box.addWidget(self.checkdatasets[i], m, n)
            n += 1

        self.setLayout(self.datasets_box)  # 设置窗体布局

    def memoryUI(self):
        global dataset_selection
        tmp_dataset = dataset_selection
        for i in range(len(self.datasets)):
            if str(self.datasets[i]) in tmp_dataset:
                self.checkdatasets[i].setChecked(True)

    def center_screen(self):
        size = self.size()
        desktopSize = QtWidgets.QDesktopWidget().screenGeometry()
        top = (desktopSize.height() / 2) - (size.height() / 2)
        left = (desktopSize.width() / 2) - (size.width() / 2)
        self.move(left, top)

    def save_selection(self):
        print('')

    def btn_draw_clicked(self):
        data = []
        for i in range(len(self.checkdatasets)):
            if self.checkdatasets[i].isChecked():
                data.append(self.datasets[i])
        self.Selectedrow_num = len(data)
        if self.Selectedrow_num == 0:
            self.all_check_box.setCheckState(0)
        elif self.Selectedrow_num == len(self.checkdatasets):
            self.all_check_box.setCheckState(2)
        else:
            self.all_check_box.setCheckState(1)
        global dataset_selection
        dataset_selection = data.copy()

    def All(self, status):
        if status == 2:
            for i in range(len(self.checkdatasets)):
                self.checkdatasets[i].setChecked(True)
        elif status == 1:
            if self.Selectedrow_num == 0:
                self.all_check_box.setCheckState(2)
        elif status == 0:
            self.clear()

    def clear(self):
        for i in range(len(self.datasets)):
            self.checkdatasets[i].setChecked(False)
        self.all_check_box.setChecked(False)


class ClassesDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Classes selection')
        global subDBManager, models, datasets, classes
        self.classes = classes

        self.checkclasses = classes.copy()

        self.setGeometry(400, 400, 200, 400)
        self.center_screen()
        self.initUI()
        self.show()
        self.memoryUI()

    def initUI(self):
        # 实例化垂直布局
        self.classes_box = QGridLayout()

        self.all_check_box = QCheckBox('All')
        self.all_check_box.stateChanged.connect(self.All)
        self.classes_box.addWidget(self.all_check_box, 0, 0)

        m, n = 1, 0
        for i in range(len(self.classes)):
            self.checkclasses[i] = QCheckBox(str(self.classes[i]))
            self.checkclasses[i].stateChanged.connect(self.btn_draw_clicked)
            if i > 0 and i % 5 == 0:
                m += 1
                n = 0
            self.classes_box.addWidget(self.checkclasses[i], m, n)
            n += 1


        self.setLayout(self.classes_box)  # 设置窗体布局


    def memoryUI(self):
        global class_selection
        tmp_class = class_selection
        for i in range(len(self.classes)):
            if str(self.classes[i]) in tmp_class:
                self.checkclasses[i].setChecked(True)


    def center_screen(self):
        size = self.size()
        desktopSize = QtWidgets.QDesktopWidget().screenGeometry()
        top = (desktopSize.height() / 2) - (size.height() / 2)
        left = (desktopSize.width() / 2) - (size.width() / 2)
        self.move(left, top)

    def save_selection(self):
        print('')

    def btn_draw_clicked(self):
        data = []
        for i in range(len(self.checkclasses)):
            if self.checkclasses[i].isChecked():
                data.append(self.classes[i])
        self.Selectedrow_num = len(data)
        if self.Selectedrow_num == 0:
            self.all_check_box.setCheckState(0)
        elif self.Selectedrow_num == len(self.checkclasses):
            self.all_check_box.setCheckState(2)
        else:
            self.all_check_box.setCheckState(1)
        global class_selection
        class_selection = data.copy()

    def All(self, status):
        if status == 2:
            for i in range(len(self.checkclasses)):
                self.checkclasses[i].setChecked(True)
        elif status == 1:
            if self.Selectedrow_num == 0:
                self.all_check_box.setCheckState(2)
        elif status == 0:
            self.clear()

    def clear(self):
        for i in range(len(self.checkclasses)):
            self.checkclasses[i].setChecked(False)
        self.all_check_box.setChecked(False)


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

        # global subDBManager, models, datasets
        # self.models = models.copy()
        # self.datasets = datasets.copy()
        self.DBManager = DBManager()

        self.tab1 = QtWidgets.QWidget()
        self.tab2 = QtWidgets.QWidget()
        self.tab3 = QtWidgets.QWidget()
        self.tab4 = QtWidgets.QWidget()
        self.tab5 = QtWidgets.QWidget()
        self.addTab(self.tab1, "Detection Metrics")
        self.addTab(self.tab2, "Visual Comparsion")
        self.addTab(self.tab3, "Show Database")
        self.addTab(self.tab4, "Error File Preview")
        self.addTab(self.tab5, "Database Manager")
        self.tab1UI()
        self.tab2UI()
        self.tab3UI()
        self.tab4UI()
        self.tab5UI()
        self.setWindowTitle("Object Detection Metrics")

        self.thr80_id_max1, self.id_max_class_name1, self.id_max_datasets = self.DBManager.search_id()
        self.class_dict = {'person':0, 'escalator':1, 'escalator_handrails':2, 'person_dummy':3, 'escalator_model':4, 'escalator_handrails_model':5}
        self.filter_thresh = 0

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
        h5.addWidget(QLabel("Onnx Model Type:"), 2, Qt.AlignLeft)
        self.combobox_process = QComboBox()
        h5.addWidget(self.combobox_process, 9, Qt.AlignLeft)
        self.combobox_process.addItems(['', 'yolov3', 'yolov3_padding', 'yolov5', 'yolov5x', 'yolov3_tiny3'])
        self.combobox_process.setMinimumSize(200, 27)
        self.combobox_process.currentIndexChanged.connect(self.comboSelectionChanged)
        h5.addWidget(QLabel("Datasets Name:"), 0, Qt.AlignLeft)
        self.txt_gt_data_name = QLineEdit()
        self.txt_gt_data_name.setPlaceholderText("默认为数据集文件夹名")
        self.txt_gt_data_name.setMinimumSize(200, 27)
        h5.addWidget(self.txt_gt_data_name, 20, Qt.AlignLeft)
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
        self.checkmodels, self.checkdatasets, self.models, self.datasets = [], [], [], []
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

        select_model = QPushButton("Model Select")
        select_model.setMinimumSize(100, 27)
        select_model.clicked.connect(self.pop_model_select)
        h2.addWidget(select_model, 1, Qt.AlignRight)

        select_dataset = QPushButton("Dataset Select")
        select_dataset.setMinimumSize(100, 27)
        select_dataset.clicked.connect(self.pop_dataset_select)
        h2.addWidget(select_dataset, 1, Qt.AlignRight)

        select_best_thresh = QPushButton("Load other threshold")
        select_best_thresh.setMinimumSize(100, 27)
        select_best_thresh.clicked.connect(self.btn_load_diff_thresh)
        h2.addWidget(select_best_thresh, 1, Qt.AlignRight)

        self.load_selection = QPushButton("Load selection")
        self.load_selection.setMinimumSize(100, 27)
        h2.addWidget(self.load_selection, 1, Qt.AlignRight)
        self.load_selection.clicked.connect(self.btn_load_selection)

        # self.load_class_dir = QPushButton("Load ...")
        # self.load_class_dir.setMinimumSize(60, 27)
        # h2.addWidget(self.load_class_dir, 1, Qt.AlignRight)
        # self.load_class_dir.clicked.connect(self.btn_show_classes_clicked)
        # self.btn_draw = QPushButton("Draw")
        # self.btn_draw.setMinimumSize(80, 27)
        # h2.addWidget(self.btn_draw, 1, Qt.AlignRight)
        # self.btn_draw.clicked.connect(self.btn_draw_clicked)

        layout.addRow(h2)

        h1 = QGridLayout()
        group_box = QtWidgets.QGroupBox('Model')
        self.group_box_layout = QtWidgets.QHBoxLayout()
        group_box.setLayout(self.group_box_layout)

        group_box.setMinimumSize(100, 10)
        h1.addWidget(group_box, 0, 0, 1, 2)

        self._group_box1 = QtWidgets.QGroupBox('Datasets')
        self.group_box_layout1 = QtWidgets.QVBoxLayout()
        self._group_box1.setLayout(self.group_box_layout1)

        self._group_box1.setMaximumSize(200, 1000)
        # layout.addChildLayout(h1)
        h1.addWidget(self._group_box1, 1, 0)
        # self.btn_load_md()

        self.draw_grid = QWidget()
        self._groupBox = QGroupBox(self.draw_grid)
        self.gridlayout = QGridLayout(self._groupBox)
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
        self.filter_line_ui3.setPlaceholderText("m&d^c/m^c/d^c")
        h1.addWidget(self.filter_line_ui3)
        search_by_filter = QPushButton("Search by condition")
        h1.addWidget(search_by_filter)
        search_by_filter.clicked.connect(self.btn_search_by_filter1)
        refresh = QPushButton("Refresh")
        h1.addWidget(refresh)
        refresh.clicked.connect(self.btn_refresh)
        layout.addRow(h1)

        pop_subwindow = QHBoxLayout()
        select_model = QPushButton("Model Select")
        select_model.clicked.connect(self.pop_model_select)

        pop_subwindow.addWidget(select_model)
        select_dataset = QPushButton("Dataset Select")
        select_dataset.clicked.connect(self.pop_dataset_select)
        pop_subwindow.addWidget(select_dataset)

        select_classes = QPushButton("classes Select")
        select_classes.clicked.connect(self.pop_classes_select)
        pop_subwindow.addWidget(select_classes)

        search_by_selection = QPushButton("search by Selections")
        search_by_selection.clicked.connect(self.search_selection)
        pop_subwindow.addWidget(search_by_selection)

        search_by_thresh = QPushButton("refresh by threshold0.8")
        search_by_thresh.clicked.connect(self.refresh_thresh)
        pop_subwindow.addWidget(search_by_thresh)
        layout.addRow(pop_subwindow)


        h3 = QGridLayout()
        self.table_widget = QtWidgets.QTableView()
        self.table_widget.horizontalHeader().setStretchLastSection(False)

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
        self.table_widget.horizontalHeader().setStretchLastSection(True)
        self.table_widget.verticalHeader().setStretchLastSection(True)
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

    def tab5UI(self):
        layout = QFormLayout()
        gt = QHBoxLayout()
        font = QtGui.QFont()
        font.setBold(True)
        font.setPixelSize(25)
        gt_label = QLabel("Database Manager")
        gt.addWidget(gt_label, 1, Qt.AlignCenter)
        gt_label.setFont(font)
        layout.addRow(gt)
        layout.addRow(QLabel(''))

        gt1 = QHBoxLayout()
        font = QtGui.QFont()
        font.setBold(True)
        font.setPixelSize(15)
        gt_label = QLabel("Merge Database")
        gt1.addWidget(gt_label, 1, Qt.AlignCenter)
        gt_label.setFont(font)
        layout.addRow(gt1)
        layout.addRow(QLabel(''))

        h1 = QHBoxLayout()
        h1.addWidget(QLabel("Main database name:       "))
        self.main_database_dir = QLineEdit()
        self.main_database_dir.setReadOnly(True)
        h1.addWidget(self.main_database_dir)
        self.load_model_dir = QPushButton("...")
        h1.addWidget(self.load_model_dir)
        self.load_model_dir.clicked.connect(self.btn_main_database_clicked)
        layout.addRow(h1)

        h2 = QHBoxLayout()
        h2.addWidget(QLabel("Another database name:     "))
        self.ano_database_dir = QLineEdit()
        self.ano_database_dir.setReadOnly(True)
        h2.addWidget(self.ano_database_dir)
        self.load_images_dir = QPushButton("...")
        h2.addWidget(self.load_images_dir)
        self.load_images_dir.clicked.connect(self.btn_ano_database_clicked)
        layout.addRow(h2)

        h3 = QHBoxLayout()
        self.merge_button = QPushButton("Merge")
        self.merge_button.clicked.connect(self.merge_database)
        h3.addWidget(self.merge_button)
        layout.addRow(h3)

        self.tab5.setLayout(layout)

    @staticmethod
    def pop_model_select(self):
        diary_window = ModelDialog()
        diary_window.exec_()
        print('')

    @staticmethod
    def pop_dataset_select(self):
        diary_window = DatasetDialog()
        diary_window.exec_()
        print('')

    @staticmethod
    def pop_classes_select(self):
        diary_window = ClassesDialog()
        diary_window.exec_()
        print('')

    def search_selection(self):
        global model_selecion, dataset_selection
        temp_models = model_selecion
        temp_dataset = dataset_selection

        self.model.clear()
        self.model.setHorizontalHeaderLabels(['ID', 'Model', 'dataset', 'class', 'TP', 'FP'
                                                 , 'FN', 'F1', 'Ap', 'Map', 'Precision', 'Recall', 'Threshold'])
        self.model.itemChanged.disconnect(self.QStandardModelItemChanged)
        try:
            self.model.itemChanged.disconnect(self.QStandardModelItemChanged)
        except:
            pass

        id_max1, class_name1, datasets = self.DBManager.search_id()

        if len(id_max1) == 0:
            return
        for key, value in id_max1.items():
            data_name = key.split('$')[-1]
            model_n = key.split('$' + data_name)[0]
            if not model_n in temp_models:
                continue
            if not data_name in temp_dataset:
                continue
            id_max = value
            class_name = class_name1[key]
            id_max.append(0)
            class_name.append('all')

            data = []
            for i in range(len(self.value)):
                if str(self.value[i][1]) == model_n and str(self.value[i][2]) == data_name:
                    data.append(self.value[i])

            class_num = len(class_name)
            list = [[]] * class_num
            # global class_selection
            # selection_length = len(class_selection)
            # if selection_length > class_num:
            #     class_selection = class_name
            for i in range(len(data)):
                for l in range(class_num):
                    if data[i][3] == class_name[l] and data[i][3] in class_selection:
                    # if data[i][3] == class_name[l]:
                        if len(list[l]) == 0:
                            list[l] = [data[i]]
                        else:
                            list[l].append(data[i])

            row_ = self.model.rowCount()
            # class_num = min(class_num, len(class_selection))
            for m in range(class_num):
                row = row_ + m
                for n in range(13):
                    # item=QtGui.QStandardItem()
                    a = list[m]
                    if len(a) == 0:
                        continue
                    if n > 5:
                        self.model.setItem(row, n, QtGui.QStandardItem(str(a[id_max[m]][n])[0:5]))
                    else:
                        self.model.setItem(row, n, QtGui.QStandardItem(str(a[id_max[m]][n])))

        self.model.itemChanged.connect(self.QStandardModelItemChanged)
        self.model.setHorizontalHeaderLabels(['ID', 'Model', 'dataset', 'class', 'TP', 'FP'
                                                 , 'FN', 'F1', 'Ap', 'Map', 'Precision', 'Recall', 'Threshold'])
        self.filter_thresh = 0

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
            sys.exit(0)
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
        elif text == 'yolov3_padding':
            self.process_method = 'yolov3_padding'
        elif text == 'yolov5':
            self.process_method = 'yolov5'
        elif text == 'yolov5x':
            self.process_method = 'yolov5x'
        elif text == 'yolov3_tiny3':
            self.process_method = 'yolov3_tiny3'

    def comboSelectionChanged1(self, index):
        text = self.combobox_classes.itemText(index)
        if text == '':
            print(1)
        else:
            self.class_name_draw = text
            self.btn_draw()

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
            if self.txt_gt_data_name.text() == '':
                dataset_name = os.path.splitext(os.path.split(self.dir_images_gt)[1])[0]
            else:
                dataset_name = self.txt_gt_data_name.text()
            # dataset_name='20210924_escalator'
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

                if len(self.result['tp_'][m]) > 0 and self.result['prec_'][m] is not None and self.result['rec_'][
                    m] is not None:
                    a = np.array(value)[:, 11]
                    a = a.tolist()

                    b = np.array(id_max)[:, 3]
                    b = b.tolist()

                    value_save = []
                    for t in np.arange(-1., 0.001, 0.001):
                        t = abs(t)
                        index = self.index_number(a, float(t))
                        if value[index] not in value_save:
                            value_save.append(value[index])

                    a_s = np.array(value_save)[:, 11]
                    a_s = a_s.tolist()

                    index_max = int(float(b[m]))
                    print("value_max")
                    print(value[index_max])

                    index1 = self.index_number(a_s, float(value[index_max][11]))

                    if value[index_max] not in value_save:
                        if float(value[index_max][11]) > float(a_s[index1]):
                            value_save.insert(index1, value[index_max])
                            id_max[m][3] = index1 + 1
                        else:
                            value_save.insert(index1+1, value[index_max])
                            id_max[m][3] = index1 + 2

                    else:
                        id_max[m][3] = index1 + 1

                    DB.add_item_id(str(id_max[m][0]), str(id_max[m][1]), str(id_max[m][2]), int(id_max[m][3]))
                    for i in tqdm(range(len(value_save))):
                        DB.add_item_(str(value_save[i][0]), str(value_save[i][1]), str(value_save[i][2]),
                                     int(value_save[i][3]),
                                     int(value_save[i][4]), int(value_save[i][5]), float(value_save[i][6]),
                                     float(value_save[i][7]),
                                     float(value_save[i][8]),
                                     float(value_save[i][9]), float(value_save[i][10]), float(value_save[i][11]))
                else:
                    DB.add_item_id(str(id_max[m][0]), str(id_max[m][1]), str(id_max[m][2]), int(id_max[m][3]))

            print("saving error files ...")
            nums_list = np.arange(0, len(self.result['error'])).tolist()
            if len(nums_list) > 100:
                nums = random.sample(nums_list, 100)
                nums = sorted(nums)
            else:
                nums = nums_list

            for j in nums:
                DB.add_erro_file(model_name, dataset_name, self.result['error'][j])

    def get_metric(self, tp, fp, fn):
        if tp + fp == 0 or tp + fn == 0:
            return 0, 0, 0

        prec = tp / (tp + fp)
        rec = tp / (tp + fn)
        f1 = 2 / (1 / prec + 1 / rec)
        return prec, rec, f1

    def btn_run_clicked(self):
        self.btn_run_real()

        # self.thead1 = threading.Thread(target=self.btn_run_real)
        # self.thead1.start()

    def btn_run_real(self):
        if self.rad_gt_format_coco_json.isChecked():
            self.ret = 'coco'
        elif self.rad_gt_format_pascalvoc_xml.isChecked():
            self.ret = 'voc'
        elif self.rad_gt_format_labelme_xml.isChecked():
            self.ret = 'xml'
        elif self.rad_gt_format_yolo_text.isChecked():
            self.ret = 'darknet'
        if self.ret == '':
            print("no format select")
            exit(-1)

        model_name = os.path.splitext(os.path.split(self.dir_model_gt)[1])[0]
        if self.txt_gt_data_name.text() == '':
            dataset_name = os.path.splitext(os.path.split(self.dir_images_gt)[1])[0]
        else:
            dataset_name = self.txt_gt_data_name.text()

        id_max1, class_name1, datasets = self.DBManager.search_id()

        for key, value in id_max1.items():
            if model_name + "$" + dataset_name == key:
                print("model and dataset repeat！")
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

    def draw_by_models(self, models, dataset):
        if len(models) == 0:
            return
        self.draw_grid.setVisible(True)

        map, ap, recall, Precision, F1_, index, TP, FP, FN, Thre = [], [], [], [], [], [], [], [], [], []
        for key, value in self.thr80_id_max1.items():
            data_name = key.split('$')[-1]
            model_n = key.split('$' + data_name)[0]
            if not model_n in models:
                continue
            if not data_name == dataset:
                continue
            if self.class_name_draw == None:
                self.class_name_draw = 'person'
            id_max = value[self.class_dict[self.class_name_draw]]
            tmp_data = []
            tmp_thresh = []
            for i in range(len(self.value)):
                if str(self.value[i][1]) == model_n and str(self.value[i][2]) == data_name and str(self.value[i][3]) == self.class_name_draw:
                    tmp_data.append(self.value[i])
                    tmp_thresh.append(self.value[i][12])
            if len(tmp_data) == 0:
                continue
            index_thresh = self.index_number(tmp_thresh, float(0.8))
            id, model_name, dataset_name, class_name, tp, fp, fn, f1, Ap, Map, prec, rec, Threshold = tmp_data[index_thresh]

            if not class_name == self.class_name_draw:
                continue
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
        if len(index) == 0:
            return
        fig_show = MyFigure(width=10, height=5, dpi=100)
        fig_show.fig.suptitle("Metric comparison")
        fig_show.fig.subplots_adjust(wspace=0.3, hspace=0.5)
        fig_show.axes0 = fig_show.fig.add_subplot(258)
        fig_show.axes1 = fig_show.fig.add_subplot(256)
        fig_show.axes2 = fig_show.fig.add_subplot(255)
        fig_show.axes3 = fig_show.fig.add_subplot(251)
        fig_show.axes4 = fig_show.fig.add_subplot(252)
        fig_show.axes5 = fig_show.fig.add_subplot(253)
        fig_show.axes6 = fig_show.fig.add_subplot(254)
        fig_show.axes7 = fig_show.fig.add_subplot(257)
        fig_show.axes8 = fig_show.fig.add_subplot(259)
        # F1.axes9 = F1.fig.add_subplot(260)
        fig_show.axes0.bar(index, map)
        fig_show.axes1.bar(index, recall)
        fig_show.axes2.bar(index, Precision)
        fig_show.axes3.bar(index, F1_)
        fig_show.axes4.bar(index, TP)
        fig_show.axes5.bar(index, FP)
        fig_show.axes6.bar(index, FN)
        fig_show.axes7.bar(index, ap)
        fig_show.axes8.bar(index, Thre)

        for a, b, i in zip(index, map, range(len(index))):  # zip 函数
            fig_show.axes0.text(a, b + 0.01, "%.2f" % map[i], ha='center', fontsize=10)  # plt.text 函数
        for a, b, i in zip(index, recall, range(len(index))):  # zip 函数
            fig_show.axes1.text(a, b + 0.01, "%.2f" % recall[i], ha='center', fontsize=10)  # plt.text 函数
        for a, b, i in zip(index, Precision, range(len(index))):  # zip 函数
            fig_show.axes2.text(a, b + 0.01, "%.2f" % Precision[i], ha='center', fontsize=10)  # plt.text 函数
        for a, b, i in zip(index, F1_, range(len(index))):  # zip 函数
            fig_show.axes3.text(a, b + 0.01, "%.2f" % F1_[i], ha='center', fontsize=10)  # plt.text 函数
        for a, b, i in zip(index, TP, range(len(index))):  # zip 函数
            fig_show.axes4.text(a, b + 0.01, "%.2f" % TP[i], ha='center', fontsize=10)  # plt.text 函数
        for a, b, i in zip(index, FP, range(len(index))):  # zip 函数
            fig_show.axes5.text(a, b + 0.01, "%.2f" % FP[i], ha='center', fontsize=10)  # plt.text 函数
        for a, b, i in zip(index, FN, range(len(index))):  # zip 函数
            fig_show.axes6.text(a, b + 0.01, "%.2f" % FN[i], ha='center', fontsize=10)  # plt.text 函数
        for a, b, i in zip(index, ap, range(len(index))):  # zip 函数
            fig_show.axes7.text(a, b + 0.01, "%.2f" % ap[i], ha='center', fontsize=10)  # plt.text 函数
        for a, b, i in zip(index, Thre, range(len(index))):  # zip 函数
            fig_show.axes8.text(a, b + 0.01, "%.2f" % Thre[i], ha='center', fontsize=10)  # plt.text 函数

        fig_show.axes0.set_title("Map")
        fig_show.axes1.set_title("recall")
        fig_show.axes2.set_title("Prediction")
        fig_show.axes3.set_title("F1")
        fig_show.axes4.set_title("TP")
        fig_show.axes5.set_title("FP")
        fig_show.axes6.set_title("FN")
        fig_show.axes7.set_title("Ap")
        fig_show.axes8.set_title("Threshold")

        self.gridlayout.addWidget(fig_show, 0, 2)
        # return fig_show

    def draw_by_datasets(self, model, datasets):
        if len(datasets) == 0:
            return
        self.draw_grid.setVisible(True)
        map, ap, recall, Precision, F1_, index, TP, FP, FN, Thre = [], [], [], [], [], [], [], [], [], []
        for key, value in self.thr80_id_max1.items():
            data_name = key.split('$')[-1]
            model_n = key.split('$' + data_name)[0]
            if not model_n == model:
                continue
            if not data_name in datasets:
                continue
            id_max = value
            id, model_name, dataset_name, class_name, tp, fp, fn, f1, Ap, Map, prec, rec, Threshold = self.value[id_max]

            if not class_name==self.class_name_draw:
                continue
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
        fig_show = MyFigure(width=10, height=5, dpi=100)
        fig_show.fig.suptitle("Metric comparison")
        fig_show.fig.subplots_adjust(wspace=0.3, hspace=0.5)
        fig_show.axes0 = fig_show.fig.add_subplot(258)
        fig_show.axes1 = fig_show.fig.add_subplot(256)
        fig_show.axes2 = fig_show.fig.add_subplot(255)
        fig_show.axes3 = fig_show.fig.add_subplot(251)
        fig_show.axes4 = fig_show.fig.add_subplot(252)
        fig_show.axes5 = fig_show.fig.add_subplot(253)
        fig_show.axes6 = fig_show.fig.add_subplot(254)
        fig_show.axes7 = fig_show.fig.add_subplot(257)
        fig_show.axes8 = fig_show.fig.add_subplot(259)
        # F1.axes9 = F1.fig.add_subplot(260)
        fig_show.axes0.bar(index, map)
        fig_show.axes1.bar(index, recall)
        fig_show.axes2.bar(index, Precision)
        fig_show.axes3.bar(index, F1_)
        fig_show.axes4.bar(index, TP)
        fig_show.axes5.bar(index, FP)
        fig_show.axes6.bar(index, FN)
        fig_show.axes7.bar(index, ap)
        fig_show.axes8.bar(index, Thre)

        for a, b, i in zip(index, map, range(len(index))):  # zip 函数
            fig_show.axes0.text(a, b + 0.01, "%.2f" % map[i], ha='center', fontsize=10)  # plt.text 函数
        for a, b, i in zip(index, recall, range(len(index))):  # zip 函数
            fig_show.axes1.text(a, b + 0.01, "%.2f" % recall[i], ha='center', fontsize=10)  # plt.text 函数
        for a, b, i in zip(index, Precision, range(len(index))):  # zip 函数
            fig_show.axes2.text(a, b + 0.01, "%.2f" % Precision[i], ha='center', fontsize=10)  # plt.text 函数
        for a, b, i in zip(index, F1_, range(len(index))):  # zip 函数
            fig_show.axes3.text(a, b + 0.01, "%.2f" % F1_[i], ha='center', fontsize=10)  # plt.text 函数
        for a, b, i in zip(index, TP, range(len(index))):  # zip 函数
            fig_show.axes4.text(a, b + 0.01, "%.2f" % TP[i], ha='center', fontsize=10)  # plt.text 函数
        for a, b, i in zip(index, FP, range(len(index))):  # zip 函数
            fig_show.axes5.text(a, b + 0.01, "%.2f" % FP[i], ha='center', fontsize=10)  # plt.text 函数
        for a, b, i in zip(index, FN, range(len(index))):  # zip 函数
            fig_show.axes6.text(a, b + 0.01, "%.2f" % FN[i], ha='center', fontsize=10)  # plt.text 函数
        for a, b, i in zip(index, ap, range(len(index))):  # zip 函数
            fig_show.axes7.text(a, b + 0.01, "%.2f" % ap[i], ha='center', fontsize=10)  # plt.text 函数
        for a, b, i in zip(index, Thre, range(len(index))):  # zip 函数
            fig_show.axes8.text(a, b + 0.01, "%.2f" % Thre[i], ha='center', fontsize=10)  # plt.text 函数

        fig_show.axes0.set_title("Map")
        fig_show.axes1.set_title("recall")
        fig_show.axes2.set_title("Prediction")
        fig_show.axes3.set_title("F1")
        fig_show.axes4.set_title("TP")
        fig_show.axes5.set_title("FP")
        fig_show.axes6.set_title("FN")
        fig_show.axes7.set_title("Ap")
        fig_show.axes8.set_title("Threshold")

        self.gridlayout.addWidget(fig_show, 0, 2)
        # return fig_show

    def btn_draw_clicked_by_thresh(self):
        data = []
        for i in range(len(self.checkdatasets)):
            if self.checkdatasets[i].isChecked():
                data.append(self.datasets[i])
        model = []
        for j in range(len(self.checkmodels)):
            if self.checkmodels[j].isChecked():
                model.append(self.models[j])
        print(model)
        print(data)

        if len(data) == 1:
            self.draw_by_models(model, data[0])
        elif len(model) == 1:
            self.draw_by_datasets(model[0], data)
        else:
            print("ui2 erroe")

    def btn_draw(self):
        if self.filter_thresh == 0:
            self.btn_draw_clicked()
        else:
            self.btn_draw_clicked_by_thresh()

    def btn_draw_clicked(self):
        data = []
        for i in range(len(self.checkdatasets)):
            if self.checkdatasets[i].isChecked():
                data.append(self.datasets[i])
        model = []
        for j in range(len(self.checkmodels)):
            if self.checkmodels[j].isChecked():
                model.append(self.models[j])
        print(model)
        print(data)

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
            data_name = key.split('$')[-1]
            model_n = key.split('$' + data_name)[0]
            if not model_n == text:
                continue
            id_max = value
            class_name = class_name1[key]
            id_max.append(0)
            class_name.append('all')

            data = []
            for i in range(len(self.value)):
                if str(self.value[i][1]) == model_n and str(self.value[i][2]) == data_name:
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
                        self.model.setItem(row, n, QtGui.QStandardItem(str(round(a[id_max[m]][n],3))))
                    else:
                        self.model.setItem(row, n, QtGui.QStandardItem(str(a[id_max[m]][n])))

        self.model.itemChanged.connect(self.QStandardModelItemChanged)
        self.model.setHorizontalHeaderLabels(['ID', 'Model', 'dataset', 'class', 'TP', 'FP'
                                                 , 'FN', 'F1', 'Ap', 'Map', 'Precision', 'Recall', 'Threshold'])

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
            data_name = key.split('$')[-1]
            model_n = key.split('$' + data_name)[0]
            if not data_name == text:
                continue
            id_max = value
            class_name = class_name1[key]
            id_max.append(0)
            class_name.append('all')

            data = []
            for i in range(len(self.value)):
                if str(self.value[i][1]) == model_n and str(self.value[i][2]) == data_name:
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
                        self.model.setItem(row, n, QtGui.QStandardItem(str(round(a[id_max[m]][n],3))))
                    else:
                        self.model.setItem(row, n, QtGui.QStandardItem(str(a[id_max[m]][n])))

        self.model.itemChanged.connect(self.QStandardModelItemChanged)
        self.model.setHorizontalHeaderLabels(['ID', 'Model', 'dataset', 'class', 'TP', 'FP'
                                                 , 'FN', 'F1', 'Ap', 'Map', 'Precision', 'Recall', 'Threshold'])

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
            data_name = key.split('$')[-1]
            model_n = key.split('$' + data_name)[0]
            if model_n == text_model and data_name == text_datasets:

                id_max = value
                class_name = class_name1[key]
                id_max.append(0)
                class_name.append('all')

                data = []
                for i in range(len(self.value)):
                    if str(self.value[i][1] == model_n) and str(self.value[i][2]) == data_name:
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
                            self.model.setItem(row, n, QtGui.QStandardItem(str(round(a[id_max[m]][n],3))))
                        else:
                            self.model.setItem(row, n, QtGui.QStandardItem(str(a[id_max[m]][n])))

        self.model.itemChanged.connect(self.QStandardModelItemChanged)

    def btn_search_by_filter1(self):
        text = self.filter_line_ui3.text()
        cls = text.split('^')
        md = text.split('&')
        model_n = None
        data_name = None
        cls_name = None
        if len(md) == 1:
            if len(cls) == 1:
                cls_name = cls[0]
            else:
                data_name = cls[0]
                cls_name = cls[1]
        elif len(md) == 2:
            model_n = md[0]
            if len(cls) == 1:
                cls_name = md[1]
            else:
                cls_name = cls[1]
                data_name = md[1].split('^')[0]

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
            key_d = key.split('$')[-1]
            key_m = key.split('$' + key_d)[0]
            if data_name == None:
                data_name1 = key.split('$')[-1]
            else:
                data_name1 = data_name

            if model_n == None:
                model_n1 = key.split('$' + data_name1)[0]
            else:
                model_n1 = model_n
            if not data_name1 == key_d or not model_n1 == key_m:
                continue
            id_max = value
            class_name = class_name1[key]
            id_max.append(0)
            class_name.append('all')

            data = []
            for i in range(len(self.value)):
                if str(self.value[i][1]) == model_n1 and str(self.value[i][2]) == data_name1 and self.value[i][
                    3] == cls_name:
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
            if len(list[class_name.index(cls_name)]) > 0:
                row_ = self.model.rowCount()

                row = row_ + 0
                for n in range(13):
                    # item=QtGui.QStandardItem()
                    a = list[class_name.index(cls_name)]
                    if n > 5:
                        self.model.setItem(row, n,
                                           QtGui.QStandardItem(str(round(a[id_max[class_name.index(cls_name)]][n],3))))
                    else:

                        self.model.setItem(row, n, QtGui.QStandardItem(str(a[id_max[class_name.index(cls_name)]][n])))
            else:
                pass

        self.model.itemChanged.connect(self.QStandardModelItemChanged)

    def btn_refresh(self):
        self.model.clear()
        self.model.setHorizontalHeaderLabels(['ID', 'Model', 'dataset', 'class', 'TP', 'FP'
                                                 , 'FN', 'F1', 'Ap', 'Map', 'Precision', 'Recall', 'Threshold'])

        self.table_widget.setColumnWidth(1, 160)
        self.table_widget.setColumnWidth(2, 100)
        self.table_widget.setColumnWidth(3, 150)
        self.table_widget.setColumnWidth(0, 0)
        self.model.itemChanged.disconnect(self.QStandardModelItemChanged)

        id_max1, class_name1, datasets = self.DBManager.search_id()

        for key, value in id_max1.items():
            # for m1 in range(len(class_name1[key])):
            #     value[m1]+=1

            data_name = key.split('$')[-1]
            model_n = key.split('$' + data_name)[0]
            id_max = value
            class_name = class_name1[key]
            id_max.append(0)
            class_name.append('all')

            data = []
            for i in range(len(self.value)):
                if str(self.value[i][1]) == model_n and str(self.value[i][2]) == data_name:
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
                        self.model.setItem(row, n, QtGui.QStandardItem(str(round(list[m][id_max[m]][n],3))))
                    else:
                        self.model.setItem(row, n, QtGui.QStandardItem(str(list[m][id_max[m]][n])))

        self.model.itemChanged.connect(self.QStandardModelItemChanged)

    def refresh_thresh(self):
        global model_selecion, dataset_selection
        temp_models = model_selecion
        temp_dataset = dataset_selection
        self.model.clear()
        self.model.setHorizontalHeaderLabels(['ID', 'Model', 'dataset', 'class', 'TP', 'FP'
                                                 , 'FN', 'F1', 'Ap', 'Map', 'Precision', 'Recall', 'Threshold'])
        self.model.itemChanged.disconnect(self.QStandardModelItemChanged)
        try:
            self.model.itemChanged.disconnect(self.QStandardModelItemChanged)
        except:
            pass

        id_max1, class_name1, datasets = self.DBManager.search_id()

        if len(id_max1) == 0:
            return
        for key, value in id_max1.items():
            data_name = key.split('$')[-1]
            model_n = key.split('$' + data_name)[0]
            if not model_n in temp_models:
                continue
            if not data_name in temp_dataset:
                continue
            id_max = value
            class_name = class_name1[key]
            id_max.append(0)
            class_name.append('all')

            thresh_hold = []
            data = []
            for i in range(len(self.value)):
                if str(self.value[i][1]) == model_n and str(self.value[i][2]) == data_name:
                    data.append(self.value[i])

            # index_thresh = self.index_number(thresh_hold, float(0.8))

            class_num = len(class_name)
            list = [[]] * class_num
            thresh_hold = [[]] * class_num

            for i in range(len(data)):
                for l in range(class_num):
                    if data[i][3] == class_name[l] and data[i][3] in class_selection:
                        # if data[i][3] == class_name[l]:
                        if len(list[l]) == 0:
                            list[l] = [data[i]]
                            thresh_hold[l] = [data[i][12]]
                        else:
                            list[l].append(data[i])
                            thresh_hold[l].append(data[i][12])


            row_ = self.model.rowCount()
            for m in range(class_num):
                row = row_ + m
                temp_thresh_list = thresh_hold[m]
                if len(temp_thresh_list) > 0:
                    index_thresh = self.index_number(temp_thresh_list, float(0.8))
                else:
                    index_thresh = 0
                for n in range(13):
                    # item=QtGui.QStandardItem()
                    a = list[m]
                    if len(a) == 0:
                        continue
                    if n > 5:
                        self.model.setItem(row, n, QtGui.QStandardItem(str(a[index_thresh][n])[0:5]))
                    else:
                        self.model.setItem(row, n, QtGui.QStandardItem(str(a[index_thresh][n])))

        self.model.itemChanged.connect(self.QStandardModelItemChanged)
        self.model.setHorizontalHeaderLabels(['ID', 'Model', 'dataset', 'class', 'TP', 'FP'
                                                 , 'FN', 'F1', 'Ap', 'Map', 'Precision', 'Recall', 'Threshold'])
        self.filter_thresh = 1

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
            if str(self.value[i][1]) == model and str(self.value[i][2]) == data and self.value[i][3] == class_:
                a.append(self.value[i][12])
                b.append(self.value[i])
        index = self.index_number(a, float(thre))

        for j in range(13):
            if j > 5:
                self.model.setItem(r, j, QtGui.QStandardItem(str(round(b[index][j],3))))
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

    def btn_load_selection(self):
        global dataset_selection, model_selecion
        pre_models, pre_datasets = self.models, self.datasets
        tmp_dataset = []
        tmp_model = []
        for new_model in model_selecion:
            if new_model in pre_models:
                # p = pre_models.index(new_model)
                # self.checkmodels[p].setChecked(False)
                continue
            else:
                tmp_model.append(new_model)
        for new_dataset in dataset_selection:
            if new_dataset in pre_datasets:
                # p = pre_datasets.index(new_dataset)
                # self.checkdatasets[p].setChecked(False)
                continue
            else:
                tmp_dataset.append(new_dataset)

        if not len(tmp_model) == 0:
            self.checkmodels.extend(tmp_model)
            self.models.extend(tmp_model)
            for i in range(len(tmp_model)):
                self.checkmodels[i] = QCheckBox(str(tmp_model[i]))
                self.checkmodels[i].stateChanged.connect(self.btn_draw)
                self.group_box_layout.addWidget(self.checkmodels[i])

        if not len(tmp_dataset) == 0:
            self.checkdatasets.extend(tmp_dataset)
            self.datasets.extend(tmp_dataset)
            for i in range(len(tmp_dataset)):
                self.checkdatasets[i] = QCheckBox(str(tmp_dataset[i]))
                self.checkdatasets[i].stateChanged.connect(self.btn_draw)
                self.group_box_layout1.addWidget(self.checkdatasets[i])

        for i in range(len(tmp_model)):
            self.checkmodels[i].setChecked(True)
        self.checkdatasets[0].setChecked(True)

        self.btn_show_classes_clicked()

    def btn_load_diff_thresh(self):
        if self.filter_thresh == 1:
            self.filter_thresh = 0
        else:
            self.filter_thresh = 1
        global dataset_selection, model_selecion
        pre_models, pre_datasets = self.models, self.datasets
        tmp_dataset = []
        tmp_model = []
        for new_model in model_selecion:
            if new_model in pre_models:
                # p = pre_models.index(new_model)
                # self.checkmodels[p].setChecked(False)
                continue
            else:
                tmp_model.append(new_model)
        for new_dataset in dataset_selection:
            if new_dataset in pre_datasets:
                # p = pre_datasets.index(new_dataset)
                # self.checkdatasets[p].setChecked(False)
                continue
            else:
                tmp_dataset.append(new_dataset)

        if not len(tmp_model) == 0:
            self.checkmodels.extend(tmp_model)
            self.models.extend(tmp_model)
            for i in range(len(tmp_model)):
                self.checkmodels[i] = QCheckBox(str(tmp_model[i]))
                self.checkmodels[i].stateChanged.connect(self.btn_draw)
                self.group_box_layout.addWidget(self.checkmodels[i])

        if not len(tmp_dataset) == 0:
            self.checkdatasets.extend(tmp_dataset)
            self.datasets.extend(tmp_dataset)
            for i in range(len(tmp_dataset)):
                self.checkdatasets[i] = QCheckBox(str(tmp_dataset[i]))
                self.checkdatasets[i].stateChanged.connect(self.btn_draw)
                self.group_box_layout1.addWidget(self.checkdatasets[i])

        for i in range(len(tmp_model)):
            self.checkmodels[i].setChecked(True)
        self.checkdatasets[0].setChecked(True)

        self.btn_show_classes_clicked()

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

    def btn_main_database_clicked(self):
        if self.main_database_dir.text() == '':
            txt = self.current_directory
        else:
            txt = self.txb_gt_dir.text()
        directory = QFileDialog.getOpenFileName(
            self, 'Choose file with Main Database', txt)
        if directory == '':
            return
        file_path = directory[0]
        if os.path.isfile(file_path):
            self.main_database_dir.setText(file_path)
            self.main_database_dir_ = file_path
        else:
            self.main_database_dir_ = None
            self.main_database_dir.setText('')

    def btn_ano_database_clicked(self):
        if self.ano_database_dir.text() == '':
            txt = self.current_directory
        else:
            txt = self.ano_database_dir.text()
        directory = QFileDialog.getOpenFileName(
            self, 'Choose file with Main Database', txt)
        if directory == '':
            return
        file_path = directory[0]
        if os.path.isfile(file_path):
            self.ano_database_dir.setText(file_path)
            self.ano_database_dir_ = file_path
        else:
            self.ano_database_dir_ = None
            self.ano_database_dir.setText('')

    def merge_database(self):
        DBManager_Changed().merge(self.main_database_dir_, self.ano_database_dir_)
