import json
from multiprocessing import Lock
import os
from qgis._core import QgsCoordinateReferenceSystem, QgsField
from qgis._gui import QgsMessageBar
from qgis.core import QgsVectorLayer, QgsMapLayerRegistry
import re

from CatalogGBDQuery import GBDQuery, GBDOrderParams
from ..Settings import SettingsOps
import CatalogProcessForm
from PyQt4.QtCore import Qt, QThreadPool, QRunnable, QObject, pyqtSlot, pyqtSignal, QVariant
from PyQt4.QtGui import QStandardItem, QStandardItemModel, QProgressBar, QFileDialog, QSortFilterProxyModel


class CatalogDialogTool(QObject):
    """
    Tool for managing the search and export functionality
    """

    def __init__(self, iface, dialog_base):
        """
        Constructor for the dialog tool
        :param iface: The QGIS Interface
        :param dialog_base: The dialog GUI
        :return: dialog tool
        """
        QObject.__init__(self, None)
        self.iface = iface
        self.dialog_base = dialog_base
        self.search_thread_pool = QThreadPool()
        self.json_thread_pool = QThreadPool()
        self.progress_message_bar = None
        self.json_progress_message_bar = None
        self.json_progress = None
        self.search_lock = Lock()
        self.json_lock = Lock()
        self.search_thread_pool = QThreadPool()
        self.json_thread_pool = QThreadPool()


    def init_progress_bar(self):
        """
        Sets up the progress bar for search functionality
        :return: None
        """
        if not self.progress_message_bar:
            self.progress_message_bar = self.iface.messageBar().createMessage("Querying for data")
            progress = QProgressBar()
            progress.setMinimum(0)
            progress.setMaximum(0)
            progress.setAlignment(Qt.AlignLeft | Qt.AlignCenter)
            self.progress_message_bar.layout().addWidget(progress)
            self.iface.messageBar().pushWidget(self.progress_message_bar, self.iface.messageBar().INFO)


    def init_json_progress_bar(self, bar_max):
        """
        Sets up the progress bar for exporting
        :param bar_max: The max value for the progress bar
        :return: None
        """
        self.json_progress_message_bar = self.iface.messageBar().createMessage("Exporting json to " + self.directory)
        self.json_progress = QProgressBar()
        self.json_progress.setMinimum(0)
        self.json_progress.setMaximum(bar_max)
        self.json_progress.setAlignment(Qt.AlignLeft | Qt.AlignCenter)
        self.json_progress_message_bar.layout().addWidget(self.json_progress)
        self.iface.messageBar().pushWidget(self.json_progress_message_bar, self.iface.messageBar().INFO)

    def is_exporting(self):
        """
        Check to see if the system is still exporting (checks if there's work in the json thread pool)
        :return: True if exporting; False otherwise
        """
        return self.get_json_active_thread_count() > 0

    def is_searching(self):
        """
        Check to see if the system is still searching (checks if there's work in the search thread pool)
        :return: True if searching; False otherwise
        """
        return self.get_search_active_thread_count() > 0

    def get_search_active_thread_count(self):
        """
        Gets the number of active threads in the search thread pool
        :return:
        """
        with self.search_lock:
            return self.search_thread_pool.activeThreadCount()

    def get_json_active_thread_count(self):
        with self.json_lock:
            return self.json_thread_pool.activeThreadCount()

    def query_catalog(self, params):
        username, password, max_items_to_return = SettingsOps.get_settings()
        gbd_query = GBDQuery(username=username, password=password, client_id=username, client_secret=password)
        gbd_query.log_in()
        gbd_query.hit_test_endpoint()
        result_data = gbd_query.do_aoi_search(params)
        self.iface.messageBar().pushMessage("Blah", "result_data=" + str(result_data))
