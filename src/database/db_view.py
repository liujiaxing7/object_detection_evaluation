# coding:utf-8

from PyQt5 import QtGui,QtCore,QtWidgets,QtSql
import sys

'''
    州的先生 - 在PyQt5中使用数据库
'''

class MainUi(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUi()

    # 初始化UI界面
    def initUi(self):
        # 设置窗口标题
        self.setWindowTitle("PyQt5查询数据库")
        # 设置窗口大小
        self.resize(1900,400)

        # 创建一个窗口部件
        self.widget = QtWidgets.QWidget()
        # 创建一个网格布局
        self.grid_layout = QtWidgets.QGridLayout()
        # 设置窗口部件的布局为网格布局
        self.widget.setLayout(self.grid_layout)

        # 创建一个按钮组
        self.group_box = QtWidgets.QGroupBox('数据库按钮')
        self.group_box_layout = QtWidgets.QVBoxLayout()
        self.group_box.setLayout(self.group_box_layout)
        # 创建一个表格部件
        self.table_widget = QtWidgets.QTableView()
        # 将上述两个部件添加到网格布局中
        self.grid_layout.addWidget(self.group_box,0,0)
        self.grid_layout.addWidget(self.table_widget,0,1)

        # 创建按钮组的按钮
        self.b_create_db = QtWidgets.QPushButton("创建数据库")
        # self.b_create_db.clicked.connect(self.create_db)
        self.b_view_data = QtWidgets.QPushButton("浏览数据")
        self.b_add_row = QtWidgets.QPushButton("添加一行")
        self.b_delete_row = QtWidgets.QPushButton("删除一行")
        self.b_close = QtWidgets.QPushButton("退出")

        # 添加按钮到按钮组中
        self.group_box_layout.addWidget(self.b_create_db)
        self.group_box_layout.addWidget(self.b_view_data)
        self.group_box_layout.addWidget(self.b_add_row)
        self.group_box_layout.addWidget(self.b_delete_row)
        self.group_box_layout.addWidget(self.b_close)

        # 设置UI界面的核心部件
        self.setCentralWidget(self.widget)
        self.b_view_data.clicked.connect(self.view_data)
        self.b_delete_row.clicked.connect(self.del_row_data)
    def view_data(self):
        db_text='core'

        print(db_text)
        self.db_name = db_text
        # 添加一个sqlite数据库连接并打开
        db = QtSql.QSqlDatabase.addDatabase('QSQLITE')
        db.setDatabaseName('{}.db'.format(db_text))
        db.open()
        # 实例化一个可编辑数据模型
        self.model = QtSql.QSqlTableModel()
        self.table_widget.setModel(self.model)

        self.model.setTable('metric_') # 设置数据模型的数据表
        # self.model.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange) # 允许字段更改
        self.model.select() # 查询所有数据
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
        # 添加一行数据行

    def del_row_data(self):
        if self.model:
            self.model.removeRow(self.table_widget.currentIndex().row())
        else:
            self.create_db()

if __name__=='__main__':
    app = QtWidgets.QApplication(sys.argv)

    ui = MainUi()
    ui.show()
    sys.exit(app.exec_())