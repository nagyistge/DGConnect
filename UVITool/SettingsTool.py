__author__ = 'mtrotter'

from UVITool_Settings import Ui_Settings
from PyQt4.QtGui import QDialog
import UVIToolProcessForm

class SettingsTool:
    """
    Tool for managing settings like CAS credentials and max items to return
    """

    def __init__(self, iface):
        """
        Constructor
        :param iface: QGIS Interface
        :return: CredentialsTool
        """
        self.iface = iface
        self.dialog = SettingsDialog()
        UVIToolProcessForm.load_settings(self.dialog.ui)
        self.dialog.ui.validate_button.clicked.connect(lambda:
                                                       UVIToolProcessForm.validate_settings_clicked(self.dialog.ui,
                                                                                                    self.iface))
        self.dialog.ui.save_button.clicked.connect(lambda:
                                                   UVIToolProcessForm.save_settings_clicked(self.dialog.ui,
                                                                                            self.iface,
                                                                                            self.dialog))
        self.dialog.show()


class SettingsDialog(QDialog):
    """
    Dialog for handling the settings
    """

    def __init__(self):
        """
        Constructor
        :return: SettingsDialog
        """
        QDialog.__init__(self)
        self.ui = Ui_Settings()
        self.ui.setupUi(self)