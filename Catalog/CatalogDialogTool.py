# -*- coding: utf-8 -*-
import json
from multiprocessing import Lock
import os
from qgis._core import QgsCoordinateReferenceSystem, QgsField
from qgis._gui import QgsMessageBar
from qgis.core import QgsVectorLayer, QgsMapLayerRegistry, QgsMessageLog
import re
from uuid import uuid4

from CatalogAcquisition import CatalogAcquisition
from CatalogGBDQuery import GBDQuery, GBDOrderParams
from CatalogFilters import CatalogFilters
from PyQt4.QtCore import Qt, QThreadPool, QRunnable, QObject, pyqtSlot, pyqtSignal, QVariant, QAbstractTableModel, SIGNAL
from PyQt4.QtGui import QStandardItem, QStandardItemModel, QProgressBar, QFileDialog, QSortFilterProxyModel, QFileDialog

from ..BBox import BBoxTool
from ..Settings import SettingsOps


INCREMENTAL_INTERVAL = 1.0

DEFAULT_SUFFIX = "csv"
SELECT_FILTER = "CSV Files(*.csv)"

RESULTS_TAB_INDEX = 1
FILTER_COLUMN_INDEX_WHERE = 0
FILTER_COLUMN_INDEX_LABEL = 1
FILTER_COLUMN_INDEX_VALUE = 2
FILTER_COLUMN_INDEX_ADD = 3


class CatalogDialogTool(QObject):
    """
    Tool for managing the search and export functionality
    """

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

        self.progress_bar = None
        self.progress_message_bar = None
        self.search_thread_pool = QThreadPool()
        self.search_lock = Lock()
        self.export_thread_pool = QThreadPool()
        self.export_lock = Lock()
        self.query = None
        self.previous_credentials = None
        self.export_file = None

        self.filters = CatalogFilters(self.dialog_ui)
        self.filters.add_filter()

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

    def is_searching(self):
        """
        Check to see if the system is still searching (checks if there's work in the search thread pool)
        :return: True if searching; False otherwise
        """
        return self.get_search_active_thread_count() > 0

    def is_exporting(self):
        """
        Check to see if the system is still exporting (checks if there's work in the export thread pool)
        :return: True if searching; False otherwise
        """
        return self.get_export_active_thread_count() > 0

    def get_search_active_thread_count(self):
        """
        Gets the number of active threads in the search thread pool
        :return:
        """
        with self.search_lock:
            return self.search_thread_pool.activeThreadCount()

    def get_export_active_thread_count(self):
        """
        Gets the number of active threads in the export thread pool
        :return:
        """
        with self.export_lock:
            return self.export_thread_pool.activeThreadCount()

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

    def export_button_clicked(self):
        """
        Validates and runs the export if validation successful
        :return: None
        """
        # can't run export during search
        if self.is_searching():
            self.iface.messageBar().pushMessage("Error", "Cannot run export while search is running.", level=QgsMessageBar.CRITICAL)
        # can't run multiple exports
        elif self.is_exporting():
            self.iface.messageBar().pushMessage("Error", "Cannot run a new export while a export is running.", level=QgsMessageBar.CRITICAL)
        else:
            self.export()

    def search(self):
        self.search_thread_pool.waitForDone(0)

        # validate credentials if they changed
        settings_errors = []
        username, password, max_items_to_return = SettingsOps.get_settings()
        credentials = [username, password]
        if not self.previous_credentials or self.previous_credentials != credentials:
            SettingsOps.validate_stored_info(username, password, max_items_to_return, settings_errors)
        self.previous_credentials = credentials

        if len(settings_errors) == 0:
            self.dialog_ui.tab_widget.setCurrentIndex(RESULTS_TAB_INDEX)
            
            next_x_list = self.drange_list(float(self.bbox_tool.left) + INCREMENTAL_INTERVAL, float(self.bbox_tool.right), INCREMENTAL_INTERVAL)
            next_y_list = self.drange_list(float(self.bbox_tool.bottom) + INCREMENTAL_INTERVAL, float(self.bbox_tool.top), INCREMENTAL_INTERVAL)
            self.init_progress_bar(len(next_x_list) * len(next_y_list))

            # TODO reset model on subsequent searches
            self.model = CatalogTableModel(self.dialog_ui.table_view)
            self.dialog_ui.table_view.setModel(self.model)
            filters = self.filters.get_request_filters()
            if not self.query:
                self.query = GBDQuery(username=username, password=password, client_id=username, client_secret=password)

            current_x = float(self.bbox_tool.left)
            current_y = float(self.bbox_tool.bottom)
            for next_x in next_x_list:
                for next_y in next_y_list:
                    search_runnable = CatalogSearchRunnable(self.query, self.model, self, top=next_y, left=current_x, right=next_x, bottom=current_y, filters=filters)
                    search_runnable.task_object.task_complete.connect(self.on_search_complete)
                    self.search_thread_pool.start(search_runnable)
                    current_y = next_y
                current_y = self.bbox_tool.bottom
                current_x = next_x

    def export(self):
        self.export_thread_pool.waitForDone(0)
        acquisitions = None
        if self.model:
            acquisitions = self.model.data

        if not acquisitions:
            self.iface.messageBar().pushMessage("Error", "No data to export.", level=QgsMessageBar.CRITICAL)
        else:
            # open file ui
            select_file_ui = QFileDialog()
            starting_file = self.export_file or os.path.expanduser("~")
            self.export_file = select_file_ui.getSaveFileName(None, "Choose output file", starting_file, SELECT_FILTER)

            self.init_progress_bar(0)
            export_runnable = CatalogExportRunnable(acquisitions, self.export_file)
            export_runnable.task_object.task_complete.connect(self.on_export_complete)
            self.export_thread_pool.start(export_runnable)

    @pyqtSlot()
    def on_search_complete(self):
        thread_count = self.get_search_active_thread_count()
        if self.progress_message_bar:
            self.progress_bar.setValue(self.progress_bar.value() + 1)
        if thread_count == 0:
            self.clear_widgets()
            self.dialog_ui.table_view.resizeColumnsToContents()

    @pyqtSlot()
    def on_export_complete(self):
        thread_count = self.get_export_active_thread_count()
        if self.progress_message_bar:
            self.progress_bar.setValue(self.progress_bar.value() + 1)
        if thread_count == 0:
            self.clear_widgets()
            self.iface.messageBar().pushMessage("Info", 'File export has completed to "%s".' % self.export_file)

    def drange_list(self, start, stop, step):
        drange_list = []
        r = start
        while r < stop:
            drange_list.append(r)
            r += step
        if not drange_list:
            drange_list.append(stop)
        return drange_list


