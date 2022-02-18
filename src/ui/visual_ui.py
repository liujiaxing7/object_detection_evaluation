# -*- coding: utf-8 -*-
'''
@author: 刘家兴
@contact: ljx0ml@163.com
@file: model.py
@time: 2021/8/24 18.46
@desc:
'''
import random
import sys
from decimal import Decimal

from PyQt5 import QtGui, QtCore, QtWidgets, QtSql
from PyQt5.QtCore import Qt, QRect, QThread, pyqtSignal
from PyQt5.QtSql import QSqlQuery
from PyQt5.QtWidgets import *

import os
import sys
from cv2 import cv2
import onnx
import numpy as np
from tqdm import tqdm

# matplotlib.use("Qt5Agg")
from src.database.db import DBManager, MyFigure
from src.database.db_concat import DBManagerChanged

MAIN_WINDOW_GEOMETRY = [300, 300, 1380, 800]
SUBDIALOG_GEOMETRY = [400, 400, 200, 400]
SUB_WINDOW_GEOMETRY = [400, 400, 1000, 400]
WHITE_COLOR = QtGui.QColor(255, 255, 255)
GRAY_COLOR = QtGui.QColor(125, 125, 125)
TABLE_VALUE_NUMS = 13


global subDBManager, models, datasets, classes
subDBManager = DBManager()
models, datasets = subDBManager.searchModelDatasets()
classes = subDBManager.searchAllClasses()

global model_selecion, dataset_selection, class_selection, all_model_names, all_dataset_names, all_class_names
all_model_names = models.copy()
all_dataset_names = datasets.copy()
all_class_names = classes.copy()
model_selecion, dataset_selection, class_selection = [], [], []

# error file save path
global save_path, error_file_list
save_path = 'error_file.list'
error_file_list = []

global model_dataset_dict, model_classes_dict
model_dataset_dict, model_classes_dict = subDBManager.searchMatchedModelsDatasetsClasses()


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

        self.setGeometry(SUBDIALOG_GEOMETRY[0], SUBDIALOG_GEOMETRY[1], SUBDIALOG_GEOMETRY[2], SUBDIALOG_GEOMETRY[3])
        self.centerScreen()
        self.initUI()
        self.show()
        self.memoryUI()

    def initUI(self):
        # 实例化垂直布局
        self.models_box = QGridLayout()
        self.bt_add = QPushButton('add item')
        self.bt_add.setGeometry(QtCore.QRect(0, 0, 20, 20))
        self.bt_add.clicked.connect(self.saveSelection)
        # self.hbox.addStretch(5)
        self.all_check_box = QCheckBox('All')
        self.all_check_box.stateChanged.connect(self.selectAll)
        self.models_box.addWidget(self.all_check_box, 0, 0)

        m, n = 1, 0
        for i in range(len(self.models)):
            self.checkmodels[i] = QCheckBox(str(self.models[i]))
            self.checkmodels[i].stateChanged.connect(self.btnDrawClicked)
            if i > 0 and i % 5 == 0:
                m += 1
                n = 0
            self.models_box.addWidget(self.checkmodels[i], m, n)
            n += 1
        # for i in range(len(self.datasets)):
        #     self.checkdatasets[i] = QCheckBox(str(self.datasets[i]))
        #     self.checkdatasets[i].stateChanged.connect(self.btnDrawClicked)
        #     self.models_box.addWidget(self.checkdatasets[i])

        self.setLayout(self.models_box)  # 设置窗体布局

    def memoryUI(self):
        global model_selecion
        tmp_model = model_selecion
        for i in range(len(self.models)):
            if str(self.models[i]) in tmp_model:
                self.checkmodels[i].setChecked(True)


    def centerScreen(self):
        size = self.size()
        desktopSize = QtWidgets.QDesktopWidget().screenGeometry()
        top = (desktopSize.height() / 2) - (size.height() / 2)
        left = (desktopSize.width() / 2) - (size.width() / 2)
        self.move(left, top)
    def saveSelection(self):
        print('')
    def btnDrawClicked(self):
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

    def selectAll(self, status):
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

        self.setGeometry(SUBDIALOG_GEOMETRY[0], SUBDIALOG_GEOMETRY[1], SUBDIALOG_GEOMETRY[2], SUBDIALOG_GEOMETRY[3])
        self.centerScreen()
        self.initUI()
        self.show()
        self.memoryUI()

    def initUI(self):
        global dataset_selection
        # 实例化垂直布局
        self.datasets_box = QGridLayout()
        self.bt_add = QPushButton('add item')
        self.bt_add.setGeometry(QtCore.QRect(0, 0, 20, 20))
        self.bt_add.clicked.connect(self.saveSelection)
        # self.hbox.addStretch(5)
        self.all_check_box = QCheckBox('All')
        self.all_check_box.stateChanged.connect(self.selectAll)
        self.datasets_box.addWidget(self.all_check_box, 0, 0)

        m, n = 1, 0
        for i in range(len(self.datasets)):
            self.checkdatasets[i] = QCheckBox(str(self.datasets[i]))
            self.checkdatasets[i].stateChanged.connect(self.btnDrawClicked)
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

    def centerScreen(self):
        size = self.size()
        desktopSize = QtWidgets.QDesktopWidget().screenGeometry()
        top = (desktopSize.height() / 2) - (size.height() / 2)
        left = (desktopSize.width() / 2) - (size.width() / 2)
        self.move(left, top)

    def saveSelection(self):
        print('')

    def btnDrawClicked(self):
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

    def selectAll(self, status):
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

        self.setGeometry(SUBDIALOG_GEOMETRY[0], SUBDIALOG_GEOMETRY[1], SUBDIALOG_GEOMETRY[2], SUBDIALOG_GEOMETRY[3])
        self.centerScreen()
        self.initUI()
        self.show()
        self.memoryUI()

    def initUI(self):
        # 实例化垂直布局
        self.classes_box = QGridLayout()

        self.all_check_box = QCheckBox('All')
        self.all_check_box.stateChanged.connect(self.selectAll)
        self.classes_box.addWidget(self.all_check_box, 0, 0)

        m, n = 1, 0
        for i in range(len(self.classes)):
            self.checkclasses[i] = QCheckBox(str(self.classes[i]))
            self.checkclasses[i].stateChanged.connect(self.btnDrawClicked)
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


    def centerScreen(self):
        size = self.size()
        desktopSize = QtWidgets.QDesktopWidget().screenGeometry()
        top = (desktopSize.height() / 2) - (size.height() / 2)
        left = (desktopSize.width() / 2) - (size.width() / 2)
        self.move(left, top)

    def saveSelection(self):
        print('')

    def btnDrawClicked(self):
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

    def selectAll(self, status):
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


