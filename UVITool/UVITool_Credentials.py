# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'UVITool_Credentials.ui'
#
# Created: Tue Aug 18 10:32:30 2015
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

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

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(689, 121)
        Dialog.setModal(False)
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.validate_button = QtGui.QPushButton(Dialog)
        self.validate_button.setObjectName(_fromUtf8("validate_button"))
        self.horizontalLayout.addWidget(self.validate_button)
        self.save_button = QtGui.QPushButton(Dialog)
        self.save_button.setDefault(True)
        self.save_button.setObjectName(_fromUtf8("save_button"))
        self.horizontalLayout.addWidget(self.save_button)
        self.gridLayout.addLayout(self.horizontalLayout, 1, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 1, 1, 1, 1)
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.username_label = QtGui.QLabel(Dialog)
        self.username_label.setObjectName(_fromUtf8("username_label"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.username_label)
        self.username = QtGui.QLineEdit(Dialog)
        self.username.setObjectName(_fromUtf8("username"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.username)
        self.password_label = QtGui.QLabel(Dialog)
        self.password_label.setObjectName(_fromUtf8("password_label"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.password_label)
        self.password = QtGui.QLineEdit(Dialog)
        self.password.setObjectName(_fromUtf8("password"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.password)
        self.gridLayout.addLayout(self.formLayout, 0, 0, 1, 2)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Credentials", None))
        self.validate_button.setText(_translate("Dialog", "Validate", None))
        self.save_button.setText(_translate("Dialog", "Save", None))
        self.username_label.setText(_translate("Dialog", "Username", None))
        self.password_label.setText(_translate("Dialog", "Password", None))

