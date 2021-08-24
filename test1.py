from PyQt5 import QtWidgets
from PyQt5.Qt import * #刚开始学习可以这样一下导入
import sys
class gameWindow(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.setGeometry(300,300,1280,800)

        self.frame = QFrame()
        self.frame.resize(300,300)
        self.frame.setStyleSheet("background-color: rgb(200, 255, 255)")

        layout=QVBoxLayout()
        layout.addWidget(self.frame)
        self.setLayout(layout)
if __name__=='__main__':
    app = QtWidgets.QApplication(sys.argv)

    ui = gameWindow()
    ui.show()

    sys.exit(app.exec_())