class Sub_window(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(Sub_window, self).__init__(parent)
        self.setWindowTitle('Model and DataSet selection')
        global model_dataset_dict, model_classes_dict
        self.model_dataset_dict, self.model_classes_dict =  model_dataset_dict, model_classes_dict
        global subDBManager, models, datasets, classes
        self.models, self.datasets, self.classes = models, datasets, classes
        self.checkmodels = models.copy()
        self.checkdatasets = datasets.copy()
        self.checkclasses = classes.copy()
        self.table = QTabWidget(self)
        self.vbox_stretch = QVBoxLayout()
        self.table.setMinimumSize(900, 400)

        self.setGeometry(SUB_WINDOW_GEOMETRY[0], SUB_WINDOW_GEOMETRY[1], SUB_WINDOW_GEOMETRY[2], SUB_WINDOW_GEOMETRY[3])
        self.centerScreen()
        self.initUI()
        self.show()
        self.memoryUI()

    def initUI(self):
        self.model_tab = QtWidgets.QWidget()
        self.dataset_tab = QtWidgets.QWidget()
        self.class_tab = QtWidgets.QWidget()

        self.table.addTab(self.model_tab, "Model Selection")
        self.table.addTab(self.dataset_tab, "Dataset Selection")
        self.table.addTab(self.class_tab, "Classes Selection")

        self.initModelUI()
        self.initDatasetUI()
        self.initClassesUI()
        self.vbox_stretch.addWidget(self.table)
        self.setLayout(self.vbox_stretch)

    def centerScreen(self):
        size = self.size()
        desktopSize = QtWidgets.QDesktopWidget().screenGeometry()
        top = (desktopSize.height() / 2) - (size.height() / 2)
        left = (desktopSize.width() / 2) - (size.width() / 2)
        self.move(left, top)

    def initModelUI(self):
        # 实例化垂直布局
        self.models_box = QGridLayout()

        self.all_check_box_model = QCheckBox('All')
        self.all_check_box_model.stateChanged.connect(self.selectAllModels)
        self.models_box.addWidget(self.all_check_box_model, 0, 0)

        m, n = 1, 0
        for i in range(len(self.models)):
            self.checkmodels[i] = QCheckBox(str(self.models[i]))
            self.checkmodels[i].stateChanged.connect(self.btnDrawModelsClicked)
            if i > 0 and i % 5 == 0:
                m += 1
                n = 0
            self.models_box.addWidget(self.checkmodels[i], m, n)
            n += 1

        self.model_tab.setLayout(self.models_box)

    def initDatasetUI(self):
        global dataset_selection
        # 实例化垂直布局
        self.datasets_box = QGridLayout()
        self.all_check_box_datasets = QCheckBox('All')
        self.all_check_box_datasets.stateChanged.connect(self.selectAllDatasets)
        self.datasets_box.addWidget(self.all_check_box_datasets, 0, 0)

        m, n = 1, 0
        for i in range(len(self.datasets)):
            self.checkdatasets[i] = QCheckBox(str(self.datasets[i]))
            self.checkdatasets[i].stateChanged.connect(self.btnDrawDatasetsClicked)
            if i > 0 and i % 5 == 0:
                m += 1
                n = 0
            self.datasets_box.addWidget(self.checkdatasets[i], m, n)
            n += 1
        self.dataset_tab.setLayout(self.datasets_box)

    def initClassesUI(self):
        # 实例化垂直布局
        self.classes_box = QGridLayout()

        self.all_check_box_classes = QCheckBox('All')
        self.all_check_box_classes.stateChanged.connect(self.selectAllClasses)
        self.classes_box.addWidget(self.all_check_box_classes, 0, 0)

        m, n = 1, 0
        for i in range(len(self.classes)):
            self.checkclasses[i] = QCheckBox(str(self.classes[i]))
            self.checkclasses[i].stateChanged.connect(self.btnDrawClassesClicked)
            if i > 0 and i % 5 == 0:
                m += 1
                n = 0
            self.classes_box.addWidget(self.checkclasses[i], m, n)
            n += 1
        self.class_tab.setLayout(self.classes_box)

    def selectAllDatasets(self, status):
        if status == 2:
            for i in range(len(self.checkdatasets)):
                self.checkdatasets[i].setChecked(True)
        elif status == 1:
            if self.Selectedrow_num == 0:
                self.all_check_box_datasets.setCheckState(2)
        elif status == 0:
            self.clearDatasets()

    def clearDatasets(self):
        for i in range(len(self.datasets)):
            self.checkdatasets[i].setChecked(False)
        self.all_check_box_datasets.setChecked(False)

    def selectAllModels(self, status):
        if status == 2:
            for i in range(len(self.checkmodels)):
                self.checkmodels[i].setChecked(True)
        elif status == 1:
            if self.Selectedrow_num == 0:
                self.all_check_box_model.setCheckState(2)
        elif status == 0:
            self.clearModels()

    def clearModels(self):
        for i in range(len(self.models)):
            self.checkmodels[i].setChecked(False)
        self.all_check_box_model.setChecked(False)

    def selectAllClasses(self, status):
        if status == 2:
            for i in range(len(self.checkclasses)):
                self.checkclasses[i].setChecked(True)
        elif status == 1:
            if self.Selectedrow_num == 0:
                self.all_check_box_classes.setCheckState(2)
        elif status == 0:
            self.clearClasses()

    def clearClasses(self):
        for i in range(len(self.checkclasses)):
            self.checkclasses[i].setChecked(False)
        self.all_check_box_classes.setChecked(False)

    def btnDrawClassesClicked(self):
        data = []
        for i in range(len(self.checkclasses)):
            if self.checkclasses[i].isChecked():
                data.append(self.classes[i])
        self.Selectedrow_num = len(data)
        if self.Selectedrow_num == 0:
            self.all_check_box_classes.setCheckState(0)
        elif self.Selectedrow_num == len(self.checkclasses):
            self.all_check_box_classes.setCheckState(2)
        else:
            self.all_check_box_classes.setCheckState(1)
        global class_selection
        class_selection = data.copy()

    def btnDrawModelsClicked(self):
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
            self.all_check_box_model.setCheckState(0)
        elif self.Selectedrow_num == len(self.checkmodels):
            self.all_check_box_model.setCheckState(2)
        else:
            self.all_check_box_model.setCheckState(1)
        global model_selecion
        model_selecion = model.copy()
        self.memoryUI()

    def btnDrawDatasetsClicked(self):
        data = []
        for i in range(len(self.checkdatasets)):
            if self.checkdatasets[i].isChecked():
                data.append(self.datasets[i])
        self.Selectedrow_num = len(data)
        if self.Selectedrow_num == 0:
            self.all_check_box_datasets.setCheckState(0)
        elif self.Selectedrow_num == len(self.checkdatasets):
            self.all_check_box_datasets.setCheckState(2)
        else:
            self.all_check_box_datasets.setCheckState(1)
        global dataset_selection
        dataset_selection = data.copy()

    def memoryUI(self):
        global dataset_selection, model_selecion, class_selection
        global model_dataset_dict, model_classes_dict
        tmp_model = model_selecion
        for i in range(len(self.models)):
            if str(self.models[i]) in tmp_model:
                self.checkmodels[i].setChecked(True)
        match_index_datasets = []
        match_index_classes = []
        for index_model in tmp_model:
            match_dataset = model_dataset_dict[index_model]
            match_class = model_classes_dict[index_model]
            for index_match_dataset in match_dataset:
                if index_match_dataset not in match_index_datasets:
                    match_index_datasets.append(index_match_dataset)
            for index_match_class in match_class:
                if index_match_class not in match_index_classes:
                    match_index_classes.append(index_match_class)

        for i in range(len(self.datasets)):
            if str(self.datasets[i]) in match_index_datasets:
                self.checkdatasets[i].setEnabled(True)
                self.checkdatasets[i].setChecked(True)
            else:
                self.checkdatasets[i].setChecked(False)
                self.checkdatasets[i].setEnabled(False)

        for i in range(len(self.classes)):
            if str(self.classes[i]) in match_index_classes:
                self.checkclasses[i].setEnabled(True)
                self.checkclasses[i].setChecked(True)
            else:
                self.checkclasses[i].setChecked(False)
                self.checkclasses[i].setEnabled(False)
        class_selection = match_index_classes
        dataset_selection = match_index_datasets


class Ui_Window(QTabWidget):
    def __init__(self, parent=None):
        super(Ui_Window, self).__init__(parent)
        # set window size
        self.setGeometry(MAIN_WINDOW_GEOMETRY[0], MAIN_WINDOW_GEOMETRY[1], MAIN_WINDOW_GEOMETRY[2], MAIN_WINDOW_GEOMETRY[3])

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
        self.filter_thresh = 1
        self.class_dict = {'person': 0, 'escalator': 1, 'escalator_handrails': 2, 'person_dummy': 3,
                           'escalator_model': 4, 'escalator_handrails_model': 5}

        self.centerScreen()
        # sys.stdout = Stream(newText=self.onUpdateText)

        # global subDBManager, models, datasets
        # self.models = models.copy()
        # self.datasets = datasets.copy()
        self.DBManager = DBManager()
        self.thr_id_max, self.id_max_class_name1, self.id_max_datasets = self.DBManager.searchId()

        self.eval_tab = QtWidgets.QWidget()
        self.view_tab = QtWidgets.QWidget()
        self.selection_tab = QtWidgets.QWidget()
        self.error_tab = QtWidgets.QWidget()
        self.merge_tab = QtWidgets.QWidget()
        self.addTab(self.eval_tab, "Detection Metrics")
        self.addTab(self.view_tab, "Visual Comparsion")
        self.addTab(self.selection_tab, "Show Database")
        self.addTab(self.error_tab, "Error File Preview")
        self.addTab(self.merge_tab, "Database Manager")
        self.initEvalUI()
        self.initViewUI()
        self.initSelectionUI()
        self.initErrorUI()
        self.initMergeUI()
        self.setWindowTitle("Object Detection Metrics")

    def initEvalUI(self):
        eval_layout = QFormLayout()

        gt = QHBoxLayout()
        font = QtGui.QFont()
        font.setBold(True)
        font.setPixelSize(25)
        gt_label = QLabel("Ground truth")
        gt.addWidget(gt_label, 1, Qt.AlignCenter)

        gt_label.setFont(font)
        eval_layout.addRow(gt)

        model_hbox = QHBoxLayout()
        model_hbox.addWidget(QLabel("Model:       "))
        self.txb_gt_dir = QLineEdit()
        self.txb_gt_dir.setReadOnly(True)
        model_hbox.addWidget(self.txb_gt_dir)
        self.load_model_dir = QPushButton("...")
        model_hbox.addWidget(self.load_model_dir)
        self.load_model_dir.clicked.connect(self.btnGtDirClicked)
        eval_layout.addRow(model_hbox)

        images_hbox = QHBoxLayout()
        images_hbox.addWidget(QLabel("Images:     "))
        self.txb_gt_images_dir = QLineEdit()
        self.txb_gt_images_dir.setReadOnly(True)
        images_hbox.addWidget(self.txb_gt_images_dir)
        self.load_images_dir = QPushButton("...")
        images_hbox.addWidget(self.load_images_dir)
        self.load_images_dir.clicked.connect(self.btnGtImagesDirClicked)
        eval_layout.addRow(images_hbox)

        class_hbox = QHBoxLayout()
        class_hbox.addWidget(QLabel("Classes(*):"))
        self.txb_classes_gt = QLineEdit()
        self.txb_classes_gt.setReadOnly(True)
        class_hbox.addWidget(self.txb_classes_gt)
        self.load_class_dir = QPushButton("...")
        class_hbox.addWidget(self.load_class_dir)
        self.load_class_dir.clicked.connect(self.btnGtClassesClicked)
        eval_layout.addRow(class_hbox)
        eval_layout.addRow(QLabel("                     * required for yolo (.txt) format only."))
        eval_layout.addRow(QLabel(''))

        label_vbox = QVBoxLayout()
        format_w = QWidget()
        frame = QFrame(format_w)
        frame.setMinimumSize(2000, 100)
        frame.setStyleSheet("background-color: #feeeed")

        content_hbox = QHBoxLayout()
        gt_format = QLabel("Coordinates format:")
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        gt_format.setFont(font)
        content_hbox.addWidget(gt_format)
        label_vbox.addLayout(content_hbox)

        label_type_hbox = QHBoxLayout()
        self.rad_gt_format_coco_json = QRadioButton("COCO (.json)")
        self.rad_gt_format_pascalvoc_xml = QRadioButton("PASCAL VOC (.xml)")
        self.rad_gt_format_labelme_xml = QRadioButton("Label Me (.xml)")
        self.rad_gt_format_yolo_text = QRadioButton("(*) YOLO (.txt)")
        label_type_hbox.addWidget(self.rad_gt_format_coco_json)
        label_type_hbox.addWidget(self.rad_gt_format_pascalvoc_xml)
        label_type_hbox.addWidget(self.rad_gt_format_labelme_xml)
        label_type_hbox.addWidget(self.rad_gt_format_yolo_text)
        label_vbox.addLayout(label_type_hbox)

        format_w.setLayout(label_vbox)
        eval_layout.addWidget(format_w)
        eval_layout.addRow(QLabel(' '))

        onnx_type_hbox = QHBoxLayout()
        onnx_type_hbox.addWidget(QLabel("Onnx Model Type:"), 2, Qt.AlignLeft)
        self.combobox_process = QComboBox()

        onnx_type_hbox.addWidget(self.combobox_process, 9, Qt.AlignLeft)
        self.combobox_process.addItems(['', 'yolov3', 'yolov3_padding', 'yolov5', 'yolov5x', 'yolov3_tiny3', 'yolov3_tiny3_padding', 'yolov3_mmdetection'])

        self.combobox_process.setMinimumSize(200, 27)
        self.combobox_process.currentIndexChanged.connect(self.comboSelectionChangedModels)
        onnx_type_hbox.addWidget(QLabel("Datasets Name:"), 0, Qt.AlignLeft)
        self.txt_gt_data_name = QLineEdit()
        self.txt_gt_data_name.setPlaceholderText("默认为数据集文件夹名")
        self.txt_gt_data_name.setMinimumSize(200, 27)
        onnx_type_hbox.addWidget(self.txt_gt_data_name, 20, Qt.AlignLeft)
        btn_save = QPushButton("save")
        onnx_type_hbox.addWidget(btn_save, 1, Qt.AlignRight)
        btn_save.setMinimumSize(60, 27)
        btn_save.clicked.connect(self.btnSaveClicked)
        eval_layout.addRow(onnx_type_hbox)

        self.process = QTextEdit()
        eval_layout.addRow(self.process)

        [eval_layout.addRow(QLabel('')) for i in range(10)]

        button_hbox = QHBoxLayout()
        self.btn_run = QPushButton("RUN")
        self.btn_run.clicked.connect(self.btnRunClicked)
        button_hbox.addWidget(self.btn_run)
        self.btn_run.setStyleSheet(
            '''QPushButton{background:#afb4db;border-radius:5px;}QPushButton:hover{background:#9b95c9;}''')

        eval_layout.addRow(button_hbox)

        self.eval_tab.setLayout(eval_layout)

    def initViewUI(self):
        self.checkmodels, self.checkdatasets, self.models, self.datasets = [], [], [], []
        view_layout = QFormLayout()

        gt = QHBoxLayout()
        font = QtGui.QFont()
        font.setBold(True)
        font.setPixelSize(25)
        gt_label = QLabel("Visual Comparsion")
        gt.addWidget(gt_label, 1, Qt.AlignCenter)
        gt_label.setFont(font)
        view_layout.addRow(gt, )
        view_layout.addRow(QLabel(''))

        class_load_hbox = QHBoxLayout()
        class_load_hbox.addWidget(QLabel("Load classes:"), 1, Qt.AlignLeft)
        self.combobox_classes = QComboBox()
        self.combobox_classes.setMinimumSize(200, 27)
        self.combobox_classes.currentIndexChanged.connect(self.comboSelectionChangedClasses)
        class_load_hbox.addWidget(self.combobox_classes, 5, Qt.AlignLeft)

        select_model = QPushButton("Model Select")
        select_model.setMinimumSize(100, 27)
        select_model.clicked.connect(self.popModelSelect)
        class_load_hbox.addWidget(select_model, 1, Qt.AlignRight)

        select_dataset = QPushButton("Dataset Select")
        select_dataset.setMinimumSize(100, 27)
        select_dataset.clicked.connect(self.popDatasetSelect)
        class_load_hbox.addWidget(select_dataset, 1, Qt.AlignRight)

        select_best_thresh = QPushButton("Load other threshold")
        select_best_thresh.setMinimumSize(100, 27)
        select_best_thresh.clicked.connect(self.btnLoadDiffThresh)
        class_load_hbox.addWidget(select_best_thresh, 1, Qt.AlignRight)

        view_layout.addRow(class_load_hbox)

        models_grid = QGridLayout()
        group_model_box = QtWidgets.QGroupBox('Model')
        self.group_box_model_layout = QtWidgets.QHBoxLayout()
        group_model_box.setLayout(self.group_box_model_layout)

        group_model_box.setMinimumSize(100, 10)
        models_grid.addWidget(group_model_box, 0, 0, 1, 2)

        self._group_dataset_box = QtWidgets.QGroupBox('Datasets')
        self.group_box_dataset_layout = QtWidgets.QVBoxLayout()
        self._group_dataset_box.setLayout(self.group_box_dataset_layout)

        self._group_dataset_box.setMaximumSize(200, 1000)
        models_grid.addWidget(self._group_dataset_box, 1, 0)
        # self.btnLoadMd()

        self.draw_grid = QWidget()
        self._groupBox = QGroupBox(self.draw_grid)
        self.gridlayout = QGridLayout(self._groupBox)
        self.draw_grid.setLayout(self.gridlayout)
        self.draw_grid.setVisible(False)
        models_grid.addWidget(self.draw_grid, 1, 1)
        view_layout.addRow(models_grid)

        self.view_tab.setLayout(view_layout)

    def initSelectionUI(self):

        select_layout = QFormLayout()
        gt = QHBoxLayout()
        font = QtGui.QFont()
        font.setBold(True)
        font.setPixelSize(25)
        gt_label = QLabel("Show Database")
        gt.addWidget(gt_label, 1, Qt.AlignCenter)
        gt_label.setFont(font)
        select_layout.addRow(gt)
        select_layout.addRow(QLabel(''))

        dataset_hbox = QHBoxLayout()
        dataset_hbox.addWidget(QLabel("Datasets name："))
        self.data_line_ui3 = QLineEdit()
        dataset_hbox.addWidget(self.data_line_ui3)
        search_by_data = QPushButton("Search by Data")
        dataset_hbox.addWidget(search_by_data)
        search_by_data.clicked.connect(self.btnSearchByData)
        dataset_hbox.addWidget(QLabel(" Models name："))
        self.model_line_ui3 = QLineEdit()
        dataset_hbox.addWidget(self.model_line_ui3)
        search_by_model = QPushButton("Search by Model")
        dataset_hbox.addWidget(search_by_model)
        search_by_model.clicked.connect(self.btnSearchByModel)
        dataset_hbox.addWidget(QLabel(" Filter condition："))
        self.filter_line_ui3 = QLineEdit()
        self.filter_line_ui3.setPlaceholderText("m&d^c/m^c/d^c")
        dataset_hbox.addWidget(self.filter_line_ui3)
        search_by_filter = QPushButton("Search by condition")
        dataset_hbox.addWidget(search_by_filter)
        search_by_filter.clicked.connect(self.btnSearchByFilterOption)
        refresh = QPushButton("Refresh")
        dataset_hbox.addWidget(refresh)
        refresh.clicked.connect(self.btnRefresh)
        select_layout.addRow(dataset_hbox)

        pop_subwindow = QHBoxLayout()
        select_model = QPushButton("Model/dataset/classes Select")
        select_model.clicked.connect(self.popSubSelect)

        pop_subwindow.addWidget(select_model)

        search_by_selection = QPushButton("search by Selections")
        search_by_selection.clicked.connect(self.searchSelection)
        pop_subwindow.addWidget(search_by_selection)

        search_by_thresh = QPushButton("refresh by threshold0.8")
        search_by_thresh.clicked.connect(self.refreshByThresh)
        pop_subwindow.addWidget(search_by_thresh)
        select_layout.addRow(pop_subwindow)


        table_grid = QGridLayout()
        self.table_widget = QtWidgets.QTableView()

        self.table_widget.horizontalHeader().setStretchLastSection(True)
        self.table_widget.verticalHeader().setStretchLastSection(True)

        query = QSqlQuery()
        self.value = []
        if query.exec(
                'select id ,model_name,dataset_name,class_name,TP,FP,FN,F1,Ap,Map,Precision,Recall,Threshold from metric_'):
            while query.next():
                value_ = [query.value(i) for i in range(TABLE_VALUE_NUMS)]
                self.value.append(value_)

        self.model = QtGui.QStandardItemModel()

        self.table_widget.setSortingEnabled(True)
        self.table_widget.setColumnWidth(1, 160)
        self.table_widget.setColumnWidth(2, 150)
        self.table_widget.setColumnWidth(3, 150)
        self.table_widget.setModel(self.model)
        # self.table_widget.setColumnWidth(0, 50)


        self.model.itemChanged.connect(self.setQStandardModelItemChanged)
        self.table_widget.doubleClicked.connect(self.doubleClicked)
        self.table_widget.clicked.connect(self.selectClicked)
        if len(self.value) != 0:
            self.btnRefresh()
        for i in range(12):
            self.table_widget.setItemDelegateForColumn(i, EmptyDelegate(self))
        self.table_widget.setEditTriggers(QAbstractItemView.AllEditTriggers)

        table_grid.addWidget(self.table_widget)
        select_layout.addRow(table_grid)

        self.selection_tab.setLayout(select_layout)

    def initErrorUI(self):

        error_layout = QFormLayout()
        gt = QHBoxLayout()
        font = QtGui.QFont()
        font.setBold(True)
        font.setPixelSize(25)
        gt_label = QLabel("Error File")
        gt.addWidget(gt_label, 1, Qt.AlignCenter)
        gt_label.setFont(font)
        error_layout.addRow(gt)
        error_layout.addRow(QLabel(''))

        error_dataset_hbox = QHBoxLayout()
        error_dataset_hbox.addWidget(QLabel("Datasets name："))
        self.data_line_ui4 = QLineEdit()
        error_dataset_hbox.addWidget(self.data_line_ui4)
        search_by_data = QPushButton("Search by Data")
        error_dataset_hbox.addWidget(search_by_data)
        search_by_data.clicked.connect(self.btnSearchByDataError)
        error_dataset_hbox.addWidget(QLabel(" Models name："))
        self.model_line_ui4 = QLineEdit()
        error_dataset_hbox.addWidget(self.model_line_ui4)
        search_by_model = QPushButton("Search by Model")
        error_dataset_hbox.addWidget(search_by_model)
        search_by_model.clicked.connect(self.btnSearchByModelError)
        error_dataset_hbox.addWidget(QLabel(" Filter condition："))
        self.filter_line_ui4 = QLineEdit()
        error_dataset_hbox.addWidget(self.filter_line_ui4)
        search_by_filter = QPushButton("Search by condition")
        error_dataset_hbox.addWidget(search_by_filter)
        search_by_filter.clicked.connect(self.btnSearchByFilterError)
        refresh = QPushButton("Refresh")
        error_dataset_hbox.addWidget(refresh)
        refresh.clicked.connect(self.btnRefreshError)
        error_layout.addRow(error_dataset_hbox)

        pop_subwindow = QHBoxLayout()

        select_classes = QPushButton("models/datasets/classes Select")
        select_classes.clicked.connect(self.popErrorSelect)
        pop_subwindow.addWidget(select_classes)


        # self.search_for_error = QPushButton("search for error")
        # self.search_for_error.clicked.connect(self.searchError)
        # pop_subwindow.addWidget(self.search_for_error)

        label_text = QLabel("error save path:")
        label_text.setMaximumWidth(100)
        pop_subwindow.addWidget(label_text)
        self.error_path = QLineEdit()
        self.error_path.setMaximumWidth(200)
        pop_subwindow.addWidget(self.error_path)
        # self.load_save_dir = QPushButton("...")
        # self.load_save_dir.setMaximumWidth(40)
        # pop_subwindow.addWidget(self.load_save_dir)
        # self.load_save_dir.clicked.connect(self.btnSaveDirClicked)

        self.export_selection = QPushButton("export error")
        self.export_selection.clicked.connect(self.exportError)
        pop_subwindow.addWidget(self.export_selection)

        error_layout.addRow(pop_subwindow)

        error_table_grid = QGridLayout()
        self.error_table_view_widget = QtWidgets.QTableView()
        self.error_table_view_widget.horizontalHeader().setStretchLastSection(True)
        self.error_table_view_widget.verticalHeader().setStretchLastSection(True)

        db_text = os.getcwd() + '/src/database/core'

        # 实例化一个可编辑数据模型
        self.error_model = QtGui.QStandardItemModel()

        self.error_table_view_widget.setModel(self.error_model)
        # self.error_model.itemChanged.connect(self.setQStandardModelItemChanged)
        self.error_table_view_widget.setSortingEnabled(True)
        self.error_table_view_widget.doubleClicked.connect(self.showErrorFile)

        # self.error_model.setTable('error')  # 设置数据模型的数据表
        # self.error_model.setEditStrategy(False)  # 允许字段更改
        # self.error_model.select()  # 查询所有数据
        # # 设置表格头
        # self.error_model.setHeaderData(0, QtCore.Qt.Horizontal, 'ID')
        # self.error_model.setHeaderData(1, QtCore.Qt.Horizontal, 'Model')
        # self.error_model.setHeaderData(2, QtCore.Qt.Horizontal, 'dataset')
        # self.error_model.setHeaderData(3, QtCore.Qt.Horizontal, 'Error file')
        self.error_table_view_widget.setColumnWidth(3, 1035)
        # self.initRefreshError()
        for i in range(4):
            self.error_table_view_widget.setItemDelegateForColumn(i, EmptyDelegate(self))
        error_table_grid.addWidget(self.error_table_view_widget)
        error_layout.addRow(error_table_grid)

        self.error_tab.setLayout(error_layout)

    def initMergeUI(self):
        merge_layout = QFormLayout()
        merge_hbox_gt = QHBoxLayout()
        merge_hbox_font = QtGui.QFont()
        merge_hbox_font.setBold(True)
        merge_hbox_font.setPixelSize(25)
        merge_database_gt_label = QLabel("Database Manager")
        merge_hbox_gt.addWidget(merge_database_gt_label, 1, Qt.AlignCenter)
        merge_database_gt_label.setFont(merge_hbox_font)
        merge_layout.addRow(merge_hbox_gt)
        merge_layout.addRow(QLabel(''))

        merge_label_hbox_gt = QHBoxLayout()
        merge_label_hbox_font = QtGui.QFont()
        merge_label_hbox_font.setBold(True)
        merge_label_hbox_font.setPixelSize(15)
        merge_gt_label = QLabel("Merge Database")
        merge_label_hbox_gt.addWidget(merge_gt_label, 1, Qt.AlignCenter)
        merge_gt_label.setFont(merge_label_hbox_font)
        merge_layout.addRow(merge_label_hbox_gt)
        merge_layout.addRow(QLabel(''))

        merge_main_database_hbox = QHBoxLayout()
        merge_main_database_hbox.addWidget(QLabel("Main database name:       "))
        self.main_database_dir = QLineEdit()
        self.main_database_dir.setReadOnly(True)
        merge_main_database_hbox.addWidget(self.main_database_dir)
        self.load_model_dir = QPushButton("...")
        merge_main_database_hbox.addWidget(self.load_model_dir)
        self.load_model_dir.clicked.connect(self.btnMainDatabaseClicked)
        merge_layout.addRow(merge_main_database_hbox)

        merge_ano_database_hbox = QHBoxLayout()
        merge_ano_database_hbox.addWidget(QLabel("Another database name:     "))
        self.ano_database_dir = QLineEdit()
        self.ano_database_dir.setReadOnly(True)
        merge_ano_database_hbox.addWidget(self.ano_database_dir)
        self.load_images_dir = QPushButton("...")
        merge_ano_database_hbox.addWidget(self.load_images_dir)
        self.load_images_dir.clicked.connect(self.btnAnoDatabaseClicked)
        merge_layout.addRow(merge_ano_database_hbox)

        merge_opt_hbox = QHBoxLayout()
        self.merge_button = QPushButton("Merge")
        self.merge_button.clicked.connect(self.mergeDatabase)
        merge_opt_hbox.addWidget(self.merge_button)
        merge_layout.addRow(merge_opt_hbox)

        self.merge_tab.setLayout(merge_layout)

    def popSubSelect(self):
        diary_window = Sub_window()
        diary_window.exec_()
        self.refreshByThresh()
        self.refreshError()

    def popErrorSelect(self):
        diary_window = Sub_window()
        diary_window.exec_()
        self.refreshError()
        self.refreshByThresh()

    @staticmethod
    def popModelSelect(self):
        diary_window = ModelDialog()
        diary_window.exec_()
        print('')

    @staticmethod
    def popDatasetSelect(self):
        diary_window = DatasetDialog()
        diary_window.exec_()
        print('')

    @staticmethod
    def popClassesSelect(self):
        diary_window = ClassesDialog()
        diary_window.exec_()
        print('')

    def searchSelection(self):
        global model_selecion, dataset_selection
        temp_models = model_selecion
        temp_dataset = dataset_selection

        self.model.clear()
        self.model.setHorizontalHeaderLabels(['ID', 'Model', 'dataset', 'class', 'TP', 'FP'
                                                 , 'FN', 'F1', 'Ap', 'Map', 'Precision', 'Recall', 'Threshold'])
        self.table_widget.setColumnWidth(1, 160)
        self.table_widget.setColumnWidth(2, 150)
        self.table_widget.setColumnWidth(3, 150)
        self.model.itemChanged.disconnect(self.setQStandardModelItemChanged)
        try:
            self.model.itemChanged.disconnect(self.setQStandardModelItemChanged)
        except:
            pass

        id_max1, class_name1, datasets = self.DBManager.searchId()

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
            tmp_index = 0
            for m in range(class_num):
                row = row_ + tmp_index
                a = list[m]
                if len(a) == 0:
                    continue
                for n in range(TABLE_VALUE_NUMS):
                    # item=QtGui.QStandardItem()
                    if n > 5:
                        self.model.setItem(row, n, QtGui.QStandardItem(str(round(a[id_max[m]][n],3))))
                    else:
                        self.model.setItem(row, n, QtGui.QStandardItem(str(a[id_max[m]][n])))
                tmp_index += 1
        row_last = self.model.rowCount()
        self.model.setItem(row_last, 0, QtGui.QStandardItem(str('')))
        self.model.itemChanged.connect(self.setQStandardModelItemChanged)
        self.model.setHorizontalHeaderLabels(['ID', 'Model', 'dataset', 'class', 'TP', 'FP'
                                                 , 'FN', 'F1', 'Ap', 'Map', 'Precision', 'Recall', 'Threshold'])
        self.filter_thresh = 0

    def doubleClicked(self, index):
        self.table_widget.openPersistentEditor(index)

    def selectClicked(self, Item=None):
        r = Item.row()  # 获取行号D
        c = Item.column()  # 获取列号D
        row_last = self.model.rowCount()
        col_last = self.model.columnCount()
        try:
            self.model.itemChanged.disconnect(self.setQStandardModelItemChanged)
        except:
            pass
        for i in range(row_last-1):
            for j in range(col_last):
                try:
                    self.model.item(i, j).setBackground(QtGui.QBrush(WHITE_COLOR))
                except:
                    print(1)
        for i in range(row_last-1):
            try:
                self.model.item(i, c).setBackground(QtGui.QBrush(GRAY_COLOR))
            except:
                print(1)
        for j in range(col_last):
            try:
                self.model.item(r, j).setBackground(QtGui.QBrush(GRAY_COLOR))
            except:
                print(1)
        self.model.itemChanged.connect(self.setQStandardModelItemChanged)


    def onUpdateText(self, text):
        """Write console output to text widget."""
        cursor = self.process.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.process.setTextCursor(cursor)
        self.process.ensureCursorVisible()

    def centerScreen(self):
        size = self.size()
        desktopSize = QtWidgets.QDesktopWidget().screenGeometry()
        top = (desktopSize.height() / 2) - (size.height() / 2)
        left = (desktopSize.width() / 2) - (size.width() / 2)
        self.move(left, top)

    def closeEvent(self, event):
        conf = self.showPopUp('Are you sure you want to close the program?',
                               'Closing',
                               buttons=QMessageBox.Yes | QMessageBox.No,
                               icon=QMessageBox.Question)
        if conf == QMessageBox.Yes:
            event.accept()
            sys.exit(0)
        else:
            event.ignore()

    def showPopUp(self,
                   message,
                   title,
                   buttons=QMessageBox.Ok | QMessageBox.Cancel,
                   icon=QMessageBox.Information):
        self.msgBox.setIcon(icon)
        self.msgBox.setText(message)
        self.msgBox.setWindowTitle(title)
        self.msgBox.setStandardButtons(buttons)
        return self.msgBox.exec()

    def comboSelectionChangedModels(self, index):
        text = self.combobox_process.itemText(index)
        if text == 'yolov3':
            self.process_method = 'yolov3'
        elif text == 'yolov3_padding':
            self.process_method = 'yolov3_padding'
        elif text == 'yolov5':
            self.process_method = 'yolov5'
        elif text == 'yolov5x':
            self.process_method = 'yolov5x'
        elif text == 'yolov3_tiny3_padding':
            self.process_method = 'yolov3_tiny3_padding'
        elif text == 'yolov3_tiny3':
            self.process_method = 'yolov3_tiny3'
        elif text == 'yolov3_mmdetection':
            self.process_method = 'yolov3_mmdetection'

    def comboSelectionChangedClasses(self, index):
        text = self.combobox_classes.itemText(index)
        if text == '':
            print(1)
        else:
            self.class_name_draw = text
            self.btnDraw()

    def loadAnnotationsGround(self):

        if self.rad_gt_format_coco_json.isChecked():
            self.ret = 'coco'
        elif self.rad_gt_format_pascalvoc_xml.isChecked():
            self.ret = 'voc'
        elif self.rad_gt_format_yolo_text.isChecked():
            self.ret = 'darknet'
        if self.ret == '':
            print("no format select")
            exit(-1)

    def btnGtStatisticsClicked(self):
        pass

    def btnGtDirClicked(self):
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

    def btnSaveDirClicked(self):
        if self.error_path.text() == '':
            txt = self.current_directory
        else:
            txt = self.error_path.text()
        directory = QFileDialog.getExistingDirectory(
            self, 'Choose directory to save', txt)
        if directory == '':
            return
        if os.path.isdir(directory):
            self.error_path.setText(directory)
        else:
            self.error_path.setText('')

    def btnGtClassesClicked(self):
        filepath = QFileDialog.getOpenFileName(self, 'Choose a file with a list of classes',
                                               self.current_directory,
                                               "Image files (*.txt *.names)")
        filepath = filepath[0]
        if os.path.isfile(filepath):
            self.txb_classes_gt.setText(filepath)
            self.filepath_classes_gt = filepath
        else:
            self.filepath_classes_gt = None

    def btnGtImagesDirClicked(self):
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

    def btnDetClassesClicked(self):
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

    def btnDetDirClicked(self):
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

    def btnOutputDirClicked(self):
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

    def btnSaveClicked(self):
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

                DB.addItem(model_name, dataset_name, name_cl, tp_cl, fp_cl, fn_cl, F1_cl, ap_cl, map_cl, prec_cl,
                            rec_cl, thre_cl)
                DB.addItem_(model_name, dataset_name, name_cl, tp_cl, fp_cl, fn_cl, F1_cl, ap_cl, map_cl, prec_cl,
                             rec_cl, thre_cl)

            # save all classes metric
            result_metric = result_csv[2].split(",")

            map = float(result_metric[0])
            Precision, recall, F1_ = self.getMetric(TP_all, FP_all, FN_all)
            print(model_name, dataset_name, "all", TP_all, FP_all, FN_all, F1_, 0, map, Precision, recall, thre_cl)
            DB.addItem(model_name, dataset_name, "all", TP_all, FP_all, FN_all, F1_, 0, map, Precision, recall,
                        thre_cl)
            DB.addItem_(model_name, dataset_name, "all", TP_all, FP_all, FN_all, F1_, 0, map, Precision, recall,
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
                        index = self.getIndexNumber(a, float(t))
                        if value[index] not in value_save:
                            value_save.append(value[index])

                    a_s = np.array(value_save)[:, 11]
                    a_s = a_s.tolist()

                    index_max = int(float(b[m]))
                    print("value_max")
                    print(value[index_max])

                    index1 = self.getIndexNumber(a_s, float(value[index_max][11]))

                    if value[index_max] not in value_save:
                        if float(value[index_max][11]) > float(a_s[index1]):
                            value_save.insert(index1, value[index_max])
                            id_max[m][3] = index1 + 1
                        else:
                            value_save.insert(index1+1, value[index_max])
                            id_max[m][3] = index1 + 2

                    else:
                        id_max[m][3] = index1 + 1

                    DB.addItemId(str(id_max[m][0]), str(id_max[m][1]), str(id_max[m][2]), int(id_max[m][3]))
                    for i in tqdm(range(len(value_save))):
                        DB.addItem_(str(value_save[i][0]), str(value_save[i][1]), str(value_save[i][2]),
                                     int(value_save[i][3]),
                                     int(value_save[i][4]), int(value_save[i][5]), float(value_save[i][6]),
                                     float(value_save[i][7]),
                                     float(value_save[i][8]),
                                     float(value_save[i][9]), float(value_save[i][10]), float(value_save[i][11]))
                else:
                    DB.addItemId(str(id_max[m][0]), str(id_max[m][1]), str(id_max[m][2]), int(id_max[m][3]))

            print("saving error files ...")
            nums_list = np.arange(0, len(self.result['error'])).tolist()
            nums = nums_list

            for j in tqdm(nums):
                DB.addErrorFile(model_name, dataset_name, self.result['error'][j])

    def getMetric(self, tp, fp, fn):
        if tp + fp == 0 or tp + fn == 0:
            return 0, 0, 0

        prec = tp / (tp + fp)
        rec = tp / (tp + fn)
        f1 = 2 / (1 / prec + 1 / rec)
        return prec, rec, f1

    def btnRunClicked(self):
        self.btnRunReal()

    def btnRunReal(self):
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

        id_max1, class_name1, datasets = self.DBManager.searchId()

        for key, value in id_max1.items():
            if model_name + "$" + dataset_name == key:
                print("model and dataset repeat！")
                exit(-1)

        evaluation = onnx.ONNX(self.dir_model_gt, 64, self.dir_images_gt, self.filepath_classes_gt, self.ret,
                               self.process_method)
        self.result_csv, self.result = evaluation.evaluate()
        # threading.Thread._Thread__stop(self.thead1)
        self.btnSaveClicked()
        print("保存成功")

    def btnDrawByModel(self, model, datasets):
        self.draw_grid.setVisible(True)

        plt = self.DBManager.drawByModel(model, datasets, self.class_name_draw)
        self.gridlayout.addWidget(plt, 0, 2)

    def btnDrawByData(self, model, data):
        self.draw_grid.setVisible(True)

        plt = self.DBManager.drawByData(model, data, self.class_name_draw)
        self.gridlayout.addWidget(plt, 0, 2)

    def drawByModels(self, models, dataset):
        if len(models) == 0:
            return
        self.draw_grid.setVisible(True)

        map, ap, recall, Precision, F1_, index, TP, FP, FN, Thre = [], [], [], [], [], [], [], [], [], []
        for key, value in self.thr_id_max.items():
            data_name = key.split('$')[-1]
            model_n = key.split('$' + data_name)[0]
            if not model_n in models:
                continue
            if not data_name == dataset:
                continue
            if self.class_name_draw == None:
                self.class_name_draw = 'person'
            if self.class_name_draw not in self.class_dict or (self.class_dict[self.class_name_draw] + 1) > len(value):
                print("there is no ", self.class_name_draw)
                return
            id_max = value[self.class_dict[self.class_name_draw]]
            tmp_data = []
            tmp_thresh = []
            for i in range(len(self.value)):
                if str(self.value[i][1]) == model_n and str(self.value[i][2]) == data_name and str(self.value[i][3]) == self.class_name_draw:
                    tmp_data.append(self.value[i])
                    tmp_thresh.append(self.value[i][12])
            if len(tmp_data) == 0:
                continue
            index_thresh = self.getIndexNumber(tmp_thresh, float(0.8))
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
            fig_show.axes0.text(a, b - map[i]/10, "%.2f" % map[i], ha='center', fontsize=10)  # plt.text 函数
        for a, b, i in zip(index, recall, range(len(index))):  # zip 函数
            fig_show.axes1.text(a, b - recall[i]/10, "%.2f" % recall[i], ha='center', fontsize=10)  # plt.text 函数
        for a, b, i in zip(index, Precision, range(len(index))):  # zip 函数
            fig_show.axes2.text(a, b - Precision[i]/10, "%.2f" % Precision[i], ha='center', fontsize=10)  # plt.text 函数
        for a, b, i in zip(index, F1_, range(len(index))):  # zip 函数
            fig_show.axes3.text(a, b - F1_[i]/10, "%.2f" % F1_[i], ha='center', fontsize=10)  # plt.text 函数
        for a, b, i in zip(index, TP, range(len(index))):  # zip 函数
            fig_show.axes4.text(a, b - TP[i]/10, "%.2f" % TP[i], ha='center', fontsize=10)  # plt.text 函数
        for a, b, i in zip(index, FP, range(len(index))):  # zip 函数
            fig_show.axes5.text(a, b - FP[i]/10, "%.2f" % FP[i], ha='center', fontsize=10)  # plt.text 函数
        for a, b, i in zip(index, FN, range(len(index))):  # zip 函数
            fig_show.axes6.text(a, b - FN[i]/10, "%.2f" % FN[i], ha='center', fontsize=10)  # plt.text 函数
        for a, b, i in zip(index, ap, range(len(index))):  # zip 函数
            fig_show.axes7.text(a, b - ap[i]/10, "%.2f" % ap[i], ha='center', fontsize=10)  # plt.text 函数
        for a, b, i in zip(index, Thre, range(len(index))):  # zip 函数
            fig_show.axes8.text(a, b - Thre[i]/10, "%.2f" % Thre[i], ha='center', fontsize=10)  # plt.text 函数

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

    def drawByDatasets(self, model, datasets):
        if len(datasets) == 0:
            return
        self.draw_grid.setVisible(True)
        map, ap, recall, Precision, F1_, index, TP, FP, FN, Thre = [], [], [], [], [], [], [], [], [], []
        for key, value in self.thr_id_max.items():
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
            fig_show.axes0.text(a, b - map[i]/10, "%.2f" % map[i], ha='center', fontsize=10)  # plt.text 函数
        for a, b, i in zip(index, recall, range(len(index))):  # zip 函数
            fig_show.axes1.text(a, b - recall[i]/10, "%.2f" % recall[i], ha='center', fontsize=10)  # plt.text 函数
        for a, b, i in zip(index, Precision, range(len(index))):  # zip 函数
            fig_show.axes2.text(a, b - Precision[i]/10, "%.2f" % Precision[i], ha='center', fontsize=10)  # plt.text 函数
        for a, b, i in zip(index, F1_, range(len(index))):  # zip 函数
            fig_show.axes3.text(a, b - F1_[i]/10, "%.2f" % F1_[i], ha='center', fontsize=10)  # plt.text 函数
        for a, b, i in zip(index, TP, range(len(index))):  # zip 函数
            fig_show.axes4.text(a, b - TP[i]/10, "%.2f" % TP[i], ha='center', fontsize=10)  # plt.text 函数
        for a, b, i in zip(index, FP, range(len(index))):  # zip 函数
            fig_show.axes5.text(a, b - FP[i]/10, "%.2f" % FP[i], ha='center', fontsize=10)  # plt.text 函数
        for a, b, i in zip(index, FN, range(len(index))):  # zip 函数
            fig_show.axes6.text(a, b - FN[i]/10, "%.2f" % FN[i], ha='center', fontsize=10)  # plt.text 函数
        for a, b, i in zip(index, ap, range(len(index))):  # zip 函数
            fig_show.axes7.text(a, b - ap[i]/10, "%.2f" % ap[i], ha='center', fontsize=10)  # plt.text 函数
        for a, b, i in zip(index, Thre, range(len(index))):  # zip 函数
            fig_show.axes8.text(a, b - Thre[i]/10, "%.2f" % Thre[i], ha='center', fontsize=10)  # plt.text 函数

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

    def btnDrawClickedByThresh(self):
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
            self.drawByModels(model, data[0])
        elif len(model) == 1:
            self.drawByDatasets(model[0], data)
        else:
            print("ui2 erroe")

    def btnDraw(self):
        if self.filter_thresh == 0:
            self.btnDrawClicked()
        else:
            self.btnDrawClickedByThresh()

    def btnDrawClicked(self):
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
            self.btnDrawByModel(model, data[0])
        elif len(model) == 1:
            self.btnDrawByData(model[0], data)
        else:
            print("ui2 erroe")

    def btnSearchByModel(self):
        text = self.model_line_ui3.text()
        self.model.clear()
        self.model.itemChanged.disconnect(self.setQStandardModelItemChanged)
        try:
            self.model.itemChanged.disconnect(self.setQStandardModelItemChanged)
        except:
            pass

        id_max1, class_name1, datasets = self.DBManager.searchId()

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
                for n in range(TABLE_VALUE_NUMS):
                    # item=QtGui.QStandardItem()
                    a = list[m]
                    if n > 5:
                        self.model.setItem(row, n, QtGui.QStandardItem(str(round(a[id_max[m]][n],3))))
                    else:
                        self.model.setItem(row, n, QtGui.QStandardItem(str(a[id_max[m]][n])))
        row_last = self.model.rowCount()
        self.model.setItem(row_last, 0, QtGui.QStandardItem(str('')))
        self.model.itemChanged.connect(self.setQStandardModelItemChanged)
        self.model.setHorizontalHeaderLabels(['ID', 'Model', 'dataset', 'class', 'TP', 'FP'
                                                 , 'FN', 'F1', 'Ap', 'Map', 'Precision', 'Recall', 'Threshold'])
        self.table_widget.setColumnWidth(1, 160)
        self.table_widget.setColumnWidth(2, 150)
        self.table_widget.setColumnWidth(3, 150)

    def btnSearchByData(self):
        text = self.data_line_ui3.text()
        self.model.clear()
        self.model.itemChanged.disconnect(self.setQStandardModelItemChanged)
        try:
            self.model.itemChanged.disconnect(self.setQStandardModelItemChanged)
        except:
            pass

        id_max1, class_name1, datasets = self.DBManager.searchId()

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
                for n in range(TABLE_VALUE_NUMS):
                    # item=QtGui.QStandardItem()
                    a = list[m]
                    if n > 5:
                        self.model.setItem(row, n, QtGui.QStandardItem(str(round(a[id_max[m]][n],3))))
                    else:
                        self.model.setItem(row, n, QtGui.QStandardItem(str(a[id_max[m]][n])))
        row_last = self.model.rowCount()
        self.model.setItem(row_last, 0, QtGui.QStandardItem(str('')))
        self.model.itemChanged.connect(self.setQStandardModelItemChanged)
        self.model.setHorizontalHeaderLabels(['ID', 'Model', 'dataset', 'class', 'TP', 'FP'
                                                 , 'FN', 'F1', 'Ap', 'Map', 'Precision', 'Recall', 'Threshold'])
        self.table_widget.setColumnWidth(1, 160)
        self.table_widget.setColumnWidth(2, 150)
        self.table_widget.setColumnWidth(3, 150)

    def btnSearchByFilter(self):
        text = self.filter_line_ui3.text()
        text_model = text.split('_')[0]
        text_datasets = text.split('_')[1]
        self.model.clear()
        self.model.itemChanged.disconnect(self.setQStandardModelItemChanged)
        try:
            self.model.itemChanged.disconnect(self.setQStandardModelItemChanged)
        except:
            pass

        id_max1, class_name1, datasets = self.DBManager.searchId()

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
                    for n in range(TABLE_VALUE_NUMS):
                        # item=QtGui.QStandardItem()
                        a = list[m]
                        if n > 5:
                            self.model.setItem(row, n, QtGui.QStandardItem(str(round(a[id_max[m]][n],3))))
                        else:
                            self.model.setItem(row, n, QtGui.QStandardItem(str(a[id_max[m]][n])))

        self.model.itemChanged.connect(self.setQStandardModelItemChanged)

    def btnSearchByFilterOption(self):
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
        self.table_widget.setColumnWidth(1, 160)
        self.table_widget.setColumnWidth(2, 150)
        self.table_widget.setColumnWidth(3, 150)
        self.model.itemChanged.disconnect(self.setQStandardModelItemChanged)
        try:
            self.model.itemChanged.disconnect(self.setQStandardModelItemChanged)
        except:
            pass

        id_max1, class_name1, datasets = self.DBManager.searchId()

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
                for n in range(TABLE_VALUE_NUMS):
                    # item=QtGui.QStandardItem()
                    a = list[class_name.index(cls_name)]
                    if n > 5:
                        self.model.setItem(row, n,
                                           QtGui.QStandardItem(str(round(a[id_max[class_name.index(cls_name)]][n],3))))
                    else:

                        self.model.setItem(row, n, QtGui.QStandardItem(str(a[id_max[class_name.index(cls_name)]][n])))
            else:
                pass
        row_last = self.model.rowCount()
        self.model.setItem(row_last, 0, QtGui.QStandardItem(str('')))
        self.model.itemChanged.connect(self.setQStandardModelItemChanged)

    def btnRefresh(self):
        self.model.clear()
        self.model.setHorizontalHeaderLabels(['ID', 'Model', 'dataset', 'class', 'TP', 'FP'
                                                 , 'FN', 'F1', 'Ap', 'Map', 'Precision', 'Recall', 'Threshold'])

        self.table_widget.setColumnWidth(1, 160)
        self.table_widget.setColumnWidth(2, 150)
        self.table_widget.setColumnWidth(3, 150)
        self.table_widget.setColumnWidth(0, 0)
        self.model.itemChanged.disconnect(self.setQStandardModelItemChanged)

        id_max1, class_name1, datasets = self.DBManager.searchId()

        showID = 0
        for key, value in id_max1.items():
            if showID<len(id_max1)-50:
                showID+=1
                continue
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
                for n in range(TABLE_VALUE_NUMS):
                    if n > 5:
                        self.model.setItem(row, n, QtGui.QStandardItem(str(round(list[m][id_max[m]][n],3))))
                    else:
                        self.model.setItem(row, n, QtGui.QStandardItem(str(list[m][id_max[m]][n])))
        row_last = self.model.rowCount()
        self.model.setItem(row_last, 0, QtGui.QStandardItem(str('')))
        self.model.itemChanged.connect(self.setQStandardModelItemChanged)

    def refreshByThresh(self):
        global model_selecion, dataset_selection
        temp_models = model_selecion
        temp_dataset = dataset_selection
        if len(temp_models) == 0 or len(temp_dataset) == 0:
            self.showPopUp('please select models and datasets', 'warning')
            return
        self.model.clear()
        self.model.setHorizontalHeaderLabels(['ID', 'Model', 'dataset', 'class', 'TP', 'FP'
                                                 , 'FN', 'F1', 'Ap', 'Map', 'Precision', 'Recall', 'Threshold'])
        self.table_widget.setColumnWidth(1, 160)
        self.table_widget.setColumnWidth(2, 150)
        self.table_widget.setColumnWidth(3, 150)
        self.model.itemChanged.disconnect(self.setQStandardModelItemChanged)
        try:
            self.model.itemChanged.disconnect(self.setQStandardModelItemChanged)
        except:
            pass

        id_max1, class_name1, datasets = self.DBManager.searchId()

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

            # index_thresh = self.getIndexNumber(thresh_hold, float(0.8))

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
            tmp_index = 0
            for m in range(class_num):
                row = row_ + tmp_index
                temp_thresh_list = thresh_hold[m]
                if len(temp_thresh_list) > 0:
                    index_thresh = self.getIndexNumber(temp_thresh_list, float(0.8))
                else:
                    index_thresh = 0
                a = list[m]
                if len(a) == 0:
                    continue
                for n in range(TABLE_VALUE_NUMS):
                    # item=QtGui.QStandardItem()
                    if n > 5:
                        self.model.setItem(row, n, QtGui.QStandardItem(str(round(a[index_thresh][n],3))))
                    else:
                        self.model.setItem(row, n, QtGui.QStandardItem(str(a[index_thresh][n])))
                tmp_index += 1
        row_last = self.model.rowCount()
        self.model.setItem(row_last, 0, QtGui.QStandardItem(str('')))

        self.model.itemChanged.connect(self.setQStandardModelItemChanged)
        self.model.setHorizontalHeaderLabels(['ID', 'Model', 'dataset', 'class', 'TP', 'FP'
                                                 , 'FN', 'F1', 'Ap', 'Map', 'Precision', 'Recall', 'Threshold'])
        self.filter_thresh = 1
        # self.btnLoadSelection()
        self.btnLoadSelection()

    def getIndexNumber(self, li, defaultnumber):
        select = Decimal(str(defaultnumber)) - Decimal(str(li[0]))
        index = 0
        for i in range(1, len(li) - 1):
            select2 = Decimal(str(defaultnumber)) - Decimal(str(li[i]))
            if (abs(select) > abs(select2)):
                select = select2
                index = i
        return index

    def setQStandardModelItemChanged(self, item):

        self.model.itemChanged.disconnect(self.setQStandardModelItemChanged)

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
        index = self.getIndexNumber(a, float(thre))

        for j in range(TABLE_VALUE_NUMS):
            if j > 5:
                self.model.setItem(r, j, QtGui.QStandardItem(str(round(b[index][j],3))))
            else:
                self.model.setItem(r, j, QtGui.QStandardItem(str(b[index][j])))

        self.model.itemChanged.connect(self.setQStandardModelItemChanged)

    def btnSearchByModelError(self):
        text = self.model_line_ui4.text()
        text = "\"" + text + "\""
        print('model_name=' + str(text))
        self.error_model.setFilter('model_name=' + str(text))

    def btnSearchByDataError(self):
        text = self.data_line_ui4.text()
        text = "\"" + text + "\""
        print('dataset_name=' + str(text))
        self.error_model.setFilter('dataset_name=' + str(text))

    def btnSearchByFilterError(self):
        text = self.filter_line_ui4.text()
        self.error_model.setFilter(str(text))

    def btnRefreshError(self):
        self.error_model.setFilter('')

    def showErrorFile(self, index):
        row = index.row()
        text = self.error_model.data(self.error_model.index(row, 3))
        # text=self.result['error'][qModelIndex.row()]
        image_path = text.split('---')[0]
        img = cv2.imread(image_path)
        cv2.imshow("Image", img)

    def btnLoadSelection(self):

        for dataset_check_name in self.checkdatasets:
            self.group_box_dataset_layout.removeWidget(dataset_check_name)
            dataset_check_name.setParent(None)
        for model_check_name in self.checkmodels:
            self.group_box_model_layout.removeWidget(model_check_name)
            model_check_name.setParent(None)

        global dataset_selection, model_selecion
        self.models = []
        self.datasets = []

        self.checkdatasets = []
        self.checkmodels = []
        tmp_dataset = dataset_selection.copy()
        tmp_model = model_selecion.copy()

        if not len(tmp_model) == 0:
            self.checkmodels.extend(tmp_model)
            self.models.extend(tmp_model)
            for i in range(len(self.models)):
                self.checkmodels[i] = QCheckBox(str(self.models[i]))
                self.checkmodels[i].stateChanged.connect(self.btnDraw)
                self.group_box_model_layout.addWidget(self.checkmodels[i])

        if not len(tmp_dataset) == 0:
            self.datasets.extend(tmp_dataset)
            self.checkdatasets.extend(self.datasets)
            for i in range(len(self.datasets)):
                self.checkdatasets[i] = QCheckBox(str(self.datasets[i]))
                self.checkdatasets[i].stateChanged.connect(self.btnDraw)
                self.group_box_dataset_layout.addWidget(self.checkdatasets[i])

        for i in range(len(self.models)):
            self.checkmodels[i].setChecked(True)
        for i in range(len(self.checkdatasets)):
            if i == len(self.checkdatasets) - 1:
                self.checkdatasets[i].setChecked(True)
            else:
                self.checkdatasets[i].setChecked(False)

        self.btnShowClassesClicked()
    def btnLoadDiffThresh(self):
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
                self.checkmodels[i].stateChanged.connect(self.btnDraw)
                self.group_box_model_layout.addWidget(self.checkmodels[i])

        if not len(tmp_dataset) == 0:
            self.checkdatasets.extend(tmp_dataset)
            self.datasets.extend(tmp_dataset)
            for i in range(len(tmp_dataset)):
                self.checkdatasets[i] = QCheckBox(str(tmp_dataset[i]))
                self.checkdatasets[i].stateChanged.connect(self.btnDraw)
                self.group_box_dataset_layout.addWidget(self.checkdatasets[i])

        for i in range(len(tmp_model)):
            self.checkmodels[i].setChecked(True)
        # self.checkdatasets[0].setChecked(True)

        self.btnShowClassesClicked()

    def btnLoadMd(self):

        models, datasets = self.DBManager.searchModelDatasets()
        self.models, self.datasets = models, datasets

        self.checkmodels = models.copy()
        self.checkdatasets = datasets.copy()
        for i in range(len(models)):
            self.checkmodels[i] = QCheckBox(str(models[i]))
            self.checkmodels[i].stateChanged.connect(self.btnDrawClicked)
            self.group_box_model_layout.addWidget(self.checkmodels[i])
        for i in range(len(datasets)):
            self.checkdatasets[i] = QCheckBox(str(datasets[i]))
            self.checkdatasets[i].stateChanged.connect(self.btnDrawClicked)
            self.group_box_dataset_layout.addWidget(self.checkdatasets[i])

    def btnShowClassesClicked(self):
        name = None
        for i in range(len(self.checkdatasets)):
            if self.checkdatasets[i].isChecked():
                name = self.datasets[i]
        class_names = self.DBManager.searchClasses(name)
        self.combobox_classes.clear()
        self.combobox_classes.addItems(class_names)

    def btnMainDatabaseClicked(self):
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

    def btnAnoDatabaseClicked(self):
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

    def mergeDatabase(self):
        DBManagerChanged().merge(self.main_database_dir_, self.ano_database_dir_)

    def searchError(self):
        global model_selecion, dataset_selection, class_selection
        tmp_error_list = []
        tmp_model_selection = model_selecion
        tmp_dataset_selection = dataset_selection
        tmp_class_selection = class_selection
        if len(tmp_model_selection) == 0:
            self.showPopUp('please select models!', 'warning')
            return
        if len(tmp_dataset_selection) == 0:
            self.showPopUp('please select datasets!', 'warning')
            return
        if len(tmp_class_selection) == 0:
            self.showPopUp('please select classes!', 'warning')
            return
        error_id, error_dic = self.DBManager.searchError()
        for key, value in error_dic.items():
            tmp_model_name, tmp_data_name = key.split('$')
            if not tmp_model_name in tmp_model_selection:
                continue
            if not tmp_data_name in tmp_dataset_selection:
                continue
            for index_value in value:
                if '---' not in index_value:
                    continue
                match_class = index_value.split('---')[1].split('+')[0]
                if match_class in tmp_class_selection:
                    tmp_error_list.append(index_value)
        global error_file_list
        error_file_list = tmp_error_list

    def exportError(self):
        self.btnSaveDirClicked()
        self.export_selection.setEnabled(False)
        tmp_save_path = self.error_path.text()
        if len(tmp_save_path) > 0 and os.path.exists(tmp_save_path):
            cache_path = tmp_save_path
        else:
            self.showPopUp('please input error file save path', 'warning')
            self.export_selection.setEnabled(True)
            return
        self.searchError()
        global error_file_list
        cache_file_list = error_file_list
        error_file = open(os.path.join(cache_path, 'error_files.list'), 'w')
        for index_file in cache_file_list:
            error_file.write(index_file + '\n')
        error_file.close()
        self.export_selection.setEnabled(True)

    def initRefreshError(self):
        self.error_model.clear()
        self.error_model.setHorizontalHeaderLabels(['ID', 'Model', 'dataset', 'error file'])
        error_id, error_dic = self.DBManager.searchError()
        row_ = self.error_model.rowCount()


        init_show_nums = 0
        for key, values in error_dic.items():
            tmp_model_name, tmp_data_name = key.split('$')
            tmp_ids = error_id[key]
            tmp_model_dataset = [tmp_model_name, tmp_data_name]
            tmp_values = values
            if init_show_nums > 100:
                break
            for index, index_value in enumerate(tmp_values):
                tmp_id = tmp_ids[index]
                self.error_model.setItem(row_, 0, QtGui.QStandardItem(str(tmp_id)))
                init_show_nums += 1
                for n in range(1, 4):
                    if 0 < n < 3:
                        self.error_model.setItem(row_, n, QtGui.QStandardItem(str(tmp_model_dataset[n - 1])))
                    else:
                        self.error_model.setItem(row_, n, QtGui.QStandardItem(str(index_value)))
                row_ += 1


    def refreshError(self):
        global model_selecion, dataset_selection, class_selection
        tmp_model_selection = model_selecion
        tmp_dataset_selection = dataset_selection
        tmp_class_selection = class_selection

        if len(tmp_model_selection) == 0:
            self.showPopUp('please select models!', 'warning')
            return
        if len(tmp_dataset_selection) == 0:
            self.showPopUp('please select datasets!', 'warning')
            return
        if len(tmp_class_selection) == 0:
            self.showPopUp('please select classes!', 'warning')
            return

        self.error_model.clear()
        self.error_model.setHorizontalHeaderLabels(['ID', 'Model', 'dataset', 'error file'])
        error_id, error_dic = self.DBManager.searchError()
        row_ = self.error_model.rowCount()

        for key, values in error_dic.items():
            tmp_model_name, tmp_data_name = key.split('$')
            if not tmp_model_name in tmp_model_selection:
                continue
            if not tmp_data_name in tmp_dataset_selection:
                continue
            tmp_ids = error_id[key]
            tmp_model_dataset = [tmp_model_name, tmp_data_name]
            tmp_values = values
            for index, index_value in enumerate(tmp_values):
                if '---' not in index_value:
                    continue
                match_class = index_value.split('---')[1].split('+')[0]
                if not match_class in tmp_class_selection:
                    continue
                tmp_id = tmp_ids[index]
                row_ += 1
                self.error_model.setItem(row_, 0, QtGui.QStandardItem(str(tmp_id)))
                for n in range(1, 4):
                    if 0 < n < 3:
                        self.error_model.setItem(row_, n, QtGui.QStandardItem(str(tmp_model_dataset[n - 1])))
                    else:
                        self.error_model.setItem(row_, n, QtGui.QStandardItem(str(index_value)))
        row_last = self.error_model.rowCount()
        self.error_model.setItem(row_last, 0, QtGui.QStandardItem(str('')))

