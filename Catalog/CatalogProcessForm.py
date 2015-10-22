# -*- coding: utf-8 -*-
__author__ = 'mtrotter'


from qgis.gui import QgsMessageBar
from PyQt4 import QtGui
from os.path import expanduser
from ..BBox import BBoxTool
from CatalogGBDQuery import GBDQuery, GBDOrderParams

import re
import os


def search_clicked(dialog_tool, left, right, top, bottom, query=None):
    """
    Action performed when the ok button is clicked
    :param ui: The UI ui where this occurs
    :return: None
    """
    errors = []
    if not BBoxTool.validate_bbox_fields(top=top, bottom=bottom, left=left, right=right, errors=errors):
        dialog_tool.iface.messageBar().pushMessage("ERROR", "The following errors occurred:<br />" +
                                                   "<br />".join(errors),
                                                   level=QgsMessageBar.CRITICAL)
        return
    params = GBDOrderParams(top=top, right=right, bottom=bottom, left=left, time_begin=None, time_end=None)
    dialog_tool.query_catalog(params)
