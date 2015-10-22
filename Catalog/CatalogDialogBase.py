# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'CatalogDialogBase.ui'
#
# Created: Wed Aug 19 13:37:15 2015
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

class Ui_CatalogDialog(object):
    def setupUi(self, DockWidget):
        DockWidget.setObjectName(_fromUtf8("DockWidget"))
        DockWidget.resize(496, 541)
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
        self.gridLayout = QtGui.QGridLayout(self.dockWidgetContents)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setSizeConstraint(QtGui.QLayout.SetNoConstraint)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.button_layout = QtGui.QHBoxLayout()
        self.button_layout.setObjectName(_fromUtf8("button_layout"))
        self.search_button = QtGui.QPushButton(self.dockWidgetContents)
        self.search_button.setDefault(True)
        self.search_button.setObjectName(_fromUtf8("search_button"))
        self.button_layout.addWidget(self.search_button)
        self.export_button = QtGui.QPushButton(self.dockWidgetContents)
        self.export_button.setDefault(True)
        self.export_button.setObjectName(_fromUtf8("export_button"))
        self.button_layout.addWidget(self.export_button)
        self.verticalLayout.addLayout(self.button_layout)
        self.gridLayout.addLayout(self.verticalLayout, 1, 0, 1, 1)
        self.table_view = QtGui.QTableView(self.dockWidgetContents)
        self.table_view.setObjectName(_fromUtf8("table_view"))
        self.gridLayout.addWidget(self.table_view, 0, 0, 1, 1)
        DockWidget.setWidget(self.dockWidgetContents)

        self.retranslateUi(DockWidget)
        QtCore.QMetaObject.connectSlotsByName(DockWidget)

    def retranslateUi(self, DockWidget):
        DockWidget.setWindowTitle(_translate("DockWidget", "DGX Catalog", None))
        self.search_button.setText(_translate("DockWidget", "Search", None))
        self.export_button.setText(_translate("DockWidget", "Export", None))
