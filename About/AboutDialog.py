from PyQt4.QtGui import QDialog
from About import Ui_AboutDialog

__author__ = 'Michael Trotter <michael.trotter@digitalglobe.com>'

class AboutDialog(QDialog):
    def __init__(self, QWidget_parent=None):
        QDialog.__init__(self, QWidget_parent)
        self.ui = Ui_AboutDialog()
        self.ui.setupUi(self)