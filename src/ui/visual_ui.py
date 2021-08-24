# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main_ui.ui'
#
# Created by: PyQt5 UI code generator 5.12.3
#
# WARNING! All changes made in this file will be lost!
import os
import sys


from PyQt5 import QtGui,QtCore,QtWidgets,QtSql
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtWidgets import *

import os
import sys

import onnx
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QMainWindow, QMessageBox, QTabWidget
from PyQt5 import QtCore, QtGui
import matplotlib

matplotlib.use("Qt5Agg")
from src.database.db import DBManager

class Stream(QtCore.QObject):
    """Redirects console output to text widget."""
    newText = QtCore.pyqtSignal(str)

    def write(self, text):
        self.newText.emit(str(text))

class Ui_Window(QTabWidget):
    def __init__(self,parent=None):
        super(Ui_Window, self).__init__(parent)
        # super(Ui_Dialog, self).__init__()
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
        self.process_method=''
        self.result_csv=None
        self.class_name_draw=None

        self.center_screen()
        sys.stdout = Stream(newText=self.onUpdateText)

        self.tab1 = QtWidgets.QWidget()
        self.tab2 = QtWidgets.QWidget()
        self.tab3 = QtWidgets.QWidget()
        self.addTab(self.tab1, "Detection Metrics")
        self.addTab(self.tab2, "Visual Comparsion")
        self.addTab(self.tab3, "Show Database")
        self.tab1UI()
        self.tab2UI()
        self.tab3UI()
        self.setWindowTitle("Object Detection Metrics")

    def tab1UI(self):
        layout = QFormLayout()

        gt = QHBoxLayout()
        font = QtGui.QFont()
        font.setBold(True)
        font.setPixelSize(25)
        gt_label=QLabel("Ground truth")
        gt.addWidget(gt_label,1,Qt.AlignCenter)

        gt_label.setFont(font)
        layout.addRow(gt)

        h1 = QHBoxLayout()
        h1.addWidget(QLabel("Model:       "))
        self.txb_gt_dir=QLineEdit()
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
        frame.setMinimumSize(2000,100)
        frame.setStyleSheet("background-color: #feeeed")

        h4_1=QHBoxLayout()
        gt_format = QLabel("Coordinates format:")
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        gt_format.setFont(font)
        h4_1.addWidget(gt_format)
        h4.addLayout(h4_1)

        h4_2=QHBoxLayout()
        self.rad_gt_format_coco_json= QRadioButton("COCO (.json)")
        self.rad_gt_format_pascalvoc_xml= QRadioButton("PASCAL VOC (.xml)")
        self.rad_gt_format_labelme_xml= QRadioButton("Label Me (.xml)")
        self.rad_gt_format_yolo_text= QRadioButton("(*) YOLO (.txt)")
        h4_2.addWidget(self.rad_gt_format_coco_json)
        h4_2.addWidget(self.rad_gt_format_pascalvoc_xml)
        h4_2.addWidget(self.rad_gt_format_labelme_xml)
        h4_2.addWidget(self.rad_gt_format_yolo_text)
        h4.addLayout(h4_2)

        format_w.setLayout(h4)
        layout.addWidget(format_w)
        layout.addRow(QLabel(' '))

        h5=QHBoxLayout()
        h5.addWidget(QLabel("Onnx Model Type:"),1, Qt.AlignLeft )
        self.combobox_process=QComboBox()
        h5.addWidget(self.combobox_process,5, Qt.AlignLeft )
        self.combobox_process.addItems(['','yolov3','yolov5'])
        self.combobox_process.setMinimumSize(200,27)
        self.combobox_process.currentIndexChanged.connect(self.comboSelectionChanged)
        btn_save=QPushButton("save")
        h5.addWidget(btn_save,1, Qt.AlignRight )
        btn_save.setMinimumSize(60,27)
        btn_save.clicked.connect(self.btn_save_clicked)
        layout.addRow(h5)

        self.process=QTextEdit()
        layout.addRow(self.process)

        [layout.addRow(QLabel('')) for i in range(10)]

        h6=QHBoxLayout()
        self.btn_run=QPushButton("RUN")
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
        gt.addWidget(gt_label,1,Qt.AlignCenter)
        gt_label.setFont(font)
        layout.addRow(gt)
        layout.addRow(QLabel(''))

        h1=QHBoxLayout()
        h1.addWidget(QLabel("Datasets name："))
        self.data_line=QLineEdit()
        h1.addWidget( self.data_line)
        self.draw_by_data=QPushButton("Draw by Data")
        h1.addWidget(self.draw_by_data)
        self.draw_by_data.clicked.connect(self.btn_draw_by_data)
        h1.addWidget(QLabel("(*The different models on same dataset)"))
        layout.addRow(h1)

        h2 = QHBoxLayout()
        h2.addWidget(QLabel("    Model name："))
        self.model_line=QLineEdit()
        h2.addWidget(self.model_line)
        self.draw_by_model=QPushButton("Draw by Model")
        h2.addWidget(self.draw_by_model)
        self.draw_by_model.clicked.connect(self.btn_draw_by_model)
        h2.addWidget(QLabel("(*The same model on different datasets)"))
        layout.addRow(h2)

        w = QWidget()
        groupBox = QGroupBox(w)
        self.gridlayout = QGridLayout(groupBox)
        w.setLayout(self.gridlayout)
        layout.addWidget(w)

        h3 = QHBoxLayout()
        h3.addWidget(QLabel("Load classes:"),1,Qt.AlignLeft)
        self.combobox_classes=QComboBox()
        self.combobox_classes.setMinimumSize(200,27)
        self.combobox_classes.currentIndexChanged.connect(self.comboSelectionChanged1)
        h3.addWidget(self.combobox_classes,5,Qt.AlignLeft)
        self.load_class_dir = QPushButton("Load ...")
        self.load_class_dir.setMinimumSize(60,27)
        h3.addWidget(self.load_class_dir,1,Qt.AlignRight)
        self.load_class_dir.clicked.connect(self.btn_show_classes_clicked)
        layout.addRow(h3)

        self.tab2.setLayout(layout)

    def tab3UI(self):
        layout=QGridLayout()
        self.table_widget = QtWidgets.QTableView()
        self.table_widget.setGeometry(0, 0, 1214, 950)
        db_text = os.getcwd() + '/src/database/core'

        self.db_name = db_text
        # 添加一个sqlite数据库连接并打开
        db = QtSql.QSqlDatabase.addDatabase('QSQLITE')
        db.setDatabaseName('{}.db'.format(db_text))
        db.open()
        # 实例化一个可编辑数据模型
        self.model = QtSql.QSqlTableModel()

        self.table_widget.setModel(self.model)
        self.table_widget.setSortingEnabled(True)

        self.model.setTable('metric')  # 设置数据模型的数据表
        # self.model.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange) # 允许字段更改
        self.model.select()  # 查询所有数据
        # 设置表格头
        self.model.setHeaderData(0, QtCore.Qt.Horizontal, 'ID')
        self.model.setHeaderData(1, QtCore.Qt.Horizontal, 'Model')
        self.model.setHeaderData(2, QtCore.Qt.Horizontal, 'dataset')
        self.model.setHeaderData(3, QtCore.Qt.Horizontal, 'class')
        self.model.setHeaderData(4, QtCore.Qt.Horizontal, 'TP')
        self.model.setHeaderData(5, QtCore.Qt.Horizontal, 'FP')
        self.model.setHeaderData(6, QtCore.Qt.Horizontal, 'FN')
        self.model.setHeaderData(7, QtCore.Qt.Horizontal, 'F1')
        self.model.setHeaderData(8, QtCore.Qt.Horizontal, 'ap')
        self.model.setHeaderData(9, QtCore.Qt.Horizontal, 'map')
        self.model.setHeaderData(10, QtCore.Qt.Horizontal, 'precision')
        self.model.setHeaderData(11, QtCore.Qt.Horizontal, 'recall')
        self.model.setHeaderData(12, QtCore.Qt.Horizontal, 'threshold')
        layout.addWidget(self.table_widget)
        self.tab3.setLayout(layout)

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

    def comboSelectionChanged(self,index):
        text = self.combobox_process.itemText(index)
        if text=='yolov3':
            self.process_method='yolov3'
        elif text=='yolov5':
            self.process_method='yolov5'

    def comboSelectionChanged1(self, index):
        text = self.combobox_classes.itemText(index)
        if text == '':
            print(1)
        else:
            self.class_name_draw = text

    def load_annotations_gt(self):

        if self.rad_gt_format_coco_json.isChecked():
            self.ret='coco'
        elif self.rad_gt_format_pascalvoc_xml.isChecked():
            self.ret='voc'
        elif self.rad_gt_format_yolo_text.isChecked():
            self.ret='darknet'
        if self.ret=='':
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
        file_path=directory[0]
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

    def btn_show_classes_clicked(self):
        name=None
        if not self.data_line.text()=='':
            name=self.data_line.text()
        elif not self.model_line.text()=='':
            name=self.model_line.text()
        else:
            print(1)

        class_names=DBManager().search_classes(name)

        self.combobox_classes.addItems(class_names)

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

    def btn_draw_clicked(self):
       # self.process.setVisible(False)
       # self.groupBox.setVisible(True)
       plt= DBManager().draw()
       self.gridlayout.addWidget(plt, 0, 2)

    def btn_save_clicked(self):
        if self.result_csv is None:
            print("error")
        else:
            DB=DBManager()
            result_csv = self.result_csv.split("\n")
            #each class
            class_name=result_csv[4].split(",")
            model_name = os.path.splitext(os.path.split(self.dir_model_gt)[1])[0]
            dataset_name = os.path.splitext(os.path.split(self.dir_images_gt)[1])[0]
            AP_class,F1_class,prec_class,rec_class,threshold_class,TP_class,FP_class,FN_class=result_csv[6].split(","),result_csv[7].split(","),\
                                                                   result_csv[8].split(","),result_csv[9].split(","),result_csv[10].split(",")\
                ,result_csv[11].split(","),result_csv[12].split(","),result_csv[13].split(",")

            TP_all,FP_all,FN_all=0,0,0

            #id, model_name, dataset, class, [f1, fp, tp, fn, map, prec, recall], threshold(best select by f1)
            for i,name_cl in enumerate(class_name):
                if name_cl=='class_names 'or name_cl=='':
                    continue
                else:
                    map_cl=0
                    ap_cl,tp_cl,fp_cl,fn_cl,F1_cl,prec_cl,rec_cl,thre_cl=AP_class[i],TP_class[i],FP_class[i],\
                                                                         FN_class[i],F1_class[i],prec_class[i],rec_class[i],threshold_class[i]
                    TP_all+=int(tp_cl)
                    FP_all+=int(fp_cl)
                    FN_all+=int(fn_cl)

                DB.add_item(model_name, dataset_name,name_cl,tp_cl,fp_cl,fn_cl,F1_cl,ap_cl,map_cl,prec_cl,rec_cl,thre_cl)

            #save all classes metric
            result_metric = result_csv[2].split(",")
            map,recall,F1_,Precision = float(result_metric[0]),float(result_metric[1]),float(result_metric[2]),float(result_metric[3])

            DB.add_item(model_name,dataset_name, "all",TP_all,FP_all,FN_all,F1_,0,map, Precision,recall,thre_cl)

    def btn_run_clicked(self):
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
        self.result_csv = evaluation.evaluate()

    def btn_draw_by_model(self):
        model_name = None
        if self.model_line.text() == '':
            print(1)
        else:
            model_name = self.model_line.text()

        plt = DBManager().draw_by_model(model_name, self.class_name_draw)
        self.gridlayout.addWidget(plt, 0, 2)

    def btn_draw_by_data(self):
        dataset_name=None
        if self.data_line.text()=='':
            print(1)
        else:
            dataset_name=self.data_line.text()

        plt = DBManager().draw_by_data(dataset_name,self.class_name_draw)
        self.gridlayout.addWidget(plt, 0, 2)


