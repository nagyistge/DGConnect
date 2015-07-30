# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Ui_DGConnect.ui'
#
# Created: Thu Jul 30 15:45:49 2015
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui
from qgis.core import QgsProject

# constants for plugin settings
PLUGIN_NAME = "DGConnect"
GDB_USERNAME = "gdb.username"
GDB_PASSWORD = "gdb.password"
GDB_API_KEY = "gdb.api.key"
INSIGHTCLOUD_USERNAME = "insightcloud.username"
INSIGHTCLOUD_PASSWORD = "insightcloud.password"

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


class Ui_DGConnect(object):

    def __init__(self):
        self.formLayout = None
        self.gdb_api_key = None
        self.gdb_api_key_label = None
        self.gdb_password = None
        self.gdb_password_label = None
        self.gdb_username = None
        self.gdb_username_label = None
        self.insightcloud_password = None
        self.insightcloud_password_label = None
        self.insightcloud_username = None
        self.insightcloud_username_label = None
        self.load_settings_button = None
        self.yes_no_box = None
        self.save_settings_button = None
        self.settings_layout = None
        self.ui = None

    def setupUi(self, DGConnect):
        DGConnect.setObjectName(_fromUtf8("DGConnect"))
        DGConnect.resize(918, 221)

        self.ui = DGConnect

        self.formLayout = QtGui.QFormLayout(DGConnect)
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.gdb_username_label = QtGui.QLabel(DGConnect)
        self.gdb_username_label.setObjectName(_fromUtf8("gdb_username_label"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.gdb_username_label)
        self.gdb_username = QtGui.QLineEdit(DGConnect)
        self.gdb_username.setObjectName(_fromUtf8("gdb_username"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.gdb_username)
        self.gdb_password_label = QtGui.QLabel(DGConnect)
        self.gdb_password_label.setObjectName(_fromUtf8("gdb_password_label"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.gdb_password_label)
        self.gdb_password = QtGui.QLineEdit(DGConnect)
        self.gdb_password.setObjectName(_fromUtf8("gdb_password"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.gdb_password)
        self.gdb_api_key_label = QtGui.QLabel(DGConnect)
        self.gdb_api_key_label.setObjectName(_fromUtf8("gdb_api_key_label"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.gdb_api_key_label)
        self.gdb_api_key = QtGui.QLineEdit(DGConnect)
        self.gdb_api_key.setObjectName(_fromUtf8("gdb_api_key"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.gdb_api_key)
        self.insightcloud_username_label = QtGui.QLabel(DGConnect)
        self.insightcloud_username_label.setObjectName(_fromUtf8("insightcloud_username_label"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.LabelRole, self.insightcloud_username_label)
        self.insightcloud_username = QtGui.QLineEdit(DGConnect)
        self.insightcloud_username.setObjectName(_fromUtf8("insightcloud_username"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.FieldRole, self.insightcloud_username)
        self.insightcloud_password_label = QtGui.QLabel(DGConnect)
        self.insightcloud_password_label.setObjectName(_fromUtf8("insightcloud_password_label"))
        self.formLayout.setWidget(4, QtGui.QFormLayout.LabelRole, self.insightcloud_password_label)
        self.insightcloud_password = QtGui.QLineEdit(DGConnect)
        self.insightcloud_password.setObjectName(_fromUtf8("insightcloud_password"))
        self.formLayout.setWidget(4, QtGui.QFormLayout.FieldRole, self.insightcloud_password)
        self.yes_no_box = QtGui.QDialogButtonBox(DGConnect)
        self.yes_no_box.setOrientation(QtCore.Qt.Horizontal)
        self.yes_no_box.setStandardButtons(QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Ok)
        self.yes_no_box.setObjectName(_fromUtf8("yes_no_box"))
        self.formLayout.setWidget(5, QtGui.QFormLayout.FieldRole, self.yes_no_box)
        self.settings_layout = QtGui.QHBoxLayout()
        self.settings_layout.setContentsMargins(-1, -1, 0, 0)
        self.settings_layout.setObjectName(_fromUtf8("settings_layout"))
        self.load_settings_button = QtGui.QPushButton(DGConnect)
        self.load_settings_button.setObjectName(_fromUtf8("load_settings_button"))
        self.settings_layout.addWidget(self.load_settings_button)
        self.save_settings_button = QtGui.QPushButton(DGConnect)
        self.save_settings_button.setObjectName(_fromUtf8("save_settings_button"))
        self.settings_layout.addWidget(self.save_settings_button)
        self.formLayout.setLayout(5, QtGui.QFormLayout.LabelRole, self.settings_layout)

        self.retranslateUi(DGConnect)

        # set up handlers
        self.yes_no_box.accepted.connect(self.ok_clicked)
        self.yes_no_box.rejected.connect(self.cancel_clicked)
        self.save_settings_button.clicked.connect(self.save_settings_clicked)
        self.load_settings_button.clicked.connect(self.load_settings_clicked)

        QtCore.QMetaObject.connectSlotsByName(DGConnect)

    def retranslateUi(self, DGConnect):
        DGConnect.setWindowTitle(_translate("DGConnect", "DGConnect", None))
        self.gdb_username_label.setText(_translate("DGConnect", "GDB Username", None))
        self.gdb_password_label.setText(_translate("DGConnect", "GDB Password", None))
        self.gdb_api_key_label.setText(_translate("DGConnect", "GDB API Key", None))
        self.insightcloud_username_label.setText(_translate("DGConnect", "InsightCloud Username", None))
        self.insightcloud_password_label.setText(_translate("DGConnect", "InsightCloud Password", None))
        self.load_settings_button.setText(_translate("DGConnect", "Load Settings", None))
        self.save_settings_button.setText(_translate("DGConnect", "Save Settings", None))

    def ok_clicked(self):
        self.ui.accept()

    def cancel_clicked(self):
        self.ui.reject()

    def load_settings_clicked(self):
        proj = QgsProject.instance()

        # read values
        self.gdb_api_key.setText(proj.readEntry(PLUGIN_NAME, GDB_API_KEY)[0])
        self.gdb_username.setText(proj.readEntry(PLUGIN_NAME, GDB_USERNAME)[0])
        self.gdb_password.setText(proj.readEntry(PLUGIN_NAME, GDB_PASSWORD)[0])

        self.insightcloud_username.setText(proj.readEntry(PLUGIN_NAME, INSIGHTCLOUD_USERNAME)[0])
        self.insightcloud_password.setText(proj.readEntry(PLUGIN_NAME, INSIGHTCLOUD_PASSWORD)[0])

    def save_settings_clicked(self):
        proj = QgsProject.instance()

        # store values
        proj.writeEntry(PLUGIN_NAME, GDB_API_KEY, self.gdb_api_key.text())
        proj.writeEntry(PLUGIN_NAME, GDB_USERNAME, self.gdb_username.text())
        proj.writeEntry(PLUGIN_NAME, GDB_PASSWORD, self.gdb_password.text())

        proj.writeEntry(PLUGIN_NAME, INSIGHTCLOUD_USERNAME, self.insightcloud_username.text())
        proj.writeEntry(PLUGIN_NAME, INSIGHTCLOUD_PASSWORD, self.insightcloud_password.text())




