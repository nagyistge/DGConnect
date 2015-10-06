# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Ui_InfoCube.ui'
#
# Created: Tue Aug  4 15:16:57 2015
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import pyqtSlot
from qgis.core import QgsRectangle
from PyQt4.QtGui import QMessageBox
import InfoCubeProcessForm
import logging as log

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8

    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


class Ui_InfoCube(object):

    def __init__(self):
        self.formLayout = None
        self.client_secret = None
        self.client_secret_label = None
        self.client_id = None
        self.client_id_label = None
        self.password = None
        self.password_label = None
        self.username = None
        self.username_label = None
        self.select_file = None
        self.select_file_button = None
        self.select_file_label = None
        self.top = None
        self.top_label = None
        self.left = None
        self.left_label = None
        self.right = None
        self.right_label = None
        self.bottom = None
        self.bottom_label = None
        self.load_settings_button = None
        self.yes_no_box = None
        self.save_settings_button = None
        self.settings_layout = None
        self.select_file_layout = None
        self.bbox_layout = None
        self.top_layout = None
        self.left_layout = None
        self.right_layout = None
        self.bottom_layout = None
        self.line = None
        self.line_2 = None
        self.dialog = None
        self.csv_generator = None

    def setupUi(self, dialog):
        dialog.setObjectName(_fromUtf8("DGConnect"))
        dialog.resize(918, 221)

        self.dialog = dialog
        
        self.formLayout = QtGui.QFormLayout(dialog)
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.username_label = QtGui.QLabel(dialog)
        self.username_label.setObjectName(_fromUtf8("username_label"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.username_label)
        self.username = QtGui.QLineEdit(dialog)
        self.username.setObjectName(_fromUtf8("username"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.username)
        self.password_label = QtGui.QLabel(dialog)
        self.password_label.setObjectName(_fromUtf8("password_label"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.password_label)
        self.password = QtGui.QLineEdit(dialog)
        self.password.setEchoMode(QtGui.QLineEdit.Password)
        self.password.setObjectName(_fromUtf8("password"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.password)
        self.client_id_label = QtGui.QLabel(dialog)
        self.client_id_label.setObjectName(_fromUtf8("client_id_label"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.client_id_label)
        self.client_id = QtGui.QLineEdit(dialog)
        self.client_id.setObjectName(_fromUtf8("client_id"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.client_id)
        self.client_secret_label = QtGui.QLabel(dialog)
        self.client_secret_label.setObjectName(_fromUtf8("client_secret_label"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.LabelRole, self.client_secret_label)
        self.client_secret = QtGui.QLineEdit(dialog)
        self.client_secret.setEchoMode(QtGui.QLineEdit.Password)
        self.client_secret.setObjectName(_fromUtf8("client_secret"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.FieldRole, self.client_secret)
        self.select_file_layout = QtGui.QHBoxLayout()
        self.select_file_layout.setObjectName(_fromUtf8("select_file_layout"))
        self.select_file = QtGui.QLineEdit(dialog)
        self.select_file.setObjectName(_fromUtf8("select_file"))
        self.select_file_layout.addWidget(self.select_file)
        self.select_file_button = QtGui.QPushButton(dialog)
        self.select_file_button.setObjectName(_fromUtf8("select_file_button"))
        self.select_file_layout.addWidget(self.select_file_button)
        self.formLayout.setLayout(6, QtGui.QFormLayout.FieldRole, self.select_file_layout)
        self.settings_layout = QtGui.QHBoxLayout()
        self.settings_layout.setContentsMargins(-1, -1, 0, 0)
        self.settings_layout.setObjectName(_fromUtf8("settings_layout"))
        self.load_settings_button = QtGui.QPushButton(dialog)
        self.load_settings_button.setCheckable(False)
        self.load_settings_button.setObjectName(_fromUtf8("load_settings_button"))
        self.settings_layout.addWidget(self.load_settings_button)
        self.save_settings_button = QtGui.QPushButton(dialog)
        self.save_settings_button.setCheckable(False)
        self.save_settings_button.setObjectName(_fromUtf8("save_settings_button"))
        self.settings_layout.addWidget(self.save_settings_button)
        self.formLayout.setLayout(7, QtGui.QFormLayout.LabelRole, self.settings_layout)
        self.line = QtGui.QFrame(dialog)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.formLayout.setWidget(9, QtGui.QFormLayout.SpanningRole, self.line)
        self.bbox_layout = QtGui.QGridLayout()
        self.bbox_layout.setContentsMargins(-1, -1, -1, 0)
        self.bbox_layout.setHorizontalSpacing(6)
        self.bbox_layout.setObjectName(_fromUtf8("bbox_layout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.bbox_layout.addItem(spacerItem, 0, 2, 1, 1)
        self.top_layout = QtGui.QHBoxLayout()
        self.top_layout.setContentsMargins(0, -1, -1, -1)
        self.top_layout.setObjectName(_fromUtf8("top_layout"))
        self.top_label = QtGui.QLabel(dialog)
        self.top_label.setObjectName(_fromUtf8("top_label"))
        self.top_layout.addWidget(self.top_label)
        self.top = QtGui.QLineEdit(dialog)
        self.top.setReadOnly(False)
        self.top.setObjectName(_fromUtf8("top"))
        self.top_layout.addWidget(self.top)
        self.bbox_layout.addLayout(self.top_layout, 0, 1, 1, 1)
        self.left_layout = QtGui.QHBoxLayout()
        self.left_layout.setContentsMargins(-1, -1, -1, 0)
        self.left_layout.setObjectName(_fromUtf8("left_layout"))
        self.left_label = QtGui.QLabel(dialog)
        self.left_label.setObjectName(_fromUtf8("left_label"))
        self.left_layout.addWidget(self.left_label)
        self.left = QtGui.QLineEdit(dialog)
        self.left.setReadOnly(False)
        self.left.setObjectName(_fromUtf8("left"))
        self.left_layout.addWidget(self.left)
        self.bbox_layout.addLayout(self.left_layout, 1, 0, 1, 1)
        self.right_layout = QtGui.QHBoxLayout()
        self.right_layout.setObjectName(_fromUtf8("right_layout"))
        self.right_label = QtGui.QLabel(dialog)
        self.right_label.setObjectName(_fromUtf8("right_label"))
        self.right_layout.addWidget(self.right_label)
        self.right = QtGui.QLineEdit(dialog)
        self.right.setReadOnly(False)
        self.right.setObjectName(_fromUtf8("right"))
        self.right_layout.addWidget(self.right)
        self.bbox_layout.addLayout(self.right_layout, 1, 2, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.bbox_layout.addItem(spacerItem1, 0, 0, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.bbox_layout.addItem(spacerItem2, 1, 1, 1, 1)
        self.bottom_layout = QtGui.QHBoxLayout()
        self.bottom_layout.setContentsMargins(-1, -1, -1, 0)
        self.bottom_layout.setObjectName(_fromUtf8("bottom_layout"))
        self.bottom_label = QtGui.QLabel(dialog)
        self.bottom_label.setObjectName(_fromUtf8("bottom_label"))
        self.bottom_layout.addWidget(self.bottom_label)
        self.bottom = QtGui.QLineEdit(dialog)
        self.bottom.setReadOnly(False)
        self.bottom.setObjectName(_fromUtf8("bottom"))
        self.bottom_layout.addWidget(self.bottom)
        self.bbox_layout.addLayout(self.bottom_layout, 2, 1, 1, 1)
        self.formLayout.setLayout(13, QtGui.QFormLayout.SpanningRole, self.bbox_layout)
        self.line_2 = QtGui.QFrame(dialog)
        self.line_2.setFrameShape(QtGui.QFrame.HLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName(_fromUtf8("line_2"))
        self.formLayout.setWidget(15, QtGui.QFormLayout.SpanningRole, self.line_2)
        self.yes_no_box = QtGui.QDialogButtonBox(dialog)
        self.yes_no_box.setOrientation(QtCore.Qt.Horizontal)
        self.yes_no_box.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.yes_no_box.setObjectName(_fromUtf8("yes_no_box"))
        self.formLayout.setWidget(16, QtGui.QFormLayout.FieldRole, self.yes_no_box)
        self.select_file_label = QtGui.QLabel(dialog)
        self.select_file_label.setObjectName(_fromUtf8("select_file_label"))
        self.formLayout.setWidget(6, QtGui.QFormLayout.LabelRole, self.select_file_label)
        self.username_label.setBuddy(self.username)
        self.password_label.setBuddy(self.password)
        self.client_id_label.setBuddy(self.client_id)
        self.client_secret_label.setBuddy(self.client_secret)
        self.top_label.setBuddy(self.top)
        self.left_label.setBuddy(self.left)
        self.right_label.setBuddy(self.right)
        self.bottom_label.setBuddy(self.bottom)
        self.select_file_label.setBuddy(self.select_file)

        self.retranslateUi(dialog)
        QtCore.QObject.connect(self.yes_no_box, QtCore.SIGNAL(_fromUtf8("accepted()")), dialog.accept)
        QtCore.QObject.connect(self.yes_no_box, QtCore.SIGNAL(_fromUtf8("rejected()")), dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(dialog)

        # set up handlers
        self.yes_no_box.accepted.connect(lambda: InfoCubeProcessForm.ok_clicked(self))
        self.yes_no_box.rejected.connect(lambda: InfoCubeProcessForm.cancel_clicked(self))
        self.save_settings_button.clicked.connect(lambda: InfoCubeProcessForm.save_settings_clicked(self))
        self.load_settings_button.clicked.connect(lambda: InfoCubeProcessForm.load_settings_clicked(self))
        self.select_file_button.clicked.connect(lambda: InfoCubeProcessForm.select_file_clicked(self))

        QtCore.QMetaObject.connectSlotsByName(dialog)

        InfoCubeProcessForm.load_settings(self)

    def retranslateUi(self, DGConnect):
        DGConnect.setWindowTitle(_translate("DGConnect", "DGConnect", None))
        self.username_label.setText(_translate("DGConnect", "Username", None))
        self.password_label.setText(_translate("DGConnect", "Password", None))
        self.client_id_label.setText(_translate("DGConnect", "Client ID", None))
        self.client_secret_label.setText(_translate("DGConnect", "Client Secret", None))
        self.select_file_button.setText(_translate("DGConnect", "Select", None))
        self.load_settings_button.setText(_translate("DGConnect", "Load Settings", None))
        self.save_settings_button.setText(_translate("DGConnect", "Save Settings", None))
        self.top_label.setText(_translate("DGConnect", "Top", None))
        self.left_label.setText(_translate("DGConnect", "Left", None))
        self.right_label.setText(_translate("DGConnect", "Right", None))
        self.bottom_label.setText(_translate("DGConnect", "Bottom", None))
        self.select_file_label.setText(_translate("DGConnect", "Output File", None))

    @pyqtSlot(str)
    def on_new_top(self, new_top):
        if self.top.text() != new_top:
            self.top.setText(new_top)

    @pyqtSlot(str)
    def on_new_bottom(self, new_bottom):
        if self.bottom.text() != new_bottom:
            self.bottom.setText(new_bottom)

    @pyqtSlot(str)
    def on_new_left(self, new_left):
        if self.left.text() != new_left:
            self.left.setText(new_left)

    @pyqtSlot(str)
    def on_new_right(self, new_right):
        if self.right.text() != new_right:
            self.right.setText(new_right)

    @pyqtSlot(str)
    def show_complete_message(self, file_name):
        self.csv_generator = None
        message = QMessageBox()
        message.information(None, "CSV Write Complete", "CSV output to " + file_name + " is complete")
        self.dialog.show()