class CatalogTaskObject(QObject):
    """
    QObject for holding the signal
    """
    task_complete = pyqtSignal()

    def __init__(self, QObject_parent=None):
        QObject.__init__(self, QObject_parent)


class CatalogSearchRunnable(QRunnable):

    def __init__(self, query, model, dialog_tool, top, left, right, bottom, filters):
        QRunnable.__init__(self)
        self.query = query
        self.model = model
        self.dialog_tool = dialog_tool
        self.top = top
        self.left = left
        self.right = right
        self.bottom = bottom
        self.filters = filters
        self.task_object = CatalogTaskObject()

    def run(self):
        params = GBDOrderParams(top=self.top, right=self.right, bottom=self.bottom, left=self.left, time_begin=None, time_end=None, filters=self.filters)
        result_data = self.query.acquisition_search(params)

        if result_data:
            acquisitions = []
            results = result_data[u"results"]
            for acquisition_result in results:
                acquisitions.append(CatalogAcquisition(acquisition_result))
            self.model.add_data(acquisitions)
        self.task_object.task_complete.emit()


class CatalogExportRunnable(QRunnable):

    def __init__(self, acquisitions, export_filename):
        QRunnable.__init__(self)
        self.task_object = CatalogTaskObject()
        self.acquisitions = acquisitions
        self.export_filename = export_filename

    def run(self):
        export_file = open(self.export_filename, 'w')

        header = CatalogAcquisition.get_csv_header()
        export_file.write(header)
        export_file.write("\n")

        for acquisition in self.acquisitions:
            export_file.write(str(acquisition))
            export_file.write("\n")

        export_file.close()
        self.task_object.task_complete.emit()


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
        return len(CatalogAcquisition.COLUMNS)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return CatalogAcquisition.COLUMNS[section]
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

