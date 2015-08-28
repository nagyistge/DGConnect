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
 This script initializes the plugin, making it known to QGIS.
"""


def name():
    return "DGConnect plugin"


def description():
    return "Queries the GBD catalog and the UVI index"


def version():
    return "Version 0.1"


def qgisMinimumVersion():
    return "1.0"


def classFactory(iface):
    # load DGConnect class from file DGConnect
    from DGConnect import DGConnect
    '''
    Debug settings
    '''
    import sys, os
    sys.path.insert(1, os.path.expanduser('~') + '/pycharm-debug.egg')
    import pydevd
    pydevd.settrace('localhost', port=53100, stdoutToServer=True, stderrToServer=True)

    return DGConnect(iface)
