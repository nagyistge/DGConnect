# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'About.ui'
#
# Created: Tue Sep  8 10:51:14 2015
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

class Ui_AboutDialog(object):
    def setupUi(self, AboutDialog):
        AboutDialog.setObjectName(_fromUtf8("AboutDialog"))
        AboutDialog.resize(400, 300)
        self.textEdit = QtGui.QTextEdit(AboutDialog)
        self.textEdit.setGeometry(QtCore.QRect(10, 20, 371, 251))
        self.textEdit.setObjectName(_fromUtf8("textEdit"))
        self.textEdit.setText("DGX is a DigitalGlobe product enabling data search, download and analytics capabilities"
                              " for vector and raster commercial, open source and proprietary data sources.")

        self.retranslateUi(AboutDialog)
        QtCore.QMetaObject.connectSlotsByName(AboutDialog)

    def retranslateUi(self, AboutDialog):
        AboutDialog.setWindowTitle(_translate("AboutDialog", "About", None))

