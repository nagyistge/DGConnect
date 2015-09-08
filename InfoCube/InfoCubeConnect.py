"""
/***************************************************************************
Name			 	 : DGConnect plugin
Description          : Queries the GBD catalog and the UVI index
Date                 : 30/Jul/15 
copyright            : (C) 2015 by Michael Trotter/DigitalGlobe
email                : michael.trotter@digitalglobe.com 
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
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from InfoCubeDialog import InfoCubeDialog
from InfoCubeBBoxTool import InfoCubeBBoxTool


class InfoCubeConnect:
    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        self.action = None
        self.dlg = None
        self.bbox = None

    def initGui(self):
        # Create action that will start plugin configuration
        self.action = QAction(QIcon(":/plugins/DGConnect/icon.png"),
                              "DGConnect", self.iface.mainWindow())
        self.action.setObjectName("DGConnect")
        self.action.setWhatsThis("Query GBD and UVI for data")
        self.action.setIconVisibleInMenu(True)
        # connect the action to the run method
        QObject.connect(self.action, SIGNAL("activated()"), self.run)

        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu("&DGConnect", self.action)

        # create and show the dialog
        self.dlg = InfoCubeDialog()
        self.dlg.message_bar = self.iface.messageBar()

        # create the bbox tool
        self.bbox = InfoCubeBBoxTool(self.iface.mapCanvas(), self.dlg)

    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu("&DGConnect", self.action)
        self.iface.removeToolBarIcon(self.action)
        self.bbox.reset()

        # remove the bbox
        self.iface.mapCanvas().unsetMapTool(self.bbox)

    # run method that performs all the real work
    def run(self):
        # add the bbox
        self.iface.mapCanvas().setMapTool(self.bbox)
        # show the dialog
        self.dlg.show()
        self.dlg.exec_()
