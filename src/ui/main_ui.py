# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main_ui.ui'
#
# Created by: PyQt5 UI code generator 5.12.3
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtSql import QSqlQuery,QSqlDatabase



class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(1214, 850)
        Dialog.setMinimumSize(QtCore.QSize(1214, 950))
        Dialog.setMaximumSize(QtCore.QSize(1214, 950))
        #button
        self.combobox_process = QtWidgets.QComboBox(Dialog)
        self.combobox_process.setGeometry(QtCore.QRect(151, 265, 221, 27))
        self.combobox_process.setObjectName("combobox_process")
        self.combobox_process.addItems(['','yolov3','yolov5'])


        self.btn_gt_images_dir = QtWidgets.QPushButton(Dialog)
        self.btn_gt_images_dir.setGeometry(QtCore.QRect(1170, 70, 31, 27))
        self.btn_gt_images_dir.setObjectName("btn_gt_images_dir")
        self.txb_gt_images_dir = QtWidgets.QLineEdit(Dialog)
        self.txb_gt_images_dir.setGeometry(QtCore.QRect(110, 70, 1051, 27))
        self.txb_gt_images_dir.setReadOnly(True)
        self.txb_gt_images_dir.setObjectName("txb_gt_images_dir")
        self.txb_gt_dir = QtWidgets.QLineEdit(Dialog)
        self.txb_gt_dir.setGeometry(QtCore.QRect(110, 40, 1051, 27))
        self.txb_gt_dir.setReadOnly(True)
        self.txb_gt_dir.setObjectName("txb_gt_dir")
        self.btn_gt_dir = QtWidgets.QPushButton(Dialog)
        self.btn_gt_dir.setGeometry(QtCore.QRect(1170, 40, 31, 27))
        self.btn_gt_dir.setObjectName("btn_gt_dir")
        #frame+radio
        self.frame = QtWidgets.QFrame(Dialog)
        self.frame.setGeometry(QtCore.QRect(10, 160, 1191, 101))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.rad_gt_format_coco_json = QtWidgets.QRadioButton(self.frame)
        self.rad_gt_format_coco_json.setGeometry(QtCore.QRect(10, 40, 161, 22))
        self.rad_gt_format_coco_json.setChecked(True)
        self.rad_gt_format_coco_json.setObjectName("rad_gt_format_coco_json")
        self.lbl_detections_dir_3 = QtWidgets.QLabel(self.frame)
        self.lbl_detections_dir_3.setGeometry(QtCore.QRect(10, 10, 151, 17))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.lbl_detections_dir_3.setFont(font)
        self.lbl_detections_dir_3.setObjectName("lbl_detections_dir_3")
        self.rad_gt_format_pascalvoc_xml = QtWidgets.QRadioButton(self.frame)
        self.rad_gt_format_pascalvoc_xml.setGeometry(QtCore.QRect(470, 40, 151, 22))
        self.rad_gt_format_pascalvoc_xml.setObjectName("rad_gt_format_pascalvoc_xml")
        self.rad_gt_format_labelme_xml = QtWidgets.QRadioButton(self.frame)
        self.rad_gt_format_labelme_xml.setGeometry(QtCore.QRect(220, 40, 231, 22))
        self.rad_gt_format_labelme_xml.setObjectName("rad_gt_format_labelme_xml")
        self.rad_gt_format_yolo_text = QtWidgets.QRadioButton(self.frame)
        self.rad_gt_format_yolo_text.setGeometry(QtCore.QRect(750, 40, 181, 22))
        self.rad_gt_format_yolo_text.setChecked(False)
        self.rad_gt_format_yolo_text.setObjectName("rad_gt_format_yolo_text")

        self.lbl_groundtruth_dir_3 = QtWidgets.QLabel(Dialog)
        self.lbl_groundtruth_dir_3.setGeometry(QtCore.QRect(10, 10, 1191, 20))
        font = QtGui.QFont()
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        self.lbl_groundtruth_dir_3.setFont(font)
        self.lbl_groundtruth_dir_3.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_groundtruth_dir_3.setObjectName("lbl_groundtruth_dir_3")
        self.lbl_groundtruth_dir_2 = QtWidgets.QLabel(Dialog)
        self.lbl_groundtruth_dir_2.setGeometry(QtCore.QRect(10, 75, 101, 17))
        self.lbl_groundtruth_dir_2.setObjectName("lbl_groundtruth_dir_2")
        self.lbl_groundtruth_dir = QtWidgets.QLabel(Dialog)
        self.lbl_groundtruth_dir.setGeometry(QtCore.QRect(10, 45, 101, 17))
        self.lbl_groundtruth_dir.setObjectName("lbl_groundtruth_dir")
        self.lbl_groundtruth_dir_22 = QtWidgets.QLabel(Dialog)
        self.lbl_groundtruth_dir_22.setGeometry(QtCore.QRect(10, 300, 1181, 20))
        self.btn_run = QtWidgets.QPushButton(Dialog)
        self.btn_run.setGeometry(QtCore.QRect(10, 920, 1191, 27))

        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.btn_run.setFont(font)
        self.btn_run.setObjectName("btn_run")
        self.lbl_groundtruth_dir_24 = QtWidgets.QLabel(Dialog)
        self.lbl_groundtruth_dir_24.setGeometry(QtCore.QRect(10, 370, 101, 17))
        self.lbl_groundtruth_dir_24.setObjectName("lbl_groundtruth_dir_24")

        self.txb_classes_gt = QtWidgets.QLineEdit(Dialog)
        self.txb_classes_gt.setGeometry(QtCore.QRect(110, 100, 1051, 27))
        self.txb_classes_gt.setReadOnly(True)
        self.txb_classes_gt.setObjectName("txb_classes_gt")
        self.lbl_groundtruth_dir_25 = QtWidgets.QLabel(Dialog)
        self.lbl_groundtruth_dir_25.setGeometry(QtCore.QRect(10, 105, 101, 17))
        self.lbl_groundtruth_dir_25.setObjectName("lbl_groundtruth_dir_25")
        self.btn_groundtruth_dir_5 = QtWidgets.QPushButton(Dialog)
        self.btn_groundtruth_dir_5.setGeometry(QtCore.QRect(1170, 100, 31, 27))
        self.btn_groundtruth_dir_5.setObjectName("btn_groundtruth_dir_5")
        self.btn_groundtruth_dir_5.setFont(font)
        self.btn_groundtruth_dir_6 = QtWidgets.QLabel(Dialog)
        self.btn_groundtruth_dir_6.setGeometry(QtCore.QRect(10, 265, 141, 27))
        self.btn_groundtruth_dir_6.setObjectName("btn_groundtruth_dir_6")
        self.lbl_groundtruth_dir_27 = QtWidgets.QLabel(Dialog)
        self.lbl_groundtruth_dir_27.setGeometry(QtCore.QRect(110, 130, 531, 21))
        self.lbl_groundtruth_dir_27.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.lbl_groundtruth_dir_27.setObjectName("lbl_groundtruth_dir_27")

        self.process = QtWidgets.QTextEdit(self, readOnly=True)
        self.process.setGeometry(QtCore.QRect(37, 320, 1110, 200))
        self.process.ensureCursorVisible()

        self.btn_draw = QtWidgets.QPushButton(Dialog)
        self.btn_draw.setGeometry(QtCore.QRect(1150, 265, 50, 27))
        self.btn_save_db = QtWidgets.QPushButton(Dialog)
        self.btn_save_db.setGeometry(QtCore.QRect(1090, 265, 50, 27))
        self.widget = QtWidgets.QWidget(Dialog)
        self.widget.setGeometry(QtCore.QRect(130, 350, 891, 451))
        self.widget.setObjectName("widget")
        self.groupBox = QtWidgets.QGroupBox(self.widget)
        self.groupBox.setGeometry(QtCore.QRect(0, 0, 891, 451))
        self.groupBox.setObjectName("groupBox")


        self.retranslateUi(Dialog)
        self.btn_gt_dir.clicked.connect(Dialog.btn_gt_dir_clicked)
        self.btn_gt_images_dir.clicked.connect(Dialog.btn_gt_images_dir_clicked)
        self.combobox_process.currentIndexChanged.connect(Dialog.comboSelectionChanged)
        self.btn_groundtruth_dir_5.clicked.connect(Dialog.btn_gt_classes_clicked)
        self.btn_run.clicked.connect(Dialog.btn_run_clicked)
        self.btn_draw.clicked.connect(Dialog.btn_draw_clicked)
        self.btn_save_db.clicked.connect(Dialog.btn_save_clicked)

        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.txb_gt_dir, self.btn_gt_dir)
        Dialog.setTabOrder(self.btn_gt_dir, self.txb_gt_images_dir)
        Dialog.setTabOrder(self.txb_gt_images_dir, self.btn_gt_images_dir)
        Dialog.setTabOrder(self.btn_gt_images_dir, self.rad_gt_format_coco_json)
        Dialog.setTabOrder(self.rad_gt_format_coco_json,self.rad_gt_format_labelme_xml)
        Dialog.setTabOrder(self.rad_gt_format_labelme_xml, self.rad_gt_format_yolo_text)
        Dialog.setTabOrder(self.rad_gt_format_yolo_text, self.rad_gt_format_pascalvoc_xml)
        Dialog.setTabOrder(self.rad_gt_format_pascalvoc_xml, self.combobox_process)



    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Object Detection Metrics"))
        self.combobox_process.setToolTip(_translate("Dialog", "The configurations will be applied in a random ground truth image."))
        # self.btn_stats_gt.setText(_translate("Dialog", "show ground-truth statistics"))
        self.btn_gt_images_dir.setText(_translate("Dialog", "..."))
        self.btn_gt_dir.setText(_translate("Dialog", "..."))
        self.rad_gt_format_coco_json.setText(_translate("Dialog", "COCO (.json)"))
        self.lbl_detections_dir_3.setText(_translate("Dialog", "Coordinates format:"))

        self.rad_gt_format_labelme_xml.setText(_translate("Dialog", "Label Me (.xml)"))
        self.rad_gt_format_pascalvoc_xml.setText(_translate("Dialog", "PASCAL VOC (.xml)"))

        self.rad_gt_format_yolo_text.setText(_translate("Dialog", "(*) YOLO (.txt)"))
        self.lbl_groundtruth_dir_3.setText(_translate("Dialog", "Ground truth"))
        self.lbl_groundtruth_dir_2.setText(_translate("Dialog", "Images:"))
        self.lbl_groundtruth_dir.setText(_translate("Dialog", "Model:"))

        self.btn_run.setText(_translate("Dialog", "RUN"))
        self.btn_draw.setText(_translate("Dialog", "Draw"))
        self.btn_save_db.setText(_translate("Dialog", "Save"))

        self.lbl_groundtruth_dir_25.setText(_translate("Dialog", "Classes (*):"))
        self.btn_groundtruth_dir_5.setText(_translate("Dialog", "..."))
        self.btn_groundtruth_dir_6.setText(_translate("Dialog", "Onnx Model Type:"))
        self.lbl_groundtruth_dir_27.setText(_translate("Dialog", "* required for yolo (.txt) format only."))


