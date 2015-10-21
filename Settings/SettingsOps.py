from PyQt4.QtCore import QSettings
from qgis._gui import QgsMessageBar
from Vectors.VectorsInsightCloudQuery import InsightCloudQuery

__author__ = 'mtrotter'

VALIDATION_MIN_EXPORT = 1
VALIDATION_MAX_EXPORT = 150000

# constants for plugin settings
PLUGIN_NAME = "DGConnect"
INSIGHTCLOUD_USERNAME = "insightcloud.username"
INSIGHTCLOUD_PASSWORD = "insightcloud.password"
INSIGHTCLOUD_CLIENT_ID = "insightcloud.client_id"
INSIGHTCLOUD_CLIENT_SECRET = "insightcloud.client_secret"
MAX_ITEMS_TO_RETURN = "max.items.to.return"


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
        iface.messageBar().pushMessage("Error", "The following error(s) occurred:<br />" + "<br />".join(errors),
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
    # validate credentials by hitting insight-vector
    if is_info_good:
        query = InsightCloudQuery(username=ui.username.text(), password=ui.password.text())
        query.log_in()
        query.hit_test_endpoint()
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


def validate_stored_info(username, password, max_items_to_return, errors):
    """
    Validates the username and password in the stored setting, writing any errors to the provided list
    :param username: Username for OAuth2 authentication
    :param password: Password for OAuth2 authentication
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
        query.log_in()
        query.hit_test_endpoint()
        if not query.is_login_successful:
            errors.append("Unable to verify InsightCloud credentials. See logs for details.")
            is_field_good = False
    if not max_items_to_return or max_items_to_return < VALIDATION_MIN_EXPORT or max_items_to_return \
            > VALIDATION_MAX_EXPORT:
        is_field_good = False
    return is_field_good