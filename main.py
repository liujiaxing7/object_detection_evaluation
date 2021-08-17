import os
import sys
import onnx
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QMainWindow, QMessageBox
from PyQt5 import QtCore, QtGui
from src.ui.main_ui import Ui_Dialog as Main_UI

class Stream(QtCore.QObject):
    """Redirects console output to text widget."""
    newText = QtCore.pyqtSignal(str)

    def write(self, text):
        self.newText.emit(str(text))

class Main_Dialog(QMainWindow, Main_UI):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.current_directory = os.path.dirname(os.path.realpath(__file__))
        # Define error msg dialog
        self.msgBox = QMessageBox()


        # Default values
        self.dir_annotations_gt = None
        self.dir_images_gt = None
        self.filepath_classes_gt = None
        self.dir_dets = None
        self.filepath_classes_det = None
        self.dir_save_results = None
        self.ret = ''

        self.center_screen()

        sys.stdout = Stream(newText=self.onUpdateText)

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

    def load_annotations_gt(self):
        print()
        if self.rad_gt_format_coco_json.isChecked():
            self.ret='coco'
        elif self.rad_gt_format_pascalvoc_xml.isChecked():
            self.ret='voc'
        elif self.rad_gt_format_yolo_text.isChecked():
            self.ret='darknet'
        if self.ret=='':
            print("no format select")
            exit(-1)


    # def validate_det_choices(self):
    #     pass
    #
    # def load_annotations_det(self):
    #     pass

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
            self.dir_annotations_gt = file_path
        else:
            self.dir_annotations_gt = None
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

    # def btn_statistics_det_clicked(self):
    #     pass

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

    def btn_run_clicked(self):
        if self.rad_gt_format_coco_json.isChecked():
            self.ret='coco'
        elif self.rad_gt_format_pascalvoc_xml.isChecked():
            self.ret='voc'
        elif self.rad_gt_format_yolo_text.isChecked():
            self.ret='darknet'
        if self.ret=='':
            print("no format select")
            exit(-1)
        evaluation = onnx.ONNX(self.dir_annotations_gt, 64, self.dir_images_gt, self.filepath_classes_gt,self.ret)
        evaluation.evaluate()
if __name__=='__main__':
    app = QtWidgets.QApplication(sys.argv)

    ui = Main_Dialog()
    ui.show()
    sys.exit(app.exec_())