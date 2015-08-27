# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'UVITool_BBox.ui'
#
# Created: Thu Aug 27 13:50:16 2015
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import pyqtSlot

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

class Ui_DockWidget(object):
    def setupUi(self, DockWidget):
        DockWidget.setObjectName(_fromUtf8("DockWidget"))
        DockWidget.resize(776, 252)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(DockWidget.sizePolicy().hasHeightForWidth())
        DockWidget.setSizePolicy(sizePolicy)
        self.dockWidgetContents = QtGui.QWidget()
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dockWidgetContents.sizePolicy().hasHeightForWidth())
        self.dockWidgetContents.setSizePolicy(sizePolicy)
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.gridLayout_4 = QtGui.QGridLayout(self.dockWidgetContents)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.line = QtGui.QFrame(self.dockWidgetContents)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.gridLayout.addWidget(self.line, 2, 0, 1, 1)
        self.line_2 = QtGui.QFrame(self.dockWidgetContents)
        self.line_2.setFrameShape(QtGui.QFrame.HLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName(_fromUtf8("line_2"))
        self.gridLayout.addWidget(self.line_2, 4, 0, 1, 1)
        self.bbox_layout = QtGui.QGridLayout()
        self.bbox_layout.setSizeConstraint(QtGui.QLayout.SetMinimumSize)
        self.bbox_layout.setContentsMargins(-1, -1, -1, 0)
        self.bbox_layout.setHorizontalSpacing(6)
        self.bbox_layout.setObjectName(_fromUtf8("bbox_layout"))
        self.gridLayout_3 = QtGui.QGridLayout()
        self.gridLayout_3.setContentsMargins(0, -1, -1, -1)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.top_label = QtGui.QLabel(self.dockWidgetContents)
        self.top_label.setObjectName(_fromUtf8("top_label"))
        self.gridLayout_3.addWidget(self.top_label, 0, 0, 1, 1)
        self.top = QtGui.QLineEdit(self.dockWidgetContents)
        self.top.setMinimumSize(QtCore.QSize(125, 0))
        self.top.setReadOnly(False)
        self.top.setObjectName(_fromUtf8("top"))
        self.gridLayout_3.addWidget(self.top, 0, 1, 1, 1)
        self.bbox_layout.addLayout(self.gridLayout_3, 0, 1, 1, 1)
        self.left_layout = QtGui.QHBoxLayout()
        self.left_layout.setContentsMargins(-1, -1, -1, 0)
        self.left_layout.setObjectName(_fromUtf8("left_layout"))
        self.left_label = QtGui.QLabel(self.dockWidgetContents)
        self.left_label.setObjectName(_fromUtf8("left_label"))
        self.left_layout.addWidget(self.left_label)
        self.left = QtGui.QLineEdit(self.dockWidgetContents)
        self.left.setMinimumSize(QtCore.QSize(125, 0))
        self.left.setReadOnly(False)
        self.left.setObjectName(_fromUtf8("left"))
        self.left_layout.addWidget(self.left)
        self.bbox_layout.addLayout(self.left_layout, 1, 0, 1, 1)
        self.right_layout = QtGui.QHBoxLayout()
        self.right_layout.setObjectName(_fromUtf8("right_layout"))
        self.right_label = QtGui.QLabel(self.dockWidgetContents)
        self.right_label.setObjectName(_fromUtf8("right_label"))
        self.right_layout.addWidget(self.right_label)
        self.right = QtGui.QLineEdit(self.dockWidgetContents)
        self.right.setMinimumSize(QtCore.QSize(125, 0))
        self.right.setReadOnly(False)
        self.right.setObjectName(_fromUtf8("right"))
        self.right_layout.addWidget(self.right)
        self.bbox_layout.addLayout(self.right_layout, 1, 2, 1, 1)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.bbox_layout.addItem(spacerItem, 0, 0, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.bbox_layout.addItem(spacerItem1, 1, 1, 1, 1)
        self.bottom_layout = QtGui.QHBoxLayout()
        self.bottom_layout.setContentsMargins(-1, -1, -1, 0)
        self.bottom_layout.setObjectName(_fromUtf8("bottom_layout"))
        self.bottom_label = QtGui.QLabel(self.dockWidgetContents)
        self.bottom_label.setObjectName(_fromUtf8("bottom_label"))
        self.bottom_layout.addWidget(self.bottom_label)
        self.bottom = QtGui.QLineEdit(self.dockWidgetContents)
        self.bottom.setMinimumSize(QtCore.QSize(125, 0))
        self.bottom.setReadOnly(False)
        self.bottom.setObjectName(_fromUtf8("bottom"))
        self.bottom_layout.addWidget(self.bottom)
        self.bbox_layout.addLayout(self.bottom_layout, 2, 1, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.bbox_layout.addItem(spacerItem2, 0, 2, 1, 1)
        spacerItem3 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.bbox_layout.addItem(spacerItem3, 2, 0, 1, 1)
        spacerItem4 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.bbox_layout.addItem(spacerItem4, 2, 2, 1, 1)
        self.gridLayout.addLayout(self.bbox_layout, 1, 0, 1, 1)
        self.formLayout_2 = QtGui.QFormLayout()
        self.formLayout_2.setSizeConstraint(QtGui.QLayout.SetNoConstraint)
        self.formLayout_2.setContentsMargins(-1, -1, -1, 0)
        self.formLayout_2.setObjectName(_fromUtf8("formLayout_2"))
        self.query_label = QtGui.QLabel(self.dockWidgetContents)
        self.query_label.setObjectName(_fromUtf8("query_label"))
        self.formLayout_2.setWidget(0, QtGui.QFormLayout.LabelRole, self.query_label)
        self.query = QtGui.QLineEdit(self.dockWidgetContents)
        self.query.setObjectName(_fromUtf8("query"))
        self.formLayout_2.setWidget(0, QtGui.QFormLayout.FieldRole, self.query)
        self.gridLayout.addLayout(self.formLayout_2, 3, 0, 1, 1)
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setContentsMargins(-1, -1, -1, 0)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        spacerItem5 = QtGui.QSpacerItem(300, 20, QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem5, 0, 1, 1, 1)
        self.search_button = QtGui.QPushButton(self.dockWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.search_button.sizePolicy().hasHeightForWidth())
        self.search_button.setSizePolicy(sizePolicy)
        self.search_button.setDefault(True)
        self.search_button.setObjectName(_fromUtf8("search_button"))
        self.gridLayout_2.addWidget(self.search_button, 0, 2, 1, 1)
        self.settings_button = QtGui.QPushButton(self.dockWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.settings_button.sizePolicy().hasHeightForWidth())
        self.settings_button.setSizePolicy(sizePolicy)
        self.settings_button.setObjectName(_fromUtf8("settings_button"))
        self.gridLayout_2.addWidget(self.settings_button, 0, 0, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_2, 5, 0, 1, 1)
        self.gridLayout_4.addLayout(self.gridLayout, 0, 0, 1, 1)
        DockWidget.setWidget(self.dockWidgetContents)
        self.top_label.setBuddy(self.top)
        self.left_label.setBuddy(self.left)
        self.right_label.setBuddy(self.right)
        self.bottom_label.setBuddy(self.bottom)

        self.retranslateUi(DockWidget)
        QtCore.QMetaObject.connectSlotsByName(DockWidget)

    def retranslateUi(self, DockWidget):
        DockWidget.setWindowTitle(_translate("DockWidget", "BBox", None))
        self.top_label.setText(_translate("DockWidget", "Top      ", None))
        self.left_label.setText(_translate("DockWidget", "Left", None))
        self.right_label.setText(_translate("DockWidget", "Right", None))
        self.bottom_label.setText(_translate("DockWidget", "Bottom", None))
        self.query_label.setText(_translate("DockWidget", "Query", None))
        self.search_button.setText(_translate("DockWidget", "Search", None))
        self.settings_button.setText(_translate("DockWidget", "Settings", None))

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