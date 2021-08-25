import sys
from PyQt5 import QtWidgets
from src.ui.visual_ui import Ui_Window

if __name__=='__main__':
    app = QtWidgets.QApplication(sys.argv)

    ui = Ui_Window()
    ui.show()

    sys.exit(app.exec_())