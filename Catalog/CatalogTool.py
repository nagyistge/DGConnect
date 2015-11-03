# -*- coding: utf-8 -*-
from PyQt4.QtCore import QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon
from ..BBox.BBoxTool import BBoxTool
from CatalogDialog import CatalogDialog
from CatalogDialogTool import CatalogDialogTool
from PyQt4.QtCore import Qt
import os.path


class CatalogTool:
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
        self.dialog = CatalogDialog(self.iface.mainWindow())
        self.iface.addDockWidget(Qt.BottomDockWidgetArea, self.dialog)

        self.dialog_tool = CatalogDialogTool(self.iface, self.dialog.dialog_ui, self.bbox_tool)

    def unload(self):
        self.bbox_tool.reset()
        self.dialog.close()
        # remove the tool
        self.iface.mapCanvas().unsetMapTool(self.bbox_tool)

    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dialog.show()
