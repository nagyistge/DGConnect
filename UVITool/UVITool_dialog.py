# -*- coding: utf-8 -*-
"""
/***************************************************************************
 UVIToolDialog
                                 A QGIS plugin
 Tool for querying the UVI
                             -------------------
        begin                : 2015-08-17
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Michael Trotter/DigitalGlobe, Inc.
        email                : Michael.Trotter@digitalglobe.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os

from PyQt4 import QtGui, uic
from UVITool_BBox import Ui_BBox
from UVITool_dialog_base import Ui_UVIToolDialogBase

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'UVITool_dialog_base.ui'))


class UVIToolDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(UVIToolDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.dialog_base = Ui_UVIToolDialogBase()
        self.setupUi()
        self.bbox_dialog = None
        current_pos = self.pos()
        desktop = QtGui.QApplication.instance().desktop()
        rect = desktop.screenGeometry(desktop.screenNumber(QtGui.QCursor.pos()))
        dest_width = rect.width()
        widget_width = self.width()
        self.move(dest_width / desktop.numScreens() - 1.5 * widget_width + rect.left(), current_pos.y())

    def setupUi(self):
        self.dialog_base.setupUi(self)

class BBoxDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super(BBoxDialog, self).__init__(parent)
        self.bbox = Ui_BBox()
        self.setupUi()
        self.uvi_tool_dialog = None
        current_pos = self.pos()
        desktop = QtGui.QApplication.instance().desktop()
        rect = desktop.screenGeometry(desktop.screenNumber(QtGui.QCursor.pos()))
        dest_width = rect.width()
        widget_width = self.width()
        self.move(dest_width / desktop.numScreens() - 1.5 * widget_width + rect.right(), current_pos.y())

    def setupUi(self):
        self.bbox.setupUi(self)

