# -*- coding: utf-8 -*-
"""
/***************************************************************************
 UVITool
                                 A QGIS plugin
 Tool for querying the UVI
                             -------------------
        begin                : 2015-08-17
        copyright            : (C) 2015 by Michael Trotter/DigitalGlobe, Inc.
        email                : Michael.Trotter@digitalglobe.com
        git sha              : $Format:%H$
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


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load UVITool class from file UVITool.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .UVITool import UVITool
    '''
    Debug settings
    import sys
    sys.path.insert(1, '/home/mtrotter/pycharm-debug.egg')
    import pydevd
    pydevd.settrace('localhost', port=53100, stdoutToServer=True, stderrToServer=True)
    '''
    return UVITool(iface)
