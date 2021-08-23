# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main_ui.ui'
#
# Created by: PyQt5 UI code generator 5.12.3
#
# WARNING! All changes made in this file will be lost!
import os

from PyQt5 import QtGui,QtCore,QtWidgets,QtSql
from PyQt5.QtWidgets import QDesktopWidget


class Ui_Dialog(object):
    def __init__(self):
        # super(Ui_Dialog, self).__init__()
        pass
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(1214, 850)
        Dialog.setMinimumSize(QtCore.QSize(1214, 950))
        Dialog.setMaximumSize(QtCore.QSize(1214, 950))

        self.table_widget = QtWidgets.QTableView(Dialog)
        self.table_widget.setGeometry(0,0,1214,950)
        db_text = os.getcwd()+'/src/database/core'

        self.db_name = db_text
        # 添加一个sqlite数据库连接并打开
        db = QtSql.QSqlDatabase.addDatabase('QSQLITE')
        db.setDatabaseName('{}.db'.format(db_text))
        db.open()
        # 实例化一个可编辑数据模型
        self.model = QtSql.QSqlTableModel()
        self.table_widget.setModel(self.model)

        self.model.setTable('metric')  # 设置数据模型的数据表
        # self.model.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange) # 允许字段更改
        self.model.select()  # 查询所有数据
        # 设置表格头
        self.model.setHeaderData(0, QtCore.Qt.Horizontal, 'ID')
        self.model.setHeaderData(1, QtCore.Qt.Horizontal, 'Model')
        self.model.setHeaderData(2, QtCore.Qt.Horizontal, 'Map')
        self.model.setHeaderData(3, QtCore.Qt.Horizontal, 'Recall')
        self.model.setHeaderData(4, QtCore.Qt.Horizontal, 'Precision')
        self.model.setHeaderData(5, QtCore.Qt.Horizontal, 'F1')
    # def center(self):  # 定义一个函数使得窗口居中显示
    #     # 获取屏幕坐标系
    #     screen = QDesktopWidget().screenGeometry()
    #     # 获取窗口坐标系
    #     size = self.geometry()
    #     newLeft = (screen.width() - size.width()) / 2
    #     newTop = (screen.height() - size.height()) / 2
    #     self.move(int(newLeft),int(newTop))


    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
