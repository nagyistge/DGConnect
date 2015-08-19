# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'UVITool_dialog_base.ui'
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

class Ui_DockWidget(object):
    def setupUi(self, DockWidget):
        DockWidget.setObjectName(_fromUtf8("DockWidget"))
        DockWidget.resize(496, 958)
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
        self.data_source_group_box = QtGui.QGroupBox(self.dockWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.data_source_group_box.sizePolicy().hasHeightForWidth())
        self.data_source_group_box.setSizePolicy(sizePolicy)
        self.data_source_group_box.setMinimumSize(QtCore.QSize(0, 0))
        self.data_source_group_box.setSizeIncrement(QtCore.QSize(1, 1))
        self.data_source_group_box.setObjectName(_fromUtf8("data_source_group_box"))
        self.gridLayout_2 = QtGui.QGridLayout(self.data_source_group_box)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.data_sources_list_view = QtGui.QListView(self.data_source_group_box)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.data_sources_list_view.sizePolicy().hasHeightForWidth())
        self.data_sources_list_view.setSizePolicy(sizePolicy)
        self.data_sources_list_view.setObjectName(_fromUtf8("data_sources_list_view"))
        self.gridLayout_2.addWidget(self.data_sources_list_view, 0, 0, 1, 1)
        self.verticalLayout.addWidget(self.data_source_group_box)
        self.line = QtGui.QFrame(self.dockWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.line.sizePolicy().hasHeightForWidth())
        self.line.setSizePolicy(sizePolicy)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.verticalLayout.addWidget(self.line)
        self.geometry_group_box = QtGui.QGroupBox(self.dockWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.geometry_group_box.sizePolicy().hasHeightForWidth())
        self.geometry_group_box.setSizePolicy(sizePolicy)
        self.geometry_group_box.setMinimumSize(QtCore.QSize(0, 0))
        self.geometry_group_box.setObjectName(_fromUtf8("geometry_group_box"))
        self.gridLayout_3 = QtGui.QGridLayout(self.geometry_group_box)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.geometry_list_view = QtGui.QListView(self.geometry_group_box)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.geometry_list_view.sizePolicy().hasHeightForWidth())
        self.geometry_list_view.setSizePolicy(sizePolicy)
        self.geometry_list_view.setObjectName(_fromUtf8("geometry_list_view"))
        self.gridLayout_3.addWidget(self.geometry_list_view, 0, 0, 1, 1)
        self.verticalLayout.addWidget(self.geometry_group_box)
        self.line_2 = QtGui.QFrame(self.dockWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.line_2.sizePolicy().hasHeightForWidth())
        self.line_2.setSizePolicy(sizePolicy)
        self.line_2.setFrameShape(QtGui.QFrame.HLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName(_fromUtf8("line_2"))
        self.verticalLayout.addWidget(self.line_2)
        self.types_group_box = QtGui.QGroupBox(self.dockWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.types_group_box.sizePolicy().hasHeightForWidth())
        self.types_group_box.setSizePolicy(sizePolicy)
        self.types_group_box.setObjectName(_fromUtf8("types_group_box"))
        self.gridLayout_4 = QtGui.QGridLayout(self.types_group_box)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.types_list_view = QtGui.QListView(self.types_group_box)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.types_list_view.sizePolicy().hasHeightForWidth())
        self.types_list_view.setSizePolicy(sizePolicy)
        self.types_list_view.setObjectName(_fromUtf8("types_list_view"))
        self.gridLayout_4.addWidget(self.types_list_view, 0, 0, 1, 1)
        self.verticalLayout.addWidget(self.types_group_box)
        self.line_3 = QtGui.QFrame(self.dockWidgetContents)
        self.line_3.setFrameShape(QtGui.QFrame.HLine)
        self.line_3.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_3.setObjectName(_fromUtf8("line_3"))
        self.verticalLayout.addWidget(self.line_3)
        self.button_layout = QtGui.QHBoxLayout()
        self.button_layout.setObjectName(_fromUtf8("button_layout"))
        self.export_button = QtGui.QPushButton(self.dockWidgetContents)
        self.export_button.setDefault(True)
        self.export_button.setObjectName(_fromUtf8("export_button"))
        self.button_layout.addWidget(self.export_button)
        self.verticalLayout.addLayout(self.button_layout)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)
        DockWidget.setWidget(self.dockWidgetContents)

        self.retranslateUi(DockWidget)
        QtCore.QMetaObject.connectSlotsByName(DockWidget)

    def retranslateUi(self, DockWidget):
        DockWidget.setWindowTitle(_translate("DockWidget", "UVITool", None))
        self.data_source_group_box.setTitle(_translate("DockWidget", "Data Sources", None))
        self.geometry_group_box.setTitle(_translate("DockWidget", "Geometry", None))
        self.types_group_box.setTitle(_translate("DockWidget", "Types", None))
        self.export_button.setText(_translate("DockWidget", "Export", None))

