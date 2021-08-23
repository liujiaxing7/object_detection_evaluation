import os
import sys

from PyQt5.QtWidgets import QFileDialog, QMainWindow, QMessageBox

from src.database.db import DBManager
from src.ui.visual_ui import Ui_Dialog as Main_UI

import matplotlib
matplotlib.use("Qt5Agg")



class Main_Dialog(QMainWindow, Main_UI):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)

    def btn_drawbydata_clicked(self):
        plt = DBManager().draw()
        self.gridlayout.addWidget(plt, 0, 2)
    def btn_drawbymodel_clicked(self):
        plt = DBManager().draw()
        self.gridlayout.addWidget(plt, 0, 2)
