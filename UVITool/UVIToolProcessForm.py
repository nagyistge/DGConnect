# -*- coding: utf-8 -*-
__author__ = 'mtrotter'


from qgis.gui import QgsMessageBar
from PyQt4 import QtGui
from PyQt4.QtCore import QSettings
from os.path import expanduser
from InsightCloudQuery import InsightCloudQuery, InsightCloudSourcesParams

import re
import os


# constants for plugin settings
PLUGIN_NAME = "DGConnect"
GBD_USERNAME = "gbd.username"
GBD_PASSWORD = "gbd.password"
GBD_API_KEY = "gbd.api.key"
INSIGHTCLOUD_USERNAME = "insightcloud.username"
INSIGHTCLOUD_PASSWORD = "insightcloud.password"
MAX_ITEMS_TO_RETURN = "max.items.to.return"
SELECT_FILE = "select.file"

# file filter
DEFAULT_SUFFIX = "csv"
SELECT_FILTER = "CSV Files(*.csv)"

VALIDATION_LAT_LOWER = -90.0
VALIDATION_LAT_UPPER = 90.0
VALIDATION_LONG_LOWER = -180.0
VALIDATION_LONG_UPPER = 180.0

VALIDATION_MIN_EXPORT = 1
VALIDATION_MAX_EXPORT = 150000

# simple regex validator for data; make sure there's something there
ENDS_WITH_SUFFIX_REGEX = re.compile(".+\." + DEFAULT_SUFFIX + "$")

def read_setting(key, object_type=str):
    """
    Loads the value from the QSettings specified by the key
    :param key: Key from the QSettings maps
    :param object_type: Type to return (defaults to str)
    :return: The value if present; else ""
    """
    s = QSettings()
    if s.contains(key):
        return s.value(key, type=object_type)
    return ""

def write_setting(key, value):
    """
    Writes the key with the value specified to the QSettings map
    :param key: The key in the map to write to
    :param value: The value to write
    :return: None
    """
    s = QSettings()
    s.setValue(key, value)

def search_clicked(ui, dialog_tool):
    """
    Action performed when the ok button is clicked
    :param ui: The UI ui where this occurs
    :return: None
    """
    top = ui.top.text()
    bottom = ui.bottom.text()
    left = ui.left.text()
    right = ui.right.text()
    query = ui.query.text()
    if query and len(query) == 0:
        query = None
    params = InsightCloudSourcesParams(top=top, right=right, bottom=bottom, left=left, query=query)
    dialog_tool.query_sources(params)


def cancel_clicked(ui):
    """
    Action performed when the cancel button is clicked
    :param ui:  The UI ui when this occurs
    :return: None
    """
    ui.dialog.reject()

def load_settings(ui):
    """
    Reads the QSettings file and fills in the relevant fields with stored data if present
    :param ui: The GUI object to update
    :return: None
    """

    ui.username.setText(read_setting(PLUGIN_NAME + "/" + INSIGHTCLOUD_USERNAME))
    ui.password.setText(read_setting(PLUGIN_NAME + "/" + INSIGHTCLOUD_PASSWORD))
    ui.max_items_to_return.setText(read_setting(PLUGIN_NAME + "/" + MAX_ITEMS_TO_RETURN))

def get_settings():
    max_settings_to_return_str = read_setting(PLUGIN_NAME + "/" + MAX_ITEMS_TO_RETURN)
    max_settings_to_return = None
    if validate_is_int(max_settings_to_return_str):
        max_settings_to_return = int(max_settings_to_return_str)
    return read_setting(PLUGIN_NAME + "/" + INSIGHTCLOUD_USERNAME), \
           read_setting(PLUGIN_NAME + "/" + INSIGHTCLOUD_PASSWORD), \
           max_settings_to_return

def save_settings_clicked(ui, iface, dialog):
    """
    Action performed when the save button is clicked; updates the settings file with the new data
    :param ui: The GUI object holding the fields
    :return: None
    """
    if validate_save_settings(ui, iface):
        write_setting(PLUGIN_NAME + "/" + INSIGHTCLOUD_USERNAME, ui.username.text())
        write_setting(PLUGIN_NAME + "/" + INSIGHTCLOUD_PASSWORD, ui.password.text())
        write_setting(PLUGIN_NAME + "/" + MAX_ITEMS_TO_RETURN, ui.max_items_to_return.text())
        iface.messageBar().pushMessage("Info", "InsightCloud settings saved successfully!")
        dialog.accept()

def validate_settings_clicked(ui, iface):
    if validate_save_settings(ui, iface):
        iface.messageBar().pushMessage("Info", "Entered settings have been validated successfully!")


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

def is_field_empty(field):
    """
    Validation method to test if a given field is empty
    :param field: Field to test
    :return: True if empty; false if not
    """
    text = field.text()
    return text is None or len(text) == 0

def show_errors(errors):
    """
    Helper method to render errors for the error message dialog
    :param errors: List of string errors to output
    :return: A str representation of the errors
    """
    return "The following errors have occurred:<br />" + "<br />".join(errors)

