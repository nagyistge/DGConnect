# -*- coding: utf-8 -*-
from PyQt4.QtCore import QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon
# Import the code for the dialog
from ..BBox.BBoxTool import BBoxTool
from CatalogDialog import CatalogDialog
from CatalogDialogTool import CatalogDialogTool
from PyQt4.QtCore import Qt
import os.path


class CatalogTool:
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
        self.dlg = CatalogDialog(self.iface.mainWindow())

        self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dlg)

        self.dialog_tool = CatalogDialogTool(self.iface, self.dlg.dialog_base)
        self.bbox_tool = BBoxTool(self.iface)

    def unload(self):
        self.bbox_tool.reset()
        self.dlg.close()
        # remove the tool
        self.iface.mapCanvas().unsetMapTool(self.bbox_tool)

    def run(self):
        """Run method that performs all the real work"""
        self.iface.mapCanvas().setMapTool(self.bbox_tool)
        # show the dialog
        self.dlg.show()
