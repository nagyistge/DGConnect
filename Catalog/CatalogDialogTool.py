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
        self.query = None
        self.previous_credentials = None

        self.dialog_ui.search_button.clicked.connect(self.search_button_clicked)
        self.dialog_ui.export_button.clicked.connect(self.export_button_clicked)

    def init_progress_bar(self, progress_max):
        """
        Sets up the progress bar for search functionality
        :return: None
        """
        if not self.progress_message_bar:
            self.progress_message_bar = self.iface.messageBar().createMessage("Querying for data")
            self.progress_bar = QProgressBar()
            self.progress_bar.setMinimum(0)
            self.progress_bar.setMaximum(progress_max)
            self.progress_bar.setAlignment(Qt.AlignLeft | Qt.AlignCenter)
            self.progress_message_bar.layout().addWidget(self.progress_bar)
            self.iface.messageBar().pushWidget(self.progress_message_bar, self.iface.messageBar().INFO)

    def clear_widgets(self):
        """
        Clears the progress bar for the UVI searches
        :return: None
        """
        self.progress_bar = None
        self.progress_message_bar = None
        self.iface.messageBar().clearWidgets()

    @pyqtSlot()
    def on_acquisition_search_complete(self):
        thread_count = self.get_search_active_thread_count()
        if self.progress_message_bar:
            self.progress_bar.setValue(self.progress_bar.value() + 1)
        if thread_count == 0:
            self.clear_widgets()
            self.dialog_ui.table_view.resizeColumnsToContents()

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

        # validate credentials if credentials changed
        settings_errors = []
        username, password, max_items_to_return = SettingsOps.get_settings()
        credentials = [username, password]
        if not self.previous_credentials or self.previous_credentials != credentials:
            SettingsOps.validate_stored_info(username, password, max_items_to_return, settings_errors)
        self.previous_credentials = credentials

        if len(settings_errors) == 0:
            next_x_list = self.drange_list(float(self.bbox_tool.left) + CatalogDialogTool.INCREMENTAL_INTERVAL, 
                                      float(self.bbox_tool.right), 
                                      CatalogDialogTool.INCREMENTAL_INTERVAL)
            next_y_list = self.drange_list(float(self.bbox_tool.bottom) + CatalogDialogTool.INCREMENTAL_INTERVAL, 
                                      float(self.bbox_tool.top), 
                                      CatalogDialogTool.INCREMENTAL_INTERVAL)
            self.init_progress_bar(len(next_x_list) * len(next_y_list))

            # TODO reset model on subsequent searches
            model = CatalogTableModel(self.dialog_ui.table_view)
            self.dialog_ui.table_view.setModel(model)
            if not self.query:
                self.query = GBDQuery(username=username, password=password, client_id=username, client_secret=password)

            current_x = float(self.bbox_tool.left)
            current_y = float(self.bbox_tool.bottom)
            for next_x in next_x_list:
                for next_y in next_y_list:
                    acq_search_runnable = AcquisitionSearchRunnable(self.query, model, self, top=next_y, left=current_x, right=next_x, bottom=current_y)
                    acq_search_runnable.acquisition_search_object.task_complete.connect(self.on_acquisition_search_complete)
                    self.search_thread_pool.start(acq_search_runnable)
                    current_y = next_y
                current_y = self.bbox_tool.bottom
                current_x = next_x

    def export_button_clicked(self):
        print "not implemented"

    def drange_list(self, start, stop, step):
        drange_list = []
        r = start
        while r < stop:
            drange_list.append(r)
            r += step
        return drange_list


class AcquisitionSearchObject(QObject):
    """
    QObject for holding the signal
    """
    task_complete = pyqtSignal()

    def __init__(self, QObject_parent=None):
        QObject.__init__(self, QObject_parent)


class AcquisitionSearchRunnable(QRunnable):

    def __init__(self, query, model, dialog_tool, top, left, right, bottom):
        QRunnable.__init__(self)
        self.query = query
        self.model = model
        self.dialog_tool = dialog_tool
        self.top = top
        self.left = left
        self.right = right
        self.bottom = bottom
        self.acquisition_search_object = AcquisitionSearchObject()

    def run(self):
        params = GBDOrderParams(top=self.top, right=self.right, bottom=self.bottom, left=self.left, time_begin=None, time_end=None)
        result_data = self.query.acquisition_search(params)

        if result_data:
            acquisitions = []
            results = result_data[u"results"]
            for acquisition_result in results:
                acquisitions.append(Acquisition(acquisition_result))
            self.model.add_data(acquisitions)
        self.acquisition_search_object.task_complete.emit()


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

