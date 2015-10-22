import json
from multiprocessing import Lock
import os
from qgis._core import QgsCoordinateReferenceSystem, QgsField
from qgis._gui import QgsMessageBar
from qgis.core import QgsVectorLayer, QgsMapLayerRegistry
import re

from CatalogGBDQuery import GBDQuery, GBDOrderParams
from PyQt4.QtCore import Qt, QThreadPool, QRunnable, QObject, pyqtSlot, pyqtSignal, QVariant, QAbstractTableModel
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
#             model = self.dialog_ui.table_view.model()
#             if not model:
#                 model = CatalogTableModel(self.dialog_ui.table_view)
                
            results = result_data[u"results"]
            acquisitions = []
            
            for acquisition in results:
                identifier = str(acquisition[u"identifier"])
                
                properties = acquisition[u"properties"]
                timestamp = properties[u"timestamp"]

#                 "sunElevation": "58.0927",
#                 "targetAzimuth": "81.89071",
#                 "browseURL": "https://browse.digitalglobe.com/imagefinder/showBrowseMetadata?catalogId=1010010003050D00",
#                 "": "2004-06-15T00: 00: 00.000Z",
#                 "panResolution": "0.714104414",
#                 "offNadirAngle": "24.0",
#                 "footprintWkt": "POLYGON((-0.09513235310.0801653768, 0.089107919620.08455198414, 0.089543398410.0238056134, 0.09000903295-0.03701337663, 0.09023406614-0.06588638216, -0.09589774085-0.0720278433, -0.09575256441-0.04281574741, -0.095448723830.01871460337, -0.09513235310.0801653768))",
#                 "cloudCover": "12.0",
#                 "catalogID": "1010010003050D00",
#                 "sunAzimuth": "41.47571",
#                 "imageBands": "Pan_MS1",
#                 "sensorPlatformName": "QUICKBIRD02",
#                 "multiResolution": "2.854645729",
#                 "vendorName": "DigitalGlobe"
                
                new_item = AcquisitionItem(identifier, timestamp)
                acquisitions.append(new_item)
                
            model = CatalogTableModel(acquisitions, self.dialog_ui.table_view)
            self.dialog_ui.table_view.setModel(model)
        
        self.iface.messageBar().pushMessage("Blah", "result_data=" + str(result_data))


    def export_button_clicked(self):
        print "not implemented"


class CatalogTableModel(QAbstractTableModel):
    
    def __init__(self, data, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self.data = data
        
    def data(self, index, role): 
#         if not index.isValid():
#             return QVariant()
        return self.data[index.row()].get_property(index.column()) 
    
    def rowCount(self, parent=None):
        return len(self.data)
    
    def columnCount(self, parent=None):
        return AcquisitionItem.PROPERTIES_COUNT


class AcquisitionItem(QStandardItem):
    """
    Entry in the GUI model of acquisitions
    """
    
    PROPERTIES_COUNT = 2
    properties_dict = {}
    
    def __init__(self, identifier, timestamp, *__args):
        """
        Constructor
        :param identifier: 
        :param __args: Additional args
        :return: SourceItem
        """
        QStandardItem.__init__(self, *__args)
        self._identifier = identifier
        self.properties = [identifier, timestamp]
        self.change_text()
        self.setEditable(False)

    @property
    def identifier(self):
        return self._identifier

    @property
    def timestamp(self):
        return self.timestamp

    @timestamp.setter
    def timestamp(self, timestamp):
        self._timestamp = timestamp

    def change_text(self):
        self.setText(self._identifier)
    
    def get_property(self, property_index):
        return self.properties[property_index]

    def __hash__(self):
        return hash(self._identifier)

    def __eq__(self, other):
        return self._identifier == other.identifier

    def __ne__(self, other):
        return self._identifier != other.identifier

    def __le__(self, other):
        return self._identifier <= other.identifier

    def __lt__(self, other):
        return self._identifier < other.identifier

    def __ge__(self, other):
        return self._identifier >= other.identifier

    def __gt__(self, other):
        return self._identifier > other.identifier

    def __cmp__(self, other):
        return cmp(self._identifier, other.identifier)
