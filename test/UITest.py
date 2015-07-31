__author__ = 'mtrotter'

import unittest
import DGConnect
import Ui_DGConnect

import sys

from qgis.core import QgsProject
from qgis.gui import QgsMapCanvas

from PyQt4.QtGui import QApplication
from PyQt4.QtTest import QTest
from PyQt4.QtCore import Qt

class QgisInterfaceDummy(object):
    def __init__(self):
        self.canvas = QgsMapCanvas()

    def mapCanvas(self):
        return self.canvas

    def __getattr__(self, item):
        # return a function that accepts any args and does nothing
        def dummy(*args, **kwargs):
            return None
        return dummy

class UITest(unittest.TestCase):
    def __init__(self, methodName='runTest'):
        super(UITest, self).__init__(methodName)
        self.app = QApplication(sys.argv)
        self.iface = QgisInterfaceDummy()
        self.connect = None

    def setUp(self):
        self.connect = DGConnect.DGConnect(self.iface)

        # self.connect.run()

        self.connect.initGui()
        self.connect.dlg = DGConnect.DGConnectDialog()
        # show the dialog
        self.connect.dlg.show()

    def tearDown(self):
        # delete all old keys
        proj = QgsProject.instance()

        # clear entries
        proj.writeEntry(Ui_DGConnect.PLUGIN_NAME, Ui_DGConnect.GDB_API_KEY, '')
        proj.writeEntry(Ui_DGConnect.PLUGIN_NAME, Ui_DGConnect.GDB_USERNAME, '')
        proj.writeEntry(Ui_DGConnect.PLUGIN_NAME, Ui_DGConnect.GDB_PASSWORD, '')

        proj.writeEntry(Ui_DGConnect.PLUGIN_NAME, Ui_DGConnect.INSIGHTCLOUD_USERNAME, '')
        proj.writeEntry(Ui_DGConnect.PLUGIN_NAME, Ui_DGConnect.INSIGHTCLOUD_PASSWORD, '')

    def test_ui_launch_defaults(self):
        self.assertEqual(self.connect.dlg.ui.gdb_api_key.text(), '')
        self.assertEqual(self.connect.dlg.ui.gdb_username.text(), '')
        self.assertEqual(self.connect.dlg.ui.gdb_password.text(), '')
        self.assertEqual(self.connect.dlg.ui.insightcloud_username.text(), '')
        self.assertEqual(self.connect.dlg.ui.insightcloud_password.text(), '')

    def test_update_gdb_api_key(self):
        proj = QgsProject.instance()

        proj.writeEntry(Ui_DGConnect.PLUGIN_NAME, Ui_DGConnect.GDB_API_KEY, 'ABCDEF')

        self.connect.dlg.ui.load_settings_clicked()

        self.assertEqual(self.connect.dlg.ui.gdb_api_key.text(), 'ABCDEF')
        self.assertEqual(self.connect.dlg.ui.gdb_username.text(), '')
        self.assertEqual(self.connect.dlg.ui.gdb_password.text(), '')
        self.assertEqual(self.connect.dlg.ui.insightcloud_username.text(), '')
        self.assertEqual(self.connect.dlg.ui.insightcloud_password.text(), '')

if __name__ == '__main__':
    unittest.main()

