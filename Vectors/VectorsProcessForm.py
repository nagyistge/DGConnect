# -*- coding: utf-8 -*-
__author__ = 'mtrotter'


from qgis.gui import QgsMessageBar
from PyQt4 import QtGui
from PyQt4.QtCore import QSettings
from os.path import expanduser
from VectorsInsightCloudQuery import InsightCloudQuery, InsightCloudSourcesParams
from ..Settings import SettingsOps

import re
import os

SELECT_FILE = "select.file"

# file filter
DEFAULT_SUFFIX = "csv"
SELECT_FILTER = "CSV Files(*.csv)"

VALIDATION_LAT_LOWER = -90.0
VALIDATION_LAT_UPPER = 90.0
VALIDATION_LONG_LOWER = -180.0
VALIDATION_LONG_UPPER = 180.0

VALIDATION_AOI_DIFF = 10

# simple regex validator for data; make sure there's something there
ENDS_WITH_SUFFIX_REGEX = re.compile(".+\." + DEFAULT_SUFFIX + "$")


def search_clicked(ui, dialog_tool):
    """
    Action performed when the ok button is clicked
    :param ui: The UI ui where this occurs
    :return: None
    """
    errors = []
    if not validate_bbox(ui, errors):
        dialog_tool.iface.messageBar().pushMessage("ERROR", "The following errors occurred:<br />" +
                                                   "<br />".join(errors),
                                                   level=QgsMessageBar.CRITICAL)
        return
    top = ui.top.text()
    bottom = ui.bottom.text()
    left = ui.left.text()
    right = ui.right.text()
    query = ui.query.text()
    if query and len(query) == 0:
        query = None
    params = InsightCloudSourcesParams(top=top, right=right, bottom=bottom, left=left, query=query)
    dialog_tool.query_sources(params)

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
        iface.messageBar().pushMessage("Info", "Successfully checked settings. Launching queries...")
        return True
    else:
        iface.messageBar().pushMessage("Error", "Unable to validate settings due to:<br />" + "<br />".join(errors))
        return False


def validate_bbox(ui, errors):
    """
    Validates the boundary box fields (top, left, right, bottom)
    :param ui: The GUI containing the fields
    :param errors: The list of errors occurred thus far
    :return: None
    """
    return validate_bbox_fields(ui.left.text(), ui.right.text(), ui.top.text(), ui.bottom.text(), errors)

def validate_bbox_fields(left, right, top, bottom, errors):
    """
    Validates the boundary box fields (top, left, right, bottom)
    :param left: The left value of the box
    :param right: The right value of the box
    :param top: The top value of the box
    :param bottom: The bottom value of the box
    :param errors: THe list of error occurred thus far
    :return: True if there are no errors; False otherwise
    """
    is_left_valid = validate_bbox_field(left, "Left", VALIDATION_LONG_LOWER, VALIDATION_LONG_UPPER, errors)
    is_right_valid = validate_bbox_field(right, "Right", VALIDATION_LONG_LOWER, VALIDATION_LONG_UPPER, errors)
    is_top_valid = validate_bbox_field(top, "Top", VALIDATION_LAT_LOWER, VALIDATION_LAT_UPPER, errors)
    is_bottom_valid = validate_bbox_field(bottom, "Bottom", VALIDATION_LAT_LOWER, VALIDATION_LAT_UPPER, errors)

    is_valid = is_left_valid and is_right_valid and is_top_valid and is_bottom_valid

    left_float = float(left)
    right_float = float(right)
    bottom_float = float(bottom)
    top_float = float(top)
    # check that right > left
    if is_left_valid and is_right_valid and left_float > right_float:
        errors.append("Provided left (%s) is greater than right (%s)" % (left, right))
        is_valid = False
    elif abs(right_float - left_float) > VALIDATION_AOI_DIFF:
        errors.append("Provided left (%s) is greater than 10 degrees away from right (%s)" % (left, right))
        is_valid = False

    if is_top_valid and is_bottom_valid and bottom_float > top_float:
        errors.append("Provided bottom (%s) is greater than top (%s)" % (bottom, top))
        is_valid = False
    elif abs(top_float - bottom_float) > VALIDATION_AOI_DIFF:
        errors.append("Provided top (%s) is greater than 10 degrees away from bottom (%s)" % (top, bottom))
        is_valid = False

    return is_valid

def validate_bbox_field(field_value, field_name, lower_bound, upper_bound, errors):
    """
    Performs value validation on a given box field
    :param field_value: The text value of the field
    :param field_name: The name of the field
    :param lower_bound: The lower bound of values for the field
    :param upper_bound: The upper bound of values for the field
    :param errors: List of errors that have occurred so far
    :return: True if there are no errors; False otherwise
    """
    is_field_valid = True
    if field_value is None or len(field_value) <= 0:
        is_field_valid = False
        errors.append("No %s provided." % field_name)
    else:
        # try parsing field value
        try:
            float_value = float(field_value)
            if float_value < lower_bound:
                is_field_valid = False
                errors.append("Provided %s (%s) is below threshold of %s."  % (field_name, field_value, lower_bound))
            elif float_value > upper_bound:
                is_field_valid = False
                errors.append("Provided %s (%s) is above threshold of %s." % (field_name, field_value, upper_bound))
        except ValueError, e:
            is_field_valid = False
            errors.append("Provided %s (%s) is not a number" % (field_name, field_value))
    return is_field_valid
