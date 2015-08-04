__author__ = 'Michael Trotter <michael.trotter@digitalglobe.com>'

from PyQt4 import QtGui
from PyQt4.QtCore import QSettings
from os.path import expanduser

from GBDQuery import GBDQuery
from InsightCloudQuery import InsightCloudQuery

import CSVOutput

import re

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
    if validate_ok(ui):
        # build gbd query
        gbd_query = GBDQuery(auth_token=ui.gbd_api_key.text(), username=ui.gbd_username.text(),
                         password=ui.gbd_password.text())
        gbd_query.log_in()
        gbd_query.hit_test_endpoint()

        # build insightcloud query
        insightcloud_query = InsightCloudQuery(username=ui.insightcloud_username.text(),
                                  password=ui.insightcloud_password.text())
        insightcloud_query.log_into_monocle_3()
        CSVOutput.generate_csv(top=float(ui.top.text()), left=float(ui.left.text()),
                               bottom=float(ui.bottom.text()), right=float(ui.right.text()),
                               gbd_query=gbd_query, insightcloud_query=insightcloud_query,
                               csv_filename=ui.select_file.text())
    else:
        ui.dialog.show()

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
    # read values
    ui.gbd_api_key.setText(read_setting(PLUGIN_NAME + "/" + GBD_API_KEY))
    ui.gbd_username.setText(read_setting(PLUGIN_NAME + "/" + GBD_USERNAME))
    ui.gbd_password.setText(read_setting(PLUGIN_NAME + "/" + GBD_PASSWORD))

    ui.insightcloud_username.setText(read_setting(PLUGIN_NAME + "/" + INSIGHTCLOUD_USERNAME))
    ui.insightcloud_password.setText(read_setting(PLUGIN_NAME + "/" + INSIGHTCLOUD_PASSWORD))

    ui.select_file.setText(read_setting(PLUGIN_NAME + "/" + SELECT_FILE))

def save_settings_clicked(ui):
    """
    Action performed when the save button is clicked; updates the settings file with the new data
    :param ui: The GUI object holding the fields
    :return: None
    """
    # store values
    write_setting(PLUGIN_NAME + "/" + GBD_API_KEY, ui.gbd_api_key.text())
    write_setting(PLUGIN_NAME + "/" + GBD_USERNAME, ui.gbd_username.text())
    write_setting(PLUGIN_NAME + "/" + GBD_PASSWORD, ui.gbd_password.text())

    write_setting(PLUGIN_NAME + "/" + INSIGHTCLOUD_USERNAME, ui.insightcloud_username.text())
    write_setting(PLUGIN_NAME + "/" + INSIGHTCLOUD_PASSWORD, ui.insightcloud_password.text())

    write_setting(PLUGIN_NAME + "/" + SELECT_FILE, ui.select_file.text())

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

def validate_save_settings(ui):
    """
    Validates the GDB fields and output path for errors
    :param ui: The GUI containing the fields
    :return: True if there are no errors; False otherwise
    """
    errors = []
    validate_gbd_info(ui, errors)
    validate_output_path(ui, errors)
    if len(errors) > 0:
        error_dialog = QtGui.QErrorMessage(ui.dialog)
        error_dialog.showMessage(show_errors(errors))
        return False
    return True

def validate_ok(ui):
    """
    Validates the fields for when the OK button is clicked
    :param ui:  The GUI containing the fields
    :return: True if there are no errors, False otherwise
    """
    errors = []
    validate_gbd_info(ui, errors)
    validate_output_path(ui, errors)
    validate_insightcloud_info(ui, errors)
    if len(errors) > 0:
        error_dialog = QtGui.QErrorMessage(ui.dialog)
        error_dialog.showMessage(show_errors(errors))
        return False
    return True

def validate_gbd_info(ui, errors):
    """
    Validates the GBD fields
    :param ui: The GUI containing the fields
    :param errors: The list of errors that have occurred
    :return: None
    """
    # check gbd info
    is_gbd_info_good = True
    if is_field_empty(ui.gbd_api_key):
        is_gbd_info_good = False
        errors.append("No GBD Api Key provided.")
    if is_field_empty(ui.gbd_username):
        is_gbd_info_good = False
        errors.append("No GBD Username provided.")
    if is_field_empty(ui.gbd_password):
        is_gbd_info_good = False
        errors.append("No GBD Password provided.")
    # validate credentials by hitting validate page
    if is_gbd_info_good:
        query = GBDQuery(auth_token=ui.gbd_api_key.text(), username=ui.gbd_username.text(),
                         password=ui.gbd_password.text())
        query.log_in()
        query.hit_test_endpoint()
        if not query.is_login_successful:
            errors.append("Unable to verify GBD credentials. See logs for more detail.")

def validate_output_path(ui, errors):
    """
    Checks the output path for the CSV path
    :param ui: The GUI containing the field
    :param errors: The list of errors that have occurred so far
    :return: None
    """
    # check if empty
    if is_field_empty(ui.select_file):
        errors.append("No output file provided.")
    # check if regex matches
    elif re.match(ENDS_WITH_SUFFIX_REGEX, ui.select_file.text()) is None:
        errors.append("Output file must be a csv file.")

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
