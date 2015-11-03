# -*- coding: utf-8 -*-
"""
/***************************************************************************
VectorsTool
                                 A QGIS plugin
 Tool for querying vectors
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
from Vectors_dialog import VectorsDialog
from ..BBox.BBoxTool import BBoxTool
from VectorsDialogTool import VectorsDialogTool
from PyQt4.QtCore import Qt
import os.path


class VectorsTool:
    """QGIS Plugin Implementation."""

    def __init__(self, iface, bbox_tool):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        self.bbox_tool = bbox_tool

        # Create the dialog (after translation) and keep reference
        self.dlg = VectorsDialog(self.iface.mainWindow())
        self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dlg)

        self.dialog_tool = VectorsDialogTool(self.iface, self.dlg.dialog_base, self.bbox_tool)

    def unload(self):
        self.bbox_tool.reset()
        self.dlg.close()
        # remove the tool
        self.iface.mapCanvas().unsetMapTool(self.bbox_tool)

    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()


