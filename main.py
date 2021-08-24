import sys
from PyQt5 import QtCore, QtWidgets
import matplotlib
matplotlib.use("Qt5Agg")
from src.ui.visual_ui import Ui_Dialog



if __name__=='__main__':
    app = QtWidgets.QApplication(sys.argv)

    ui = Ui_Dialog()
    ui.show()

    sys.exit(app.exec_())