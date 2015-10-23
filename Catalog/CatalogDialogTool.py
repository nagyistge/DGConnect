import json
from multiprocessing import Lock
import os
from qgis._core import QgsCoordinateReferenceSystem, QgsField
from qgis._gui import QgsMessageBar
from qgis.core import QgsVectorLayer, QgsMapLayerRegistry, QgsMessageLog
import re

from CatalogGBDQuery import GBDQuery, GBDOrderParams
from PyQt4.QtCore import Qt, QThreadPool, QRunnable, QObject, pyqtSlot, pyqtSignal, QVariant, QAbstractTableModel, SIGNAL
from PyQt4.QtGui import QStandardItem, QStandardItemModel, QProgressBar, QFileDialog, QSortFilterProxyModel

from ..BBox import BBoxTool
from ..Settings import SettingsOps


class CatalogDialogTool(QObject):
    """
    Tool for managing the search and export functionality
    """

    def __init__(self, iface, dialog_ui, bbox_tool):
        """
        Constructor for the dialog tool
        :param iface: The QGIS Interface
        :param dialog_base: The dialog GUI
        :return: dialog tool
        """
        QObject.__init__(self, None)
        self.iface = iface
        self.dialog_ui = dialog_ui
        self.bbox_tool = bbox_tool
        self.search_thread_pool = QThreadPool()
        self.json_thread_pool = QThreadPool()
        self.progress_message_bar = None
        self.json_progress_message_bar = None
        self.json_progress = None
        self.search_lock = Lock()
        self.json_lock = Lock()
        self.search_thread_pool = QThreadPool()
        self.json_thread_pool = QThreadPool()
        self.dialog_ui.search_button.clicked.connect(self.search_button_clicked)
        self.dialog_ui.export_button.clicked.connect(self.export_button_clicked)


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


    def search_button_clicked(self):
        """
        Validates and runs the search if validation successful
        :return: None
        """
        # can't run search during export
        if self.is_exporting():
            self.iface.messageBar().pushMessage("Error", "Cannot run search while export is running.",
                                                level=QgsMessageBar.CRITICAL)
        # can't run multiple search
        elif self.is_searching():
            self.iface.messageBar().pushMessage("Error", "Cannot run a new search while a search is running.",
                                                level=QgsMessageBar.CRITICAL)
        else:
            self.search()


    def search(self):
        errors = []
        if not self.bbox_tool.validate_bbox(errors):
            self.iface.messageBar().pushMessage("ERROR", "The following errors occurred:<br />" +
                                                       "<br />".join(errors),
                                                       level=QgsMessageBar.CRITICAL)
            return
        params = GBDOrderParams(top=self.bbox_tool.top, right=self.bbox_tool.right, bottom=self.bbox_tool.bottom, left=self.bbox_tool.left, 
                                time_begin=None, time_end=None)
        self.query_catalog(params)


    def query_catalog(self, params):
        username, password, max_items_to_return = SettingsOps.get_settings()
        gbd_query = GBDQuery(username=username, password=password, client_id=username, client_secret=password)
        gbd_query.log_in()
        gbd_query.hit_test_endpoint()
        result_data = gbd_query.do_aoi_search(params)
        
        if result_data:
            results = result_data[u"results"]
            acquisitions = []
            
            for acquisition_result in results:
                new_item = Acquisition(acquisition_result)
                acquisitions.append(new_item)
                
            model = CatalogTableModel(acquisitions, self.dialog_ui.table_view)
            self.dialog_ui.table_view.setModel(model)


    def export_button_clicked(self):
        print "not implemented"


class CatalogTableModel(QAbstractTableModel):

    def __init__(self, data, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self.data = data

    def data(self, index, role=Qt.DisplayRole): 
        if not index.isValid():
            return None
        elif role != Qt.DisplayRole:
            return None
        return self.data[index.row()].get_column_value(index.column()) 

    def rowCount(self, parent=None):
        return len(self.data)

    def columnCount(self, parent=None):
        return len(Acquisition.COLUMNS)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return Acquisition.COLUMNS[section]
        return QAbstractTableModel.headerData(self, section, orientation, role)

    def sort(self, column, order=Qt.AscendingOrder):
        self.emit(SIGNAL("layoutAboutToBeChanged()"))
        self.data = sorted(self.data, key=lambda acquisition: acquisition.get_column_value(column), reverse=(order==Qt.DescendingOrder))
        self.emit(SIGNAL("layoutChanged()"))


class Acquisition:
    """
    Entry in the GUI model of acquisitions
    """

    COLUMNS = ["Catalog ID", "Timestamp"]

    def __init__(self, result):
        """
        Constructor
        :param result: acquisition result json 
        :return: Acquisition
        """

        self.identifier = str(result[u"identifier"])

        properties = result.get(u"properties")

        self.timestamp = properties.get(u"timestamp")
        if self.timestamp:
            self.timestamp = self.timestamp[:10] # remove time because it's always 00:00:00

#         "sunElevation": "58.0927",
#         "targetAzimuth": "81.89071",
#         "browseURL": "https://browse.digitalglobe.com/imagefinder/showBrowseMetadata?catalogId=1010010003050D00",
#         "": "2004-06-15T00: 00: 00.000Z",
#         "panResolution": "0.714104414",
#         "offNadirAngle": "24.0",
#         "footprintWkt": "POLYGON((-0.09513235310.0801653768, 0.089107919620.08455198414, 0.089543398410.0238056134, 0.09000903295-0.03701337663, 0.09023406614-0.06588638216, -0.09589774085-0.0720278433, -0.09575256441-0.04281574741, -0.095448723830.01871460337, -0.09513235310.0801653768))",
#         "cloudCover": "12.0",
#         "catalogID": "1010010003050D00",
#         "sunAzimuth": "41.47571",
#         "imageBands": "Pan_MS1",
#         "sensorPlatformName": "QUICKBIRD02",
#         "multiResolution": "2.854645729",
#         "vendorName": "DigitalGlobe"

        self.column_values = []
        self.column_values.append(self.identifier)
        self.column_values.append(self.timestamp)

    def get_column_value(self, property_index):
        return self.column_values[property_index]

