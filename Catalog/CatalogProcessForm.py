# -*- coding: utf-8 -*-
__author__ = 'mtrotter'


from qgis.gui import QgsMessageBar
from PyQt4 import QtGui
from PyQt4.QtCore import QSettings
from os.path import expanduser
from CatalogGBDQuery import GBDQuery, GBDOrderParams

import re
import os


# constants for plugin settings
PLUGIN_NAME = "DGConnect"
USERNAME = "insightcloud.username"
PASSWORD = "insightcloud.password"
CLIENT_ID = "insightcloud.client_id"
CLIENT_SECRET = "insightcloud.client_secret"
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

VALIDATION_AOI_DIFF = 10

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

def search_clicked(dialog_tool, left, right, top, bottom, query=None):
    """
    Action performed when the ok button is clicked
    :param ui: The UI ui where this occurs
    :return: None
    """
    errors = []
    if not validate_bbox_fields(top=top, bottom=bottom, left=left, right=right, errors=errors):
        dialog_tool.iface.messageBar().pushMessage("ERROR", "The following errors occurred:<br />" +
                                                   "<br />".join(errors),
                                                   level=QgsMessageBar.CRITICAL)
        return
    params = GBDOrderParams(top=top, right=right, bottom=bottom, left=left, time_begin=None, time_end=None)
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

    ui.username.setText(read_setting(PLUGIN_NAME + "/" + USERNAME))
    ui.password.setText(read_setting(PLUGIN_NAME + "/" + PASSWORD))
    ui.client_id.setText(read_setting(PLUGIN_NAME + "/" + CLIENT_ID))
    ui.client_secret.setText(read_setting(PLUGIN_NAME + "/" + CLIENT_SECRET))
    ui.max_items_to_return.setText(read_setting(PLUGIN_NAME + "/" + MAX_ITEMS_TO_RETURN))

def get_settings():
    max_settings_to_return_str = read_setting(PLUGIN_NAME + "/" + MAX_ITEMS_TO_RETURN)
    max_settings_to_return = None
    if validate_is_int(max_settings_to_return_str):
        max_settings_to_return = int(max_settings_to_return_str)
    return read_setting(PLUGIN_NAME + "/" + USERNAME), \
           read_setting(PLUGIN_NAME + "/" + PASSWORD), \
           read_setting(PLUGIN_NAME + "/" + CLIENT_ID), \
           read_setting(PLUGIN_NAME + "/" + CLIENT_SECRET), \
           max_settings_to_return

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

def validate_info(ui, errors):
    """
    Validates the Catalog fields for errors
    :param ui: The GUI containing the fields
    :param errors: The list of errors that have occurred so far
    :return: None
    """
    # check credentials
    is_info_good = True
    if is_field_empty(ui.username):
        is_info_good = False
        errors.append("No username provided.")
    if is_field_empty(ui.password):
        is_info_good = False
        errors.append("No password provided.")
    if is_field_empty(ui.client_id):
        is_info_good = False
        errors.append("No client ID provided.")
    if is_field_empty(ui.client_secret):
        is_info_good = False
        errors.append("No client secret provided.")
    # validate credentials by hitting service
    if is_info_good:
        query = GBDQuery(username=ui.username.text(), password=ui.password.text(),
                                  client_id=ui.client_id.text(), client_secret=ui.client_secret.text())
        query.log_in()
        query.hit_test_endpoint()
        if not query.is_login_successful:
            errors.append("Unable to verify credentials. See logs for more details.")
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
    if validate_stored_info(username, password, client_id, client_secret, max_items_to_return, errors):
        iface.messageBar().pushMessage("Info", "Successfully checked settings. Launching queries...")
        return True
    else:
        iface.messageBar().pushMessage("Error", "Unable to validate settings due to:<br />" + "<br />".join(errors))
        return False

def validate_stored_info(username, password, client_id, client_secret, max_items_to_return, errors):
    """
    Validates the username and password in the stored setting, writing any errors to the provided list
    :param username: Username for OAuth2 authentication
    :param password: Password for OAuth2 authentication
    :param client_id: Client ID for OAuth2 authentication
    :param client_secret: Client Secret for OAuth2 authentication
    :param errors: List of errors
    :return: True if all validation passes; False if there are errors
    """
    # check credentials
    is_field_good = True
    if not username or len(username) == 0:
        is_field_good = False
        errors.append("No username provided.")
    if not password or len(password) == 0:
        is_field_good = False
        errors.append("No password provided.")
    if not client_id or len(client_id) == 0:
        is_field_good = False
        errors.append("No client ID provided.")
    if not client_secret or len(client_secret) == 0:
        is_field_good = False
        errors.append("No client secret provided.")
    if is_field_good:
        query = GBDQuery(username=username, password=password, client_id=client_id, client_secret=client_secret)
        query.log_in()
        query.hit_test_endpoint()
        if not query.is_login_successful:
            errors.append("Unable to verify credentials. See logs for details.")
            is_field_good = False
    if not max_items_to_return or max_items_to_return < VALIDATION_MIN_EXPORT or max_items_to_return \
            > VALIDATION_MAX_EXPORT:
        is_field_good = False
    return is_field_good

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