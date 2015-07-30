# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file Ui_DGConnect.ui
# Created with: PyQt4 UI code generator 4.4.4
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui


class Ui_DGConnect(object):
    def setupUi(self, DGConnect):
        DGConnect.setObjectName("DGConnect")
        DGConnect.resize(400, 300)
        self.buttonBox = QtGui.QDialogButtonBox(DGConnect)
        self.buttonBox.setGeometry(QtCore.QRect(30, 240, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")

        self.retranslateUi(DGConnect)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), DGConnect.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), DGConnect.reject)
        QtCore.QMetaObject.connectSlotsByName(DGConnect)

    def retranslateUi(self, DGConnect):
        DGConnect.setWindowTitle(
            QtGui.QApplication.translate("DGConnect", "DGConnect", None, QtGui.QApplication.UnicodeUTF8))
