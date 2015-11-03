# -*- coding: utf-8 -*-
__author__ = 'mtrotter'


from qgis.gui import QgsMessageBar
from PyQt4 import QtGui
from PyQt4.QtCore import QSettings
from os.path import expanduser
from VectorsInsightCloudQuery import InsightCloudQuery, InsightCloudSourcesParams
from ..Settings import SettingsOps
from ..BBox import BBoxTool

import re
import os

SELECT_FILE = "select.file"

# file filter
DEFAULT_SUFFIX = "csv"
SELECT_FILTER = "CSV Files(*.csv)"

# simple regex validator for data; make sure there's something there
ENDS_WITH_SUFFIX_REGEX = re.compile(".+\." + DEFAULT_SUFFIX + "$")


def select_file_clicked(ui):
    """
    Action performed when the Select button is clicked; Opens a File dialog
    :param ui: The GUI object to update with the path
    :return: None
    """
    # open file ui
    file_ui = QtGui.QFileDialog()
    file_name = file_ui.getSaveFileName(None, "Choose output file", str(expanduser("~")), SELECT_FILTER)
    ui.select_file.setText(file_name)

def validate_stored_settings(iface, username, password, client_id, client_secret, max_items_to_return):
    """
    Validates the settings in the stored settings
    :param iface: QGIS interface to push messages to
    :param username: Username for OAuth2 authentication
    :param password: Password for OAuth2 authentication
    :param client_id: Client ID for OAuth2 authentication
    :param client_secret: Client Secret for OAuth2 authentication
    :param max_items_to_return: Max items to return for export
    :return: True if no problems; False otherwise
    """
    errors = []
    if SettingsOps.validate_stored_info(username, password, max_items_to_return, errors):
        return True
    else:
        iface.messageBar().pushMessage("Error", "Unable to validate settings due to:<br />" + "<br />".join(errors))
        return False
