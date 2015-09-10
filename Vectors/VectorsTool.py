# -*- coding: utf-8 -*-
"""
/***************************************************************************
VectorsTool
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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon
# Import the code for the dialog
from Vectors_dialog import VectorsDialog, VectorsBBoxDialog
from VectorsBBoxTool import VectorsBBoxTool
from VectorsDialogTool import VectorsDialogTool
from PyQt4.QtCore import Qt
import os.path


class VectorsTool:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface

        # Create the dialog (after translation) and keep reference
        self.dlg = VectorsDialog(self.iface.mainWindow())
        self.bbox_dlg = VectorsBBoxDialog(self.dlg)
        self.dlg.bbox_dialog = self.bbox_dlg
        self.bbox_dlg.uvi_tool_dialog = self.dlg

        self.iface.addDockWidget(Qt.RightDockWidgetArea, self.bbox_dlg)
        self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.dlg)

        self.bbox_tool = VectorsBBoxTool(self.iface, self.bbox_dlg.bbox)
        self.dialog_tool = VectorsDialogTool(self.iface, self.bbox_dlg.bbox, self.dlg.dialog_base)
        self.bbox_tool.dialog_tool = self.dialog_tool

    def unload(self):
        self.bbox_tool.reset()
        self.dlg.close()
        self.bbox_dlg.close()
        # remove the tool
        self.iface.mapCanvas().unsetMapTool(self.bbox_tool)

    def run(self):
        """Run method that performs all the real work"""
        self.iface.mapCanvas().setMapTool(self.bbox_tool)
        # show the dialog
        self.dlg.show()
        self.bbox_dlg.show()


