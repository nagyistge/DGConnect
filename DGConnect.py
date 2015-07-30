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
from DGConnectDialog import DGConnectDialog


class DGConnect:
    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        self.action = None

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

    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu("&DGConnect", self.action)
        self.iface.removeToolBarIcon(self.action)

    # run method that performs all the real work
    def run(self):
        # create and show the dialog
        dlg = DGConnectDialog()
        # show the dialog
        dlg.show()
        result = dlg.exec_()
        # See if OK was pressed
        if result == 1:
            # do something useful (delete the line containing pass and
            # substitute with your code
            pass
