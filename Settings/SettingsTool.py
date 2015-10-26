import SettingsOps
import Settings

__author__ = 'mtrotter'

from PyQt4.QtGui import QDialog


class SettingsTool:
    """
    Tool for managing settings like OAuth2 credentials and max items to return
    """

    def __init__(self, iface):
        """
        Constructor
        :param iface: QGIS Interface
        :return: CredentialsTool
        """
        self.iface = iface
        self.dialog = SettingsDialog()
        SettingsOps.load_settings(self.dialog.ui)
        self.dialog.ui.validate_button.clicked.connect(lambda:
                                                       SettingsOps.validate_settings_clicked(self.dialog.ui,
                                                                                             self.iface))
        self.dialog.ui.save_button.clicked.connect(lambda:
                                                   SettingsOps.save_settings_clicked(self.dialog.ui,
                                                                                     self.iface,
                                                                                     self.dialog))
        self.dialog.ui.buttonBox.accepted.connect(lambda:
                                                  SettingsOps.save_settings_clicked(self.dialog.ui,
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
        self.ui = Settings.Ui_Settings()
        self.ui.setupUi(self)
