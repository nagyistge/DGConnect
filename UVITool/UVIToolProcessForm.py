__author__ = 'mtrotter'


from qgis.gui import QgsMessageBar
from PyQt4 import QtGui
from PyQt4.QtCore import QSettings
from os.path import expanduser

import re
import os


# constants for plugin settings
PLUGIN_NAME = "DGConnect"
GBD_USERNAME = "gbd.username"
GBD_PASSWORD = "gbd.password"
GBD_API_KEY = "gbd.api.key"
INSIGHTCLOUD_USERNAME = "insightcloud.username"
INSIGHTCLOUD_PASSWORD = "insightcloud.password"
SELECT_FILE = "select.file"

# file filter
DEFAULT_SUFFIX = "csv"
SELECT_FILTER = "CSV Files(*.csv)"

VALIDATION_LAT_LOWER = -90.0
VALIDATION_LAT_UPPER = 90.0
VALIDATION_LONG_LOWER = -180.0
VALIDATION_LONG_UPPER = 180.0

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

def ok_clicked(ui):
    """
    Action performed when the ok button is clicked
    :param ui: The UI ui where this occurs
    :return: None
    """
    pass

def cancel_clicked(ui):
    """
    Action performed when the cancel button is clicked
    :param ui:  The UI ui when this occurs
    :return: None
    """
    ui.dialog.reject()

def load_settings_clicked(ui):
    """
    Action performed when the load settings button is performed
    :param ui: The GUI object with the fields to update
    :return: None
    """
    load_settings(ui)

    # write sucess message
    message = QtGui.QMessageBox
    message.information(None, "Credentials Loaded!", "Credentials Loaded!")

def load_settings(ui):
    """
    Reads the QSettings file and fills in the relevant fields with stored data if present
    :param ui: The GUI object to update
    :return: None
    """

    ui.insightcloud_username.setText(read_setting(PLUGIN_NAME + "/" + INSIGHTCLOUD_USERNAME))
    ui.insightcloud_password.setText(read_setting(PLUGIN_NAME + "/" + INSIGHTCLOUD_PASSWORD))

def save_settings_clicked(ui):
    """
    Action performed when the save button is clicked; updates the settings file with the new data
    :param ui: The GUI object holding the fields
    :return: None
    """

    write_setting(PLUGIN_NAME + "/" + INSIGHTCLOUD_USERNAME, ui.insightcloud_username.text())
    write_setting(PLUGIN_NAME + "/" + INSIGHTCLOUD_PASSWORD, ui.insightcloud_password.text())

    # write success message
    message = QtGui.QMessageBox()
    message.information(None, "Credentials Saved!", "Credentials Saved!")

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
    validate_insightcloud_info(ui, errors)
    if len(errors) > 0:
        iface.messageBar().pushMessage("Error", "The following error(s) occurred:\n" + "\n".join(errors),
                                       level=QgsMessageBar.CRITICAL)
        return False
    return True


def validate_insightcloud_info(ui, errors):
    """
    Validates the InsightCloud fields for errors
    :param ui: The GUI containing the fields
    :param errors: The list of errors that have occurred so far
    :return: None
    """
    # check insightcloud credentials
    is_insightcloud_info_good = True
    if is_field_empty(ui.insightcloud_username):
        is_insightcloud_info_good = False
        errors.append("No InsightCloud username provided.")
    if is_field_empty(ui.insightcloud_password):
        is_insightcloud_info_good = False
        errors.append("No InsightCloud password provided.")
    # validate credentials by hitting monocle-3
    if is_insightcloud_info_good:
        query = InsightCloudQuery(username=ui.insightcloud_username.text(),
                                  password=ui.insightcloud_password.text())
        query.log_into_monocle_3()
        if not query.is_login_successful:
            errors.append("Unable to verify InsightCloud credentials. See logs for more details.")

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
    try:
        float_value = float(str_value)
        return True
    except ValueError, e:
        return False