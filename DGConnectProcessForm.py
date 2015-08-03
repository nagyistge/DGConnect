__author__ = 'Michael Trotter <michael.trotter@digitalglobe.com>'

from PyQt4 import QtGui
from qgis.core import QgsProject
from os.path import expanduser

from GBDQuery import GBDQuery

import re

# constants for plugin settings
PLUGIN_NAME = "DGConnect"
GDB_USERNAME = "gdb.username"
GDB_PASSWORD = "gdb.password"
GDB_API_KEY = "gdb.api.key"
INSIGHTCLOUD_USERNAME = "insightcloud.username"
INSIGHTCLOUD_PASSWORD = "insightcloud.password"
SELECT_FILE = "select.file"

# file filter
DEFAULT_SUFFIX = "csv"
SELECT_FILTER = "CSV Files(*.csv)"

# simple regex validator for data; make sure there's something there
ENDS_WITH_SUFFIX_REGEX = re.compile(".+\." + DEFAULT_SUFFIX + "$")

def ok_clicked(dialog):
    """
    Action performed when the ok button is clicked
    :param dialog: The UI dialog where this occurs
    :return: None
    """
    dialog.ui.accept()

def cancel_clicked(dialog):
    """
    Action performed when the cancel button is clicked
    :param dialog:  The UI dialog when this occurs
    :return: None
    """
    dialog.ui.reject()

def load_settings_clicked(dialog):
    """

    :param dialog:
    :return:
    """
    proj = QgsProject.instance()

    # read values
    dialog.gdb_api_key.setText(proj.readEntry(PLUGIN_NAME, GDB_API_KEY)[0])
    dialog.gdb_username.setText(proj.readEntry(PLUGIN_NAME, GDB_USERNAME)[0])
    dialog.gdb_password.setText(proj.readEntry(PLUGIN_NAME, GDB_PASSWORD)[0])

    dialog.insightcloud_username.setText(proj.readEntry(PLUGIN_NAME, INSIGHTCLOUD_USERNAME)[0])
    dialog.insightcloud_password.setText(proj.readEntry(PLUGIN_NAME, INSIGHTCLOUD_PASSWORD)[0])

    dialog.select_file.setText(proj.readEntry(PLUGIN_NAME, SELECT_FILE)[0])

def save_settings_clicked(dialog):
    proj = QgsProject.instance()

    # store values
    proj.writeEntry(PLUGIN_NAME, GDB_API_KEY, dialog.gdb_api_key.text())
    proj.writeEntry(PLUGIN_NAME, GDB_USERNAME, dialog.gdb_username.text())
    proj.writeEntry(PLUGIN_NAME, GDB_PASSWORD, dialog.gdb_password.text())

    proj.writeEntry(PLUGIN_NAME, INSIGHTCLOUD_USERNAME, dialog.insightcloud_username.text())
    proj.writeEntry(PLUGIN_NAME, INSIGHTCLOUD_PASSWORD, dialog.insightcloud_password.text())

    proj.writeEntry(PLUGIN_NAME, SELECT_FILE, dialog.select_file.text())

def select_file_clicked(dialog):
    # open file dialog
    file_dialog = QtGui.QFileDialog()
    file_name = file_dialog.getSaveFileName(None, "Choose output file", str(expanduser("~")), SELECT_FILTER)
    dialog.select_file.setText(file_name)

def is_field_empty(field):
    text = field.text()[0]
    return text is None or len(text) == 0

def validate_save_settings(dialog):
    errors = []
    validate_gdb_info(dialog, errors)
    validate_output_path(dialog, errors)
    return errors

def validate_ok(dialog):
    errors = validate_save_settings(dialog)


def validate_gdb_info(dialog, errors):
    # check gbd info
    is_gdb_info_good = True
    if is_field_empty(dialog.gdb_api_key):
        is_gdb_info_good = False
        errors.append("No GBD Api Key provided.")
    if is_field_empty(dialog.gdb_username):
        is_gdb_info_good = False
        errors.append("No GDB Username provided.")
    if is_field_empty(dialog.gdb_password):
        is_gdb_info_good = False
        errors.append("No GBD Password provided.")
    # validate credentials by hitting validate page
    if is_gdb_info_good:
        order = GBDQuery(auth_token=dialog.gdb_api_key.text()[0], username=dialog.gdb_username.text()[0],
                         password=dialog.gdb_password.text()[0])
        order.log_in()
        order.hit_test_endpoint()
        if not order.is_login_successful:
            errors.append("Unable to verify credentials. See logs for more detail.")

def validate_output_path(dialog, errors):
    # check if empty
    if is_field_empty(dialog.select_file):
        errors.append("No output file provided.")
    # check if regex matches
    elif re.match(ENDS_WITH_SUFFIX_REGEX, dialog.select_file.text()[0]) is None:
        errors.append("Output file must be a csv file.")

def validate_uvi_info(dialog, errors):
    yield
