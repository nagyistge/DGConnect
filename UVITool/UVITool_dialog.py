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
import UVITool_BBox
import UVITool_dialog_base

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'UVITool_dialog_base.ui'))


class UVIToolDialog(QtGui.QDockWidget, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(UVIToolDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.dialog_base = UVITool_dialog_base.Ui_DockWidget()
        self.setupUi()
        self.bbox_dialog = None

    def setupUi(self):
        self.dialog_base.setupUi(self)

class BBoxDialog(QtGui.QDockWidget, FORM_CLASS):
    def __init__(self, parent=None):
        super(BBoxDialog, self).__init__(parent)
        self.bbox = UVITool_BBox.Ui_DockWidget()
        self.setupUi()
        self.uvi_tool_dialog = None

    def setupUi(self):
        self.bbox.setupUi(self)

