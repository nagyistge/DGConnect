__author__ = 'mtrotter'

from Vectors_Settings import Vectors_Settings
from PyQt4.QtGui import QDialog
import VectorsProcessForm

class VectorsSettingsTool:
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
        self.dialog = VectorsSettingsDialog()
        VectorsProcessForm.load_settings(self.dialog.ui)
        self.dialog.ui.validate_button.clicked.connect(lambda:
                                                       VectorsProcessForm.validate_settings_clicked(self.dialog.ui,
                                                                                                    self.iface))
        self.dialog.ui.save_button.clicked.connect(lambda:
                                                   VectorsProcessForm.save_settings_clicked(self.dialog.ui,
                                                                                            self.iface,
                                                                                            self.dialog))
        self.dialog.show()


class VectorsSettingsDialog(QDialog):
    """
    Dialog for handling the settings
    """

    def __init__(self):
        """
        Constructor
        :return: SettingsDialog
        """
        QDialog.__init__(self)
        self.ui = Vectors_Settings()
        self.ui.setupUi(self)