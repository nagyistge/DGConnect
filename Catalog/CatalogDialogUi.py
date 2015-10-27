# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'CatalogDialogUi.ui'
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

class CatalogDialogUi(object):
    def setupUi(self, DockWidget):
        DockWidget.setObjectName(_fromUtf8("DockWidget"))
        DockWidget.resize(496, 320)
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
        self.widget_layout = QtGui.QGridLayout(self.dockWidgetContents)
        self.widget_layout.setObjectName(_fromUtf8("widget_layout"))
        self.tab_widget = QtGui.QTabWidget(self.dockWidgetContents)
        self.tab_widget.setObjectName(_fromUtf8("tab_widget"))
        self.filters_tab = QtGui.QWidget()
        self.filters_tab.setObjectName(_fromUtf8("filters_tab"))
        self.filters_tab_layout = QtGui.QGridLayout(self.filters_tab)
        self.filters_tab_layout.setObjectName(_fromUtf8("filters_tab_layout"))
        self.filters_layout = QtGui.QGridLayout()
        self.filters_layout.setObjectName(_fromUtf8("filters_layout"))
        self.filters_tab_layout.addLayout(self.filters_layout, 0, 1, 1, 1)
        self.tab_widget.addTab(self.filters_tab, _fromUtf8(""))
        self.results_tab = QtGui.QWidget()
        self.results_tab.setObjectName(_fromUtf8("results_tab"))
        self.results_tab_layout = QtGui.QGridLayout(self.results_tab)
        self.results_tab_layout.setObjectName(_fromUtf8("results_tab_layout"))
        self.table_view = QtGui.QTableView(self.results_tab)
        self.table_view.setEnabled(True)
        self.table_view.setSortingEnabled(True)
        self.table_view.setObjectName(_fromUtf8("table_view"))
        self.table_view.horizontalHeader().setCascadingSectionResizes(False)
        self.table_view.horizontalHeader().setStretchLastSection(False)
        self.table_view.verticalHeader().setCascadingSectionResizes(False)
        self.table_view.verticalHeader().setDefaultSectionSize(25)
        self.table_view.verticalHeader().setMinimumSectionSize(25)
        self.table_view.verticalHeader().setSortIndicatorShown(False)
        self.results_tab_layout.addWidget(self.table_view, 0, 0, 1, 1)
        self.tab_widget.addTab(self.results_tab, _fromUtf8(""))
        self.widget_layout.addWidget(self.tab_widget, 0, 0, 1, 1)
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
        self.widget_layout.addLayout(self.button_layout, 1, 0, 1, 1)
        DockWidget.setWidget(self.dockWidgetContents)

        self.retranslateUi(DockWidget)
        self.tab_widget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(DockWidget)

    def retranslateUi(self, DockWidget):
        DockWidget.setWindowTitle(_translate("DockWidget", "DGX Catalog", None))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.filters_tab), _translate("DockWidget", "Filters", None))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.results_tab), _translate("DockWidget", "Results", None))
        self.search_button.setText(_translate("DockWidget", "Search", None))
        self.export_button.setText(_translate("DockWidget", "Export", None))

