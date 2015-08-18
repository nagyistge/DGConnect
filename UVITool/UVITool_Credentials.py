# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'UVITool_Credentials.ui'
#
# Created: Mon Aug 17 13:51:16 2015
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
        Dialog.resize(761, 171)
        Dialog.setModal(False)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(410, 120, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.formLayoutWidget = QtGui.QWidget(Dialog)
        self.formLayoutWidget.setGeometry(QtCore.QRect(20, 30, 731, 71))
        self.formLayoutWidget.setObjectName(_fromUtf8("formLayoutWidget"))
        self.formLayout = QtGui.QFormLayout(self.formLayoutWidget)
        self.formLayout.setMargin(0)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.username_label = QtGui.QLabel(self.formLayoutWidget)
        self.username_label.setObjectName(_fromUtf8("username_label"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.username_label)
        self.username = QtGui.QLineEdit(self.formLayoutWidget)
        self.username.setObjectName(_fromUtf8("username"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.username)
        self.password_label = QtGui.QLabel(self.formLayoutWidget)
        self.password_label.setObjectName(_fromUtf8("password_label"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.password_label)
        self.password = QtGui.QLineEdit(self.formLayoutWidget)
        self.password.setObjectName(_fromUtf8("password"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.password)
        self.horizontalLayoutWidget = QtGui.QWidget(Dialog)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(20, 110, 201, 51))
        self.horizontalLayoutWidget.setObjectName(_fromUtf8("horizontalLayoutWidget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.validate_button = QtGui.QPushButton(self.horizontalLayoutWidget)
        self.validate_button.setObjectName(_fromUtf8("validate_button"))
        self.horizontalLayout.addWidget(self.validate_button)
        self.save_button = QtGui.QPushButton(self.horizontalLayoutWidget)
        self.save_button.setDefault(True)
        self.save_button.setObjectName(_fromUtf8("save_button"))
        self.horizontalLayout.addWidget(self.save_button)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Credentials", None))
        self.username_label.setText(_translate("Dialog", "Username", None))
        self.password_label.setText(_translate("Dialog", "Password", None))
        self.validate_button.setText(_translate("Dialog", "Validate", None))
        self.save_button.setText(_translate("Dialog", "Save", None))

