__author__ = 'mtrotter'

import unittest
import DGConnect
import DGConnectProcessForm

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
        proj.writeEntry(DGConnectProcessForm.PLUGIN_NAME, DGConnectProcessForm.GBD_API_KEY, '')
        proj.writeEntry(DGConnectProcessForm.PLUGIN_NAME, DGConnectProcessForm.GBD_USERNAME, '')
        proj.writeEntry(DGConnectProcessForm.PLUGIN_NAME, DGConnectProcessForm.GBD_PASSWORD, '')

        proj.writeEntry(DGConnectProcessForm.PLUGIN_NAME, DGConnectProcessForm.INSIGHTCLOUD_USERNAME, '')
        proj.writeEntry(DGConnectProcessForm.PLUGIN_NAME, DGConnectProcessForm.INSIGHTCLOUD_PASSWORD, '')

    def test_ui_launch_defaults(self):
        self.assertEqual(self.connect.dlg.ui.gbd_api_key.text(), '')
        self.assertEqual(self.connect.dlg.ui.gbd_username.text(), '')
        self.assertEqual(self.connect.dlg.ui.gbd_password.text(), '')
        self.assertEqual(self.connect.dlg.ui.insightcloud_username.text(), '')
        self.assertEqual(self.connect.dlg.ui.insightcloud_password.text(), '')

    def test_update_gbd_api_key(self):
        proj = QgsProject.instance()

        proj.writeEntry(DGConnectProcessForm.PLUGIN_NAME, DGConnectProcessForm.GBD_API_KEY, 'ABCDEF')

        self.connect.dlg.ui.load_settings_button.click()

        self.assertEqual(self.connect.dlg.ui.gbd_api_key.text(), 'ABCDEF')
        self.assertEqual(self.connect.dlg.ui.gbd_username.text(), '')
        self.assertEqual(self.connect.dlg.ui.gbd_password.text(), '')
        self.assertEqual(self.connect.dlg.ui.insightcloud_username.text(), '')
        self.assertEqual(self.connect.dlg.ui.insightcloud_password.text(), '')

    def test_click_ok_bad(self):
        DGConnectProcessForm.ok_clicked(self.connect.dlg.ui)

if __name__ == '__main__':
    unittest.main()

