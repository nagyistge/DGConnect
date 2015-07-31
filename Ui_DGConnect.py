# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Ui_DGConnect.ui'
#
# Created: Fri Jul 31 12:53:06 2015
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui
from qgis.core import QgsProject
from os.path import expanduser

# constants for plugin settings
PLUGIN_NAME = "DGConnect"
GDB_USERNAME = "gdb.username"
GDB_PASSWORD = "gdb.password"
GDB_API_KEY = "gdb.api.key"
INSIGHTCLOUD_USERNAME = "insightcloud.username"
INSIGHTCLOUD_PASSWORD = "insightcloud.password"
SELECT_FILE = "select.file"

# file filter
DEFAULT_SUFFIX = "csv"
SELECT_FILTER = "CSV Files(*.csv)"

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
        self.ui = None

    def setupUi(self, dialog):
        dialog.setObjectName(_fromUtf8("DGConnect"))
        dialog.resize(918, 221)

        self.ui = dialog

        self.formLayout = QtGui.QFormLayout(dialog)
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.gdb_username_label = QtGui.QLabel(dialog)
        self.gdb_username_label.setObjectName(_fromUtf8("gdb_username_label"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.gdb_username_label)
        self.gdb_username = QtGui.QLineEdit(dialog)
        self.gdb_username.setObjectName(_fromUtf8("gdb_username"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.gdb_username)
        self.gdb_password_label = QtGui.QLabel(dialog)
        self.gdb_password_label.setObjectName(_fromUtf8("gdb_password_label"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.gdb_password_label)
        self.gdb_password = QtGui.QLineEdit(dialog)
        self.gdb_password.setObjectName(_fromUtf8("gdb_password"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.gdb_password)
        self.gdb_api_key_label = QtGui.QLabel(dialog)
        self.gdb_api_key_label.setObjectName(_fromUtf8("gdb_api_key_label"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.gdb_api_key_label)
        self.gdb_api_key = QtGui.QLineEdit(dialog)
        self.gdb_api_key.setObjectName(_fromUtf8("gdb_api_key"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.gdb_api_key)
        self.insightcloud_username_label = QtGui.QLabel(dialog)
        self.insightcloud_username_label.setObjectName(_fromUtf8("insightcloud_username_label"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.LabelRole, self.insightcloud_username_label)
        self.insightcloud_username = QtGui.QLineEdit(dialog)
        self.insightcloud_username.setObjectName(_fromUtf8("insightcloud_username"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.FieldRole, self.insightcloud_username)
        self.insightcloud_password_label = QtGui.QLabel(dialog)
        self.insightcloud_password_label.setObjectName(_fromUtf8("insightcloud_password_label"))
        self.formLayout.setWidget(4, QtGui.QFormLayout.LabelRole, self.insightcloud_password_label)
        self.insightcloud_password = QtGui.QLineEdit(dialog)
        self.insightcloud_password.setObjectName(_fromUtf8("insightcloud_password"))
        self.formLayout.setWidget(4, QtGui.QFormLayout.FieldRole, self.insightcloud_password)
        self.select_file_label = QtGui.QLabel(dialog)
        self.select_file_label.setObjectName(_fromUtf8("select_file_label"))
        self.formLayout.setWidget(5, QtGui.QFormLayout.LabelRole, self.select_file_label)
        self.select_file_layout = QtGui.QHBoxLayout()
        self.select_file_layout.setObjectName(_fromUtf8("select_file_layout"))
        self.select_file = QtGui.QLineEdit(dialog)
        self.select_file.setObjectName(_fromUtf8("select_file"))
        self.select_file_layout.addWidget(self.select_file)
        self.select_file_button = QtGui.QPushButton(dialog)
        self.select_file_button.setObjectName(_fromUtf8("select_file_button"))
        self.select_file_layout.addWidget(self.select_file_button)
        self.formLayout.setLayout(5, QtGui.QFormLayout.FieldRole, self.select_file_layout)
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
        self.formLayout.setLayout(6, QtGui.QFormLayout.LabelRole, self.settings_layout)
        self.line = QtGui.QFrame(dialog)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.formLayout.setWidget(8, QtGui.QFormLayout.SpanningRole, self.line)
        self.line_2 = QtGui.QFrame(dialog)
        self.line_2.setFrameShape(QtGui.QFrame.HLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName(_fromUtf8("line_2"))
        self.formLayout.setWidget(14, QtGui.QFormLayout.SpanningRole, self.line_2)
        self.yes_no_box = QtGui.QDialogButtonBox(dialog)
        self.yes_no_box.setOrientation(QtCore.Qt.Horizontal)
        self.yes_no_box.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.yes_no_box.setObjectName(_fromUtf8("yes_no_box"))
        self.formLayout.setWidget(15, QtGui.QFormLayout.FieldRole, self.yes_no_box)
        self.bbox_layout = QtGui.QGridLayout()
        self.bbox_layout.setContentsMargins(-1, -1, -1, 0)
        self.bbox_layout.setHorizontalSpacing(6)
        self.bbox_layout.setObjectName(_fromUtf8("bbox_layout"))
        spacer_item = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.bbox_layout.addItem(spacer_item, 0, 2, 1, 1)
        self.top_layout = QtGui.QHBoxLayout()
        self.top_layout.setContentsMargins(0, -1, -1, -1)
        self.top_layout.setObjectName(_fromUtf8("top_layout"))
        self.top_label = QtGui.QLabel(dialog)
        self.top_label.setObjectName(_fromUtf8("top_label"))
        self.top_layout.addWidget(self.top_label)
        self.top = QtGui.QLineEdit(dialog)
        self.top.setReadOnly(True)
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
        self.left.setReadOnly(True)
        self.left.setObjectName(_fromUtf8("left"))
        self.left_layout.addWidget(self.left)
        self.bbox_layout.addLayout(self.left_layout, 1, 0, 1, 1)
        self.right_layout = QtGui.QHBoxLayout()
        self.right_layout.setObjectName(_fromUtf8("right_layout"))
        self.right_label = QtGui.QLabel(dialog)
        self.right_label.setObjectName(_fromUtf8("right_label"))
        self.right_layout.addWidget(self.right_label)
        self.right = QtGui.QLineEdit(dialog)
        self.right.setReadOnly(True)
        self.right.setObjectName(_fromUtf8("right"))
        self.right_layout.addWidget(self.right)
        self.bbox_layout.addLayout(self.right_layout, 1, 2, 1, 1)
        spacer_item_1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.bbox_layout.addItem(spacer_item_1, 0, 0, 1, 1)
        spacer_item_2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.bbox_layout.addItem(spacer_item_2, 1, 1, 1, 1)
        self.bottom_layout = QtGui.QHBoxLayout()
        self.bottom_layout.setContentsMargins(-1, -1, -1, 0)
        self.bottom_layout.setObjectName(_fromUtf8("bottom_layout"))
        self.bottom_label = QtGui.QLabel(dialog)
        self.bottom_label.setObjectName(_fromUtf8("bottom_label"))
        self.bottom_layout.addWidget(self.bottom_label)
        self.bottom = QtGui.QLineEdit(dialog)
        self.bottom.setReadOnly(True)
        self.bottom.setObjectName(_fromUtf8("bottom"))
        self.bottom_layout.addWidget(self.bottom)
        self.bbox_layout.addLayout(self.bottom_layout, 2, 1, 1, 1)
        self.formLayout.setLayout(12, QtGui.QFormLayout.SpanningRole, self.bbox_layout)

        self.retranslateUi(dialog)
        QtCore.QObject.connect(self.yes_no_box, QtCore.SIGNAL(_fromUtf8("accepted()")), dialog.accept)
        QtCore.QObject.connect(self.yes_no_box, QtCore.SIGNAL(_fromUtf8("rejected()")), dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(dialog)

        # set up handlers
        self.yes_no_box.accepted.connect(self.ok_clicked)
        self.yes_no_box.rejected.connect(self.cancel_clicked)
        self.save_settings_button.clicked.connect(self.save_settings_clicked)
        self.load_settings_button.clicked.connect(self.load_settings_clicked)
        self.select_file_button.clicked.connect(self.select_file_clicked)

        QtCore.QMetaObject.connectSlotsByName(dialog)

    def retranslateUi(self, DGConnect):
        DGConnect.setWindowTitle(_translate("DGConnect", "DGConnect", None))
        self.gdb_username_label.setText(_translate("DGConnect", "GDB Username", None))
        self.gdb_password_label.setText(_translate("DGConnect", "GDB Password", None))
        self.gdb_api_key_label.setText(_translate("DGConnect", "GDB API Key", None))
        self.insightcloud_username_label.setText(_translate("DGConnect", "InsightCloud Username", None))
        self.insightcloud_password_label.setText(_translate("DGConnect", "InsightCloud Password", None))
        self.select_file_label.setText(_translate("DGConnect", "Output File", None))
        self.select_file_button.setText(_translate("DGConnect", "Select", None))
        self.load_settings_button.setText(_translate("DGConnect", "Load Settings", None))
        self.save_settings_button.setText(_translate("DGConnect", "Save Settings", None))
        self.top_label.setText(_translate("DGConnect", "Top\t", None))
        self.left_label.setText(_translate("DGConnect", "Left", None))
        self.right_label.setText(_translate("DGConnect", "Right", None))
        self.bottom_label.setText(_translate("DGConnect", "Bottom", None))

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

        self.select_file.setText(proj.readEntry(PLUGIN_NAME, SELECT_FILE)[0])

    def save_settings_clicked(self):
        proj = QgsProject.instance()

        # store values
        proj.writeEntry(PLUGIN_NAME, GDB_API_KEY, self.gdb_api_key.text())
        proj.writeEntry(PLUGIN_NAME, GDB_USERNAME, self.gdb_username.text())
        proj.writeEntry(PLUGIN_NAME, GDB_PASSWORD, self.gdb_password.text())

        proj.writeEntry(PLUGIN_NAME, INSIGHTCLOUD_USERNAME, self.insightcloud_username.text())
        proj.writeEntry(PLUGIN_NAME, INSIGHTCLOUD_PASSWORD, self.insightcloud_password.text())

        proj.writeEntry(PLUGIN_NAME, SELECT_FILE, self.select_file.text())

    def select_file_clicked(self):
        # open file dialog
        file_dialog = QtGui.QFileDialog()
        file_name = file_dialog.getSaveFileName(None, "Choose output file", str(expanduser("~")), SELECT_FILTER)
        self.select_file.setText(file_name)

    def set_top_text(self, text):
        self.top.setText(text)

    def set_left_text(self, text):
        self.left.setText(text)

    def set_right_text(self, text):
        self.right.setText(text)

    def set_bottom_text(self, text):
        self.bottom.setText(text)




