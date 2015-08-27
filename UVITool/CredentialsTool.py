__author__ = 'mtrotter'

from UVITool_Credentials import Ui_Credentials
from PyQt4.QtGui import QDialog
import UVIToolProcessForm

class CredentialsTool:
    """
    Tool for managing CAS credentials
    """

    def __init__(self, iface):
        """
        Constructor
        :param iface: QGIS Interface
        :return: CredentialsTool
        """
        self.iface = iface
        self.dialog = CredientialsDialog()
        UVIToolProcessForm.load_settings(self.dialog.ui)
        self.dialog.ui.validate_button.clicked.connect(lambda:
                                                       UVIToolProcessForm.validate_settings_clicked(self.dialog.ui,
                                                                                                    self.iface))
        self.dialog.ui.save_button.clicked.connect(lambda:
                                                   UVIToolProcessForm.save_settings_clicked(self.dialog.ui,
                                                                                            self.iface,
                                                                                            self.dialog))
        self.dialog.show()


class CredientialsDialog(QDialog):
    """
    Dialog for handling the CAS credentials
    """

    def __init__(self):
        """
        Constructor
        :return: CredentialsDialog
        """
        QDialog.__init__(self)
        self.ui = Ui_Credentials()
        self.ui.setupUi(self)