# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Settings.ui'
#
# Created: Wed Oct 21 15:47:55 2015
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

class Ui_Settings(object):
    def setupUi(self, Settings):
        Settings.setObjectName(_fromUtf8("Settings"))
        Settings.resize(689, 155)
        Settings.setModal(False)
        self.gridLayout = QtGui.QGridLayout(Settings)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.validate_button = QtGui.QPushButton(Settings)
        self.validate_button.setObjectName(_fromUtf8("validate_button"))
        self.horizontalLayout.addWidget(self.validate_button)
        self.save_button = QtGui.QPushButton(Settings)
        self.save_button.setDefault(True)
        self.save_button.setObjectName(_fromUtf8("save_button"))
        self.horizontalLayout.addWidget(self.save_button)
        self.gridLayout.addLayout(self.horizontalLayout, 1, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(Settings)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 1, 1, 1, 1)
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.username_label = QtGui.QLabel(Settings)
        self.username_label.setObjectName(_fromUtf8("username_label"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.username_label)
        self.username = QtGui.QLineEdit(Settings)
        self.username.setObjectName(_fromUtf8("username"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.username)
        self.password_label = QtGui.QLabel(Settings)
        self.password_label.setObjectName(_fromUtf8("password_label"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.password_label)
        self.password = QtGui.QLineEdit(Settings)
        self.password.setEchoMode(QtGui.QLineEdit.Password)
        self.password.setObjectName(_fromUtf8("password"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.password)
        self.api_key_label = QtGui.QLabel(Settings)
        self.api_key_label.setObjectName(_fromUtf8("api_key_label"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.api_key_label)
        self.api_key = QtGui.QLineEdit(Settings)
        self.api_key.setObjectName(_fromUtf8("api_key"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.api_key)
        self.max_items_to_return_label = QtGui.QLabel(Settings)
        self.max_items_to_return_label.setObjectName(_fromUtf8("max_items_to_return_label"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.LabelRole, self.max_items_to_return_label)
        self.max_items_to_return = QtGui.QLineEdit(Settings)
        self.max_items_to_return.setObjectName(_fromUtf8("max_items_to_return"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.FieldRole, self.max_items_to_return)
        self.gridLayout.addLayout(self.formLayout, 0, 0, 1, 2)
        self.max_items_to_return_label.setBuddy(self.max_items_to_return)

        self.retranslateUi(Settings)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Settings.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Settings.reject)
        QtCore.QMetaObject.connectSlotsByName(Settings)
        Settings.setTabOrder(self.validate_button, self.save_button)
        Settings.setTabOrder(self.save_button, self.username)
        Settings.setTabOrder(self.username, self.password)
        Settings.setTabOrder(self.password, self.max_items_to_return)

    def retranslateUi(self, Settings):
        Settings.setWindowTitle(_translate("Settings", "Settings", None))
        self.validate_button.setText(_translate("Settings", "Validate", None))
        self.save_button.setText(_translate("Settings", "Save", None))
        self.username_label.setText(_translate("Settings", "Username", None))
        self.password_label.setText(_translate("Settings", "Password", None))
        self.api_key_label.setText(_translate("Settings", "API Key", None))
        self.max_items_to_return_label.setText(_translate("Settings", "Max Items to Return", None))

