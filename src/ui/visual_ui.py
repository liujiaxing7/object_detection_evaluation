# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main_ui.ui'
#
# Created by: PyQt5 UI code generator 5.12.3
#
# WARNING! All changes made in this file will be lost!
import os

from PyQt5 import QtGui,QtCore,QtWidgets,QtSql
from PyQt5.QtWidgets import QDesktopWidget

from src.database.db import DBManager


class Ui_Dialog(object):
    def __init__(self):
        # super(Ui_Dialog, self).__init__()
        pass
    def setupUi(self, Dialog):
        self.Dialog=Dialog
        Dialog.setObjectName("Dialog")
        Dialog.resize(1214, 850)
        Dialog.setMinimumSize(QtCore.QSize(1214, 950))
        Dialog.setMaximumSize(QtCore.QSize(1214, 950))


        self.tab_widget=QtWidgets.QTabWidget(Dialog)
        self.addTab(self.tab1, "Tab 1")
        

        self.lbl_groundtruth = QtWidgets.QLabel(Dialog)
        self.lbl_groundtruth.setGeometry(QtCore.QRect(10, 20, 1191, 40))
        self.lbl_groundtruth.setObjectName("lbl_groundtruth")
        self.lbl_groundtruth.setAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        self.lbl_groundtruth.setFont(font)

        self.btn_draw_bydata = QtWidgets.QPushButton(Dialog)
        self.btn_draw_bydata.setGeometry(QtCore.QRect(10, 100, 150, 27))
        self.btn_draw_bydata.setObjectName("btn_draw_bydata")
        self.btn_draw_bymodel=QtWidgets.QPushButton(Dialog)
        self.btn_draw_bymodel.setGeometry(QtCore.QRect(10,130,150,27))
        self.btn_draw_bymodel.setObjectName("btn_draw_bymodel")
        self.widget = QtWidgets.QWidget(Dialog)
        self.widget.setGeometry(QtCore.QRect(130, 380, 891, 451))
        self.widget.setObjectName("widget")
        self.groupBox = QtWidgets.QGroupBox(self.widget)
        self.groupBox.setGeometry(QtCore.QRect(0, 30, 891, 451))
        self.groupBox.setObjectName("groupBox")
        self.gridlayout = QtWidgets.QGridLayout(self.groupBox)
        self.retranslateUi(Dialog)

        self.btn_draw_bydata.clicked.connect(Dialog.btn_drawbydata_clicked)
        self.btn_draw_bymodel.clicked.connect(Dialog.btn_drawbymodel_clicked)



    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Visual Comparsion"))
        self.btn_draw_bydata.setText(_translate("Dialog", "Draw by Data"))
        self.btn_draw_bymodel.setText(_translate("Dialog", "Draw by Model"))
        self.lbl_groundtruth.setText(_translate("Dialog","Visual Comparsion"))