def validate_save_settings(ui, iface):
    """
    Validates the GDB fields and output path for errors
    :param ui: The GUI containing the fields
    :return: True if there are no errors; False otherwise
    """
    errors = []
    validate_info(ui, errors)
    if len(errors) > 0:
        iface.messageBar().pushMessage("Error", "The following error(s) occurred:\n" + "\n".join(errors),
                                       level=QgsMessageBar.CRITICAL)
        return False
    return True

def validate_info(ui, errors):
    """
    Validates the InsightCloud fields for errors
    :param ui: The GUI containing the fields
    :param errors: The list of errors that have occurred so far
    :return: None
    """
    # check insightcloud credentials
    is_info_good = True
    if is_field_empty(ui.username):
        is_info_good = False
        errors.append("No InsightCloud username provided.")
    if is_field_empty(ui.password):
        is_info_good = False
        errors.append("No InsightCloud password provided.")
    # validate credentials by hitting monocle-3
    if is_info_good:
        query = InsightCloudQuery(username=ui.username.text(),
                                  password=ui.password.text())
        query.log_into_monocle_3()
        if not query.is_login_successful:
            errors.append("Unable to verify InsightCloud credentials. See logs for more details.")
    # validate max items to return
    max_items_to_return = ui.max_items_to_return
    if is_field_empty(max_items_to_return):
        errors.append("No Max Items to Return provided.")
    elif validate_is_int(max_items_to_return.text()):
        max_items_to_return_int = int(max_items_to_return.text())
        if max_items_to_return_int < VALIDATION_MIN_EXPORT:
            errors.append("Supplied Max Items to Return (" + max_items_to_return.text() + ") is below threshold of "
                          + str(VALIDATION_MIN_EXPORT))
        elif max_items_to_return_int > VALIDATION_MAX_EXPORT:
            errors.append("Supplied Max Items to Return (" + max_items_to_return.text() + ") is above threshold of "
                          + str(VALIDATION_MAX_EXPORT))
    else:
        errors.append("Supplied Max Items to Return (" + max_items_to_return.text() + ") is not an integer.")

def validate_stored_settings(iface, username, password, max_items_to_return):
    """
    Validates the settings in the stored settings
    :param iface: QGIS interface to push messages to
    :param username: Username for CAS Authentication
    :param password: Password for CAS Authentication
    :param max_items_to_return: Max items to return for export
    :return: True if no problems; False otherwise
    """
    errors = []
    if validate_stored_info(username, password, max_items_to_return, errors):
        iface.messageBar().pushMessage("Info", "Successfully checked settings. Launching queries...")
        return True
    else:
        iface.messageBar().pushMessage("Error", "Unable to validate settings due to:\n" + "\n".join(errors))
        return False

def validate_stored_info(username, password, max_items_to_return, errors):
    """
    Validates the username and password in the stored setting, writing any errors to the provided list
    :param username: Username for CAS Authentication
    :param password: Password for CAS Authentication
    :param errors: List of errors
    :return: True if all validation passes; False if there are errors
    """
    # check insightcloud credentials
    is_field_good = True
    if not username or len(username) == 0:
        is_field_good = False
        errors.append("No InsightCloud username provided.")
    if not password or len(password) == 0:
        is_field_good = False
        errors.append("No InsightCloud password provided.")
    if is_field_good:
        query = InsightCloudQuery(username=username, password=password)
        query.log_into_monocle_3()
        if not query.is_login_successful:
            errors.append("Unable to verify InsightCloud credentials. See logs for details.")
            is_field_good = False
    if not max_items_to_return or max_items_to_return < VALIDATION_MIN_EXPORT or max_items_to_return \
            > VALIDATION_MAX_EXPORT:
        is_field_good = False
    return is_field_good


def validate_bbox(ui, errors):
    """
    Validates the boundary box fields (top, left, right, bottom)
    :param ui: The GUI containing the fields
    :param errors: The list of errors occurred thus far
    :return: None
    """
    validate_bbox_fields(ui.left.text(), ui.right.text(), ui.top.text(), ui.bottom.text(), errors)

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

    # check that right > left
    if is_left_valid and is_right_valid and float(left) > float(right):
        errors.append("Provided left (%s) is greater than right (%s)" % (left, right))
        is_valid = False

    if is_top_valid and is_bottom_valid and float(bottom) > float(top):
        errors.append("Provided top (%s) is greater than bottom (%s)" % (top, bottom))
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

def validate_is_float(str_value):
    """
    Checks if a string can be converted to a float
    :param str_value: The string value
    :return: True if yes; False if no
    """
    if not str_value or len(str_value) == 0:
        return False
    try:
        float_value = float(str_value)
        return True
    except ValueError, e:
        return False

def validate_is_int(str_value):
    """
    Checks if a string can be converted to an int
    :param str_value: The string value
    :return: True if yes; False if no
    """
    if not str_value or len(str_value) == 0:
        return False
    try:
        int_value = int(str_value)
        return True
    except ValueError, e:
        return False