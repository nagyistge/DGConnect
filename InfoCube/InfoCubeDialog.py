"""
/***************************************************************************
Name			 	 : InfoCube plugin
Description          : Queries the GBD catalog and the Vector index
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
from PyQt4 import QtCore, QtGui
from Ui_InfoCube import Ui_InfoCube
# create the dialog for DGConnect
class InfoCubeDialog(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        # Set up the user interface from Designer.
        self.ui = Ui_InfoCube()
        self.ui.setupUi(self)
        self.bbox = None
        self.message_bar = None
