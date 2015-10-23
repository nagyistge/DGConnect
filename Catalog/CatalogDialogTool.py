# -*- coding: utf-8 -*-
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

    INCREMENTAL_INTERVAL = 1.0

    def __init__(self, iface, dialog_ui, bbox_tool):
        """
        Constructor for the dialog tool
        :param iface: The QGIS Interface
        :param dialog_ui: The dialog GUI
        :param bbox_tool The bounding box tool
        :return: dialog tool
        """
        QObject.__init__(self, None)
        self.iface = iface
        self.dialog_ui = dialog_ui
        self.bbox_tool = bbox_tool

        self.progress_message_bar = None
        self.search_thread_pool = QThreadPool()
        self.search_lock = Lock()

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

    def is_searching(self):
        """
        Check to see if the system is still searching (checks if there's work in the search thread pool)
        :return: True if searching; False otherwise
        """
        return self.get_search_active_thread_count() > 0

    def is_exporting(self):
        return False

    def get_search_active_thread_count(self):
        """
        Gets the number of active threads in the search thread pool
        :return:
        """
        with self.search_lock:
            return self.search_thread_pool.activeThreadCount()

    def search_button_clicked(self):
        """
        Validates and runs the search if validation successful
        :return: None
        """
        # can't run search during export
        if self.is_exporting():
            self.iface.messageBar().pushMessage("Error", "Cannot run search while export is running.", level=QgsMessageBar.CRITICAL)
        # can't run multiple search
        elif self.is_searching():
            self.iface.messageBar().pushMessage("Error", "Cannot run a new search while a search is running.", level=QgsMessageBar.CRITICAL)
        else:
            self.search()


    def search(self):
        self.search_thread_pool.waitForDone(0)
        username, password, max_items_to_return = SettingsOps.get_settings()
        errors = []
        SettingsOps.validate_stored_info(username, password, max_items_to_return, errors)

        if len(errors) == 0:
            self.init_progress_bar()
            # TODO reset model on subsequent searches
            model = CatalogTableModel(self.dialog_ui.table_view)
            self.dialog_ui.table_view.setModel(model)

            current_x = float(self.bbox_tool.left)
            current_y = float(self.bbox_tool.bottom)
            for next_x in self.drange(float(self.bbox_tool.left) + CatalogDialogTool.INCREMENTAL_INTERVAL, 
                                      float(self.bbox_tool.right), 
                                      CatalogDialogTool.INCREMENTAL_INTERVAL):
                for next_y in self.drange(float(self.bbox_tool.bottom) + CatalogDialogTool.INCREMENTAL_INTERVAL, 
                                          float(self.bbox_tool.top), 
                                          CatalogDialogTool.INCREMENTAL_INTERVAL):

                    acq_search_runnable = AcquisitionSearchRunnable(model, self, top=next_y, left=current_x, right=next_x, bottom=current_y)
                    ####### csv_runnable.csv_object.new_csv_element.connect(self.csv_generator_object.callback)
                    self.search_thread_pool.start(acq_search_runnable)
                    current_y = next_y
    
                current_y = self.bbox_tool.bottom
                current_x = next_x


    def search_for_acquisitions(self, params):
        acquisitions = []
        
        username, password, max_items_to_return = SettingsOps.get_settings()
        gbd_query = GBDQuery(username=username, password=password, client_id=username, client_secret=password)
        gbd_query.log_in()
        gbd_query.hit_test_endpoint()
        result_data = gbd_query.acquisition_search(params)
        
        if result_data:
            results = result_data[u"results"]
            for acquisition_result in results:
                acquisitions.append(Acquisition(acquisition_result))

        # TODO resize after all threads done
        # self.dialog_ui.table_view.resizeColumnsToContents()

        return acquisitions


    def export_button_clicked(self):
        print "not implemented"
        
    def drange(self, start, stop, step):
        r = start
        while r < stop:
            yield r
            r += step


class AcquisitionSearchRunnable(QRunnable):

    def __init__(self, model, dialog_tool, top, left, right, bottom):
        QRunnable.__init__(self)
        self.model = model
        self.dialog_tool = dialog_tool
        self.top = top
        self.left = left
        self.right = right
        self.bottom = bottom

    def run(self):
        params = GBDOrderParams(top=self.top, right=self.right, bottom=self.bottom, left=self.left, time_begin=None, time_end=None)
        new_acquisitions = self.dialog_tool.search_for_acquisitions(params)
        self.model.add_data(new_acquisitions)


class CatalogTableModel(QAbstractTableModel):

    new_data = pyqtSignal(object)

    def __init__(self, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self.data = []
        self.data_lock = Lock()

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
        with self.data_lock:
            self.emit(SIGNAL("layoutAboutToBeChanged()"))
            self.data = sorted(self.data, key=lambda acquisition: acquisition.get_column_value(column), reverse=(order==Qt.DescendingOrder))
            self.emit(SIGNAL("layoutChanged()"))

    def add_data(self, new_data):
        QgsMessageLog.instance().logMessage("new_data=" + str(new_data), "DGX")
        if new_data:
            with self.data_lock:
                self.emit(SIGNAL("layoutAboutToBeChanged()"))
                self.data.extend(new_data)
                self.emit(SIGNAL("layoutChanged()"))


class Acquisition:
    """
    Entry in the GUI model of acquisitions
    """

    COLUMNS = ["Catalog ID", "Status", "Date", "Satellite", "Vendor", "Image Band", 
               "Cloud %", "Sun Azm.", "Sun Elev.", "Multi Res.", "Pan Res.", "Off Nadir"]
    
    def __init__(self, result):
        """
        Constructor
        :param result: acquisition result json 
        :return: Acquisition
        """

        self.identifier = str(result[u"identifier"])

        properties = result.get(u"properties")

        # determine status
        available = properties.get(u"available")
        ordered = properties.get(u"ordered")
        self.status = "Available" if available else "Ordered" if ordered else "Unordered"

        # get timestamp and remove time because it's always 00:00:00
        self.timestamp = properties.get(u"timestamp")
        if self.timestamp:
            self.timestamp = self.timestamp[:10] 

        self.sensor_platform_name = properties.get(u"sensorPlatformName")
        self.vendor_name = properties.get(u"vendorName")
        self.image_bands = properties.get(u"imageBands")

        self.cloud_cover = properties.get(u"cloudCover")
        self.sun_azimuth = properties.get(u"sunAzimuth")
        self.sun_elevation = properties.get(u"sunElevation")
        self.multi_resolution = properties.get(u"multiResolution")
        self.pan_resolution = properties.get(u"panResolution")
        self.off_nadir_angle = properties.get(u"offNadirAngle")
        
        self.target_azimuth = properties.get(u"targetAzimuth")
        self.browse_url = properties.get(u"browseURL")
        self.footprint_wkt = properties.get(u"footprintWkt")

        self.column_values = [self.identifier, self.status, self.timestamp, self.sensor_platform_name, self.vendor_name, self.image_bands,
                              self.cloud_cover, self.sun_azimuth, self.sun_elevation, self.multi_resolution, self.pan_resolution, self.off_nadir_angle]

    def get_column_value(self, property_index):
        return self.column_values[property_index]

