# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GBDX
                                 A QGIS plugin
 GBDX is a DigitalGlobe platform enabling data search, download and analytics capabilities for vector and raster commercial, open source and proprietary data sources.  
                             -------------------
        begin                : 2015-09-08
        copyright            : (C) 2015 by Michael Trotter/DigitalGlobe, Inc.
        email                : michael.trotter@digitalglobe.com
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
    """Load GBDX class from file GBDX.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .GBDX import GBDX
    return GBDX(iface)
