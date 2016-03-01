# -*- coding: utf-8 -*-
import json
from multiprocessing import Lock
import os
from qgis._core import QgsCoordinateReferenceSystem, QgsField, QgsGeometry
from qgis._gui import QgsMessageBar
from qgis.core import QgsVectorLayer, QgsMapLayerRegistry, QgsMessageLog
import re
from uuid import uuid4

from CatalogAcquisition import CatalogAcquisition, CatalogAcquisitionFeature
from CatalogGBDQuery import GBDQuery, GBDOrderParams
from CatalogFilters import CatalogFilters
from PyQt4.QtCore import Qt, QThreadPool, QRunnable, QObject, pyqtSlot, pyqtSignal, QVariant, QAbstractTableModel, SIGNAL
from PyQt4.QtGui import QStandardItem, QStandardItemModel, QItemSelectionModel, QProgressBar, QFileDialog, QSortFilterProxyModel, QFileDialog

from ..BBox import BBoxTool
from ..Settings import SettingsOps
from _sqlite3 import Row


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
        self.progress_message_bar_widget = None
        self.search_thread_pool = QThreadPool()
        self.search_lock = Lock()
        self.export_thread_pool = QThreadPool()
        self.export_lock = Lock()
        self.query = None
        self.previous_credentials = None
        self.export_file = None
        self.footprint_layer = None

        self.filters = CatalogFilters(self.dialog_ui)

        self.dialog_ui.aoi_button.clicked.connect(self.aoi_button_clicked)
        self.dialog_ui.reset_button.clicked.connect(self.reset_button_clicked)
        self.dialog_ui.export_button.clicked.connect(self.export_button_clicked)
        self.bbox_tool.released.connect(self.search)
        self.model = None

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
            self.progress_message_bar_widget = self.iface.messageBar().pushWidget(self.progress_message_bar, self.iface.messageBar().INFO)

    def init_layers(self):
        """
        Sets up the layers for rendering the items
        :return: None
        """
        if self.footprint_layer:
            QgsMapLayerRegistry.instance().removeMapLayer(self.footprint_layer.id())

        self.footprint_layer = QgsVectorLayer("Polygon?crs=EPSG:4326", "DGX Catalog Footprints", "memory")
        self.footprint_layer.setCrs(QgsCoordinateReferenceSystem(4326), True)
        self.footprint_layer.dataProvider().addAttributes(CatalogAcquisitionFeature.get_fields())
        QgsMapLayerRegistry.instance().addMapLayer(self.footprint_layer)

    def clear_widgets(self):
        """
        Clears the progress bar
        :return: None
        """
        self.progress_bar = None
        self.progress_message_bar = None
        if self.progress_message_bar_widget:
            self.iface.messageBar().popWidget(self.progress_message_bar_widget)
        self.progress_message_bar_widget = None

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

    def aoi_button_clicked(self):
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
            self.bbox_tool.reset()
            self.iface.mapCanvas().setMapTool(self.bbox_tool)

    def reset_button_clicked(self):
        """
        Resets filters.
        :return: None
        """
        self.reset()

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

    def search(self, top, bottom, left, right):
        self.search_thread_pool.waitForDone(0)

        # validate credentials if they changed
        errors = []
        username, password, api_key, max_items_to_return = SettingsOps.get_settings()
        credentials = [username, password, api_key]
        if not self.previous_credentials or self.previous_credentials != credentials:
            SettingsOps.validate_stored_info(username, password, api_key, max_items_to_return, errors)
        self.previous_credentials = credentials

        # validate filters
        if not errors:
            self.filters.validate(errors)

        if errors:
            self.iface.messageBar().pushMessage("Error", "The following errors occurred: " + "<br />".join(errors), level=QgsMessageBar.CRITICAL)
        else:
            self.init_layers()

            self.dialog_ui.tab_widget.setCurrentIndex(RESULTS_TAB_INDEX)
            
            next_x_list = self.drange_list(float(left) + INCREMENTAL_INTERVAL, float(right), INCREMENTAL_INTERVAL)
            next_y_list = self.drange_list(float(bottom) + INCREMENTAL_INTERVAL, float(top), INCREMENTAL_INTERVAL)
            self.init_progress_bar(len(next_x_list) * len(next_y_list))

            self.model = CatalogTableModel(self.dialog_ui.table_view)
            self.dialog_ui.table_view.setModel(self.model)
            self.dialog_ui.table_view.selectionModel().selectionChanged.connect(self.selection_changed)

            if not self.query:
                self.query = GBDQuery(username=username, password=password, api_key=api_key)

            filters = self.filters.get_query_filters()
            time_begin = self.filters.get_datetime_begin()
            time_end = self.filters.get_datetime_end()

            current_x = float(left)
            current_y = float(bottom)
            for next_x in next_x_list:
                for next_y in next_y_list:
                    search_runnable = CatalogSearchRunnable(self.query, self.model, self, top=next_y, left=current_x, right=next_x, bottom=current_y, 
                                                            time_begin=time_begin, time_end=time_end, filters=filters)
                    search_runnable.task_object.task_complete.connect(self.on_search_complete)
                    self.search_thread_pool.start(search_runnable)
                    current_y = next_y
                current_y = bottom
                current_x = next_x

    def reset(self):
        self.filters.remove_all()

    def export(self):
        self.export_thread_pool.waitForDone(0)
        acquisitions = None
        if self.model is not None:
            acquisitions = self.model.data

        if not acquisitions:
            self.iface.messageBar().pushMessage("Error", "No data to export.", level=QgsMessageBar.CRITICAL)
        else:
            # open file ui
            select_file_ui = QFileDialog()
            starting_file = self.export_file or os.path.expanduser("~")
            export_file = select_file_ui.getSaveFileName(None, "Choose output file", starting_file, SELECT_FILTER)

            if export_file:
                self.export_file = export_file
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

    def selection_changed(self, selected, deselected):
        self.footprint_layer.startEditing()

        # draw footprints for selected rows
        selected_rows = set()
        for index in selected.indexes():
            selected_rows.add(index.row())
        for row in selected_rows:
            acquisition = self.model.get(row)
            feature_id = self.model.generate_feature_id()
            self.model.set_feature_id(acquisition, feature_id)
            feature = CatalogAcquisitionFeature(feature_id, acquisition)
            self.footprint_layer.dataProvider().addFeatures([feature])

        # remove footprints for deselected rows
        deselected_rows = set()
        for index in deselected.indexes():
            deselected_rows.add(index.row())
        feature_ids_to_remove = []
        for row in deselected_rows:
            acquisition = self.model.get(row)
            feature_id = self.model.get_feature_id(acquisition)
            feature_ids_to_remove.append(feature_id)
            self.model.remove_feature_id(acquisition)
        if feature_ids_to_remove:
            self.footprint_layer.dataProvider().deleteFeatures(feature_ids_to_remove)

        self.footprint_layer.commitChanges()
        self.footprint_layer.updateExtents()
        self.footprint_layer.triggerRepaint()

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

    def __init__(self, query, model, dialog_tool, top, left, right, bottom, time_begin, time_end, filters):
        QRunnable.__init__(self)
        self.query = query
        self.model = model
        self.dialog_tool = dialog_tool
        self.top = top
        self.left = left
        self.right = right
        self.bottom = bottom
        self.time_begin = time_begin
        self.time_end = time_end
        self.filters = filters
        self.task_object = CatalogTaskObject()

    def run(self):
        params = GBDOrderParams(top=self.top, right=self.right, bottom=self.bottom, left=self.left, 
                                time_begin=self.time_begin, time_end=self.time_end, filters=self.filters)
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
        self.cat_ids = {}
        self.data_lock = Lock()
        self.feature_ids = {}
        self.feature_id_seq = 0

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
            return CatalogAcquisition.COLUMNS[section].name
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
                for acquisition in new_data:
                    if not self.cat_ids.get(acquisition.identifier, None):
                        self.data.append(acquisition)
                        self.cat_ids[acquisition.identifier] = True
                self.emit(SIGNAL("layoutChanged()"))

    def get(self, index):
        return self.data[index]

    def get_feature_id(self, acquisition):
        return self.feature_ids[acquisition.identifier]

    def set_feature_id(self, acquisition, feature_id):
        self.feature_ids[acquisition.identifier] = feature_id

    def remove_feature_id(self, acquisition):
        del self.feature_ids[acquisition.identifier]

    def generate_feature_id(self):
        self.feature_id_seq += 1
        return self.feature_id_seq

