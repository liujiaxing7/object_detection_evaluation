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

from src.database.db import DBManager


class M(QTabWidget):
    def __init__(self,parent=None):
        pass

    def tab2UI(self):
        layout = QFormLayout()

        gt = QHBoxLayout()
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        gt_label=QLabel("Ground truth")
        gt.addWidget(gt_label)
        gt_label.setFont(font)
        layout.addRow(gt)

        h1 = QHBoxLayout()
        h1.addWidget(QLabel("Model:       "))
        model_qline=QLineEdit()
        model_qline.setReadOnly(True)
        h1.addWidget(model_qline)
        load_model_dir = QPushButton("...")
        h1.addWidget(load_model_dir)
        # load_model_dir.clicked.connect()|
        layout.addRow(h1)

        h2 = QHBoxLayout()
        h2.addWidget(QLabel("Images:     "))
        images_qline = QLineEdit()
        images_qline.setReadOnly(True)
        h2.addWidget(images_qline)
        load_images_dir = QPushButton("...")
        h2.addWidget(load_images_dir)
        # load_images_dir.clicked.connect()
        layout.addRow(h2)

        h3 = QHBoxLayout()
        h3.addWidget(QLabel("Classes(*):"))
        class_qline = QLineEdit()
        class_qline.setReadOnly(True)
        h3.addWidget(class_qline)
        load_class_dir = QPushButton("...")
        h3.addWidget(load_class_dir)
        # load_class_dir.clicked.connect()
        layout.addRow(h3)
        layout.addRow(QLabel("                     * required for yolo (.txt) format only."))
        layout.addRow(QLabel(''))
        gt_format=QLabel("Coordinates format:")
        gt_format.setFont(font)
        layout.addRow(gt_format)




        # layout.addRow(QGraphicsLineItem())
        # window = QWidget()
        # frame = QFrame(window)
        # frame.resize(300, 300)
        # frame.setStyleSheet("background-color: rgb(200, 255, 255)")
        h4 = QHBoxLayout()
        h4.addWidget(QCheckBox("COCO (.json)"))
        h4.addWidget(QCheckBox("Label Me (.xml)"))
        h4.addWidget(QCheckBox("PASCAL VOC (.xml)"))
        h4.addWidget(QCheckBox("(*) YOLO (.txt)"))
        layout.addItem(h4)
        layout.addRow(QLabel(' '))

        h5=QHBoxLayout()
        h5.addWidget(QLabel("Onnx Model Type:"),1, Qt.AlignLeft )
        combobox=QComboBox()
        h5.addWidget(combobox,5, Qt.AlignLeft )
        combobox.addItems(['','yolov3','yolov5'])
        combobox.setMinimumSize(200,27)
        btn_save=QPushButton("save")
        h5.addWidget(btn_save,1, Qt.AlignRight )
        btn_save.setMinimumSize(60,27)
        layout.addRow(h5)

        text_edit=QTextEdit()
        layout.addRow(text_edit)

        h6=QHBoxLayout()
        btn_run=QPushButton("RUN")
        h6.addWidget(btn_run)
        layout.addRow(h6)

        self.tab1.setLayout(layout)

    def draw_by_Data(self):
        print(1)

    def draw_by_Model(self):
        print(1)

