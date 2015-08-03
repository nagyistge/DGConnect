__author__ = 'Michael Trotter <michael.trotter@digitalglobe.com>'

from PyQt4 import QtGui
from qgis.core import QgsProject
from os.path import expanduser

from GBDQuery import GBDQuery
from InsightCloudQuery import InsightCloudQuery

import re

# constants for plugin settings
PLUGIN_NAME = "DGConnect"
gbd_USERNAME = "gbd.username"
gbd_PASSWORD = "gbd.password"
gbd_API_KEY = "gbd.api.key"
INSIGHTCLOUD_USERNAME = "insightcloud.username"
INSIGHTCLOUD_PASSWORD = "insightcloud.password"
SELECT_FILE = "select.file"

# file filter
DEFAULT_SUFFIX = "csv"
SELECT_FILTER = "CSV Files(*.csv)"

# simple regex validator for data; make sure there's something there
ENDS_WITH_SUFFIX_REGEX = re.compile(".+\." + DEFAULT_SUFFIX + "$")

def ok_clicked(ui):
    """
    Action performed when the ok button is clicked
    :param ui: The UI ui where this occurs
    :return: None
    """
    if validate_ok(ui):
        print("No errors")
        ui.dialog.accept()
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

    :param ui:
    :return:
    """
    proj = QgsProject.instance()

    # read values
    ui.gbd_api_key.setText(proj.readEntry(PLUGIN_NAME, gbd_API_KEY)[0])
    ui.gbd_username.setText(proj.readEntry(PLUGIN_NAME, gbd_USERNAME)[0])
    ui.gbd_password.setText(proj.readEntry(PLUGIN_NAME, gbd_PASSWORD)[0])

    ui.insightcloud_username.setText(proj.readEntry(PLUGIN_NAME, INSIGHTCLOUD_USERNAME)[0])
    ui.insightcloud_password.setText(proj.readEntry(PLUGIN_NAME, INSIGHTCLOUD_PASSWORD)[0])

    ui.select_file.setText(proj.readEntry(PLUGIN_NAME, SELECT_FILE)[0])

def save_settings_clicked(ui):
    proj = QgsProject.instance()

    # store values
    proj.writeEntry(PLUGIN_NAME, gbd_API_KEY, ui.gbd_api_key.text())
    proj.writeEntry(PLUGIN_NAME, gbd_USERNAME, ui.gbd_username.text())
    proj.writeEntry(PLUGIN_NAME, gbd_PASSWORD, ui.gbd_password.text())

    proj.writeEntry(PLUGIN_NAME, INSIGHTCLOUD_USERNAME, ui.insightcloud_username.text())
    proj.writeEntry(PLUGIN_NAME, INSIGHTCLOUD_PASSWORD, ui.insightcloud_password.text())

    proj.writeEntry(PLUGIN_NAME, SELECT_FILE, ui.select_file.text())

def select_file_clicked(ui):
    # open file ui
    file_ui = QtGui.QFileDialog()
    file_name = file_ui.getSaveFileName(None, "Choose output file", str(expanduser("~")), SELECT_FILTER)
    ui.select_file.setText(file_name)

def is_field_empty(field):
    text = field.text()
    return text is None or len(text) == 0

def show_errors(errors):
    return "The following errors have occurred:<br />" + "<br />".join(errors)

def validate_save_settings(ui, errors):
    validate_gbd_info(ui, errors)
    return errors

def validate_ok(ui):
    errors = []
    validate_save_settings(ui, errors)
    validate_output_path(ui, errors)
    validate_insightcloud_info(ui, errors)
    if len(errors) > 0:
        error_dialog = QtGui.QErrorMessage(ui.dialog)
        error_dialog.showMessage(show_errors(errors))
        return False
    return True

def validate_gbd_info(ui, errors):
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
    # check if empty
    if is_field_empty(ui.select_file):
        errors.append("No output file provided.")
    # check if regex matches
    elif re.match(ENDS_WITH_SUFFIX_REGEX, ui.select_file.text()[0]) is None:
        errors.append("Output file must be a csv file.")

def validate_insightcloud_info(ui, errors):
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
