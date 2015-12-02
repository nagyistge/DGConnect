import json
from multiprocessing import Lock
from qgis._core import QgsCoordinateReferenceSystem, QgsField
from qgis._gui import QgsMessageBar

__author__ = 'mtrotter'

import VectorsProcessForm
from VectorsQuery import VectorsSourcesParams, VectorsGeometriesParams, VectorsTypesParams,\
    VectorQuery, VectorsItemsParams, KEY_JSON_PROPERTIES_LIST

from PyQt4.QtGui import QStandardItem, QStandardItemModel, QProgressBar, QFileDialog, QSortFilterProxyModel
from PyQt4.QtCore import Qt, QThreadPool, QRunnable, QObject, pyqtSlot, pyqtSignal, QVariant
from qgis.core import QgsMessageLog, QgsVectorLayer, QgsMapLayerRegistry
from ..Settings import SettingsOps

import os
import re

DEFAULT_LEFT = "-180.0"
DEFAULT_RIGHT = "180.0"
DEFAULT_TOP = "90.0"
DEFAULT_BOTTOM = "-90.0"


DEFAULT_ORDER_PARAMS = VectorsSourcesParams(top=DEFAULT_TOP, bottom=DEFAULT_BOTTOM, left=DEFAULT_LEFT, right=DEFAULT_RIGHT)

WIDGET_TEXT_FMT = "%s (%d)"

KEY_COUNT = "count"
KEY_GEOMETRY = "geometry"
KEY_ENABLED = "enabled"

KEY_POINT = "Point"
KEY_MULTI_POINT = "MultiPoint"
KEY_POLYGON = "Polygon"
KEY_LINE = "Line"

KEY_ESRI_GEOMETRY_POINT = u'Point'
KEY_ESRI_GEOMETRY_MULTI_POINT = u'MultiPoint'
KEY_ESRI_GEOMETRY_POLYLINE = u'PolyLine'
KEY_ESRI_GEOMETRY_POLYGON = u'Polygon'

FILE_POINTS = u'points.json'
FILE_POLYGON = u'polygon.json'
FILE_LINE = u'line.json'

GEOJSON_BEGINNING = '{"type": "FeatureCollection", "features": ['
GEOJSON_ENDING = '\n]}'

REGEX_DIGITS = re.compile("\((\d+)\)$")

class VectorsDialogTool(QObject):
    """
    Tool for managing the search and export functionality
    """

    def clear_widgets(self):
        """
        Clears the progress bar
        :return: None
        """
        self.progress_message_bar = None
        self.iface.messageBar().clearWidgets()

    def on_sort_complete(self):
        """
        Callback function for searches; will clear dialogs if the searches are done
        :return: None
        """
        if self.get_search_active_thread_count() == 0:
            self.clear_widgets()

    def on_task_complete(self):
        """
        Callback function for when a search item is done processing; checks to see if the searches are before
        processing
        :return: None
        """
        if self.get_search_active_thread_count() == 0:
            source_model = self.dialog_base.data_sources_list_view.model()
            if source_model:
                source_thread = SortRunnable(source_model)
                source_thread.sort_object.task_complete.connect(self.on_sort_complete)
                self.search_thread_pool.start(source_thread)
            geometry_model = self.dialog_base.geometry_list_view.model()
            if geometry_model:
                geometry_thread = SortRunnable(geometry_model)
                geometry_thread.sort_object.task_complete.connect(self.on_sort_complete)
                self.search_thread_pool.start(geometry_thread)
            types_model = self.dialog_base.types_list_view.model()
            if types_model:
                type_thread = SortRunnable(types_model)
                type_thread.sort_object.task_complete.connect(self.on_sort_complete)
                self.search_thread_pool.start(type_thread)

    @pyqtSlot(object, object)
    def on_new_source(self, source_params, new_sources):
        """
        Callback for a new source; inserts it to the sources list view
        :param source_params: VectorsSourcesParams holding the search params for the sources
        :param new_sources: The new source data in a dictionary
        :return: None
        """
        if new_sources:
            new_model = False
            model = self.dialog_base.data_sources_list_view.model()
            if not model:
                model = QStandardItemModel(self.dialog_base.data_sources_list_view)
                new_model = True
            for key, count in new_sources.iteritems():
                if key in self.sources:
                    self.sources[key].count = count
                else:
                    new_item = SourceItem(key, source_params, count)
                    new_item.setCheckable(True)
                    new_item.setCheckState(Qt.Checked)
                    model.appendRow(new_item)
                    self.sources[key] = new_item
                geometry_params = VectorsGeometriesParams(source_params, key)
                self.query_geometries(geometry_params)
            if new_model:
                model.itemChanged.connect(self.on_source_checked)
                self.dialog_base.data_sources_list_view.setModel(model)
        self.on_task_complete()

    @pyqtSlot(object, object)
    def on_new_geometries(self, geometry_params, new_geometries):
        """
        Callback function for new geometries; adds it to the UI
        :param geometry_params: VectorsGeometriesParams holding the search params for the geometries
        :param new_geometries: The new geometry data in a dictionary
        :return: None
        """
        if new_geometries:
            new_model = False
            model = self.dialog_base.geometry_list_view.model()
            if not model:
                model = QStandardItemModel(self.dialog_base.geometry_list_view)
                new_model = True
            for key, count in new_geometries.iteritems():
                if key in self.geometries:
                    self.geometries[key].update_count(geometry_params.source, count)
                else:
                    geometry_item = GeometryItem(key)
                    geometry_item.update_count(geometry_params.source, count)
                    geometry_item.setCheckable(True)
                    geometry_item.setCheckState(Qt.Checked)
                    model.appendRow(geometry_item)
                    self.geometries[key] = geometry_item
                if key not in self.sources[geometry_params.source].geometries:
                    self.sources[geometry_params.source].geometries[key] = self.geometries[key]
                types_params = VectorsTypesParams(geometry_params, key)
                self.query_types(types_params)
            if new_model:
                model.itemChanged.connect(self.on_geometry_check)
                self.dialog_base.geometry_list_view.setModel(model)
        self.on_task_complete()

    @pyqtSlot(object, object)
    def on_new_types(self, types_params, new_types):
        """
        Callback function for adding new types to the UI
        :param types_params: The VectorsTypesParams used for running the search
        :param new_types: The new types data in a dictionary
        :return: None
        """
        if new_types:
            new_model = False
            model = self.dialog_base.types_list_view.model()
            if not model:
                source_model = QStandardItemModel(self.dialog_base.types_list_view)
                model = TypesModel(self.dialog_base.types_list_view)
                model.setSourceModel(source_model)
                model.setDynamicSortFilter(True)
                new_model = True
            for key, count in new_types.iteritems():
                if key in self.types_dict:
                    self.types_dict[key].update_count(types_params.source, types_params.geometry, count)
                else:
                    type_item = TypesItem(key)
                    type_item.update_count(types_params.source, types_params.geometry, count)
                    type_item.setCheckable(True)
                    type_item.setCheckState(Qt.Checked)
                    model.sourceModel().appendRow(type_item)
                    self.types_dict[key] = type_item
                if key not in self.sources[types_params.source].type_entries:
                    self.sources[types_params.source].type_entries[key] = self.types_dict[key]
                if key not in self.geometries[types_params.geometry].type_entries:
                    self.geometries[types_params.geometry].type_entries[key] = self.types_dict[key]
                # source = types_params.source
                # self.start_new_item(source, key, types_params)
            if new_model:
                source_model.itemChanged.connect(self.on_type_check)
                self.dialog_base.types_list_view.setModel(model)
        self.on_task_complete()

    def start_new_item(self, source, type_key, type_params):
        """
        Function for testing if a new type query should be run; tests if the source and type have already been run
        :param source: The source name to use for the query
        :param type_key: The type name to use for the query
        :param type_params: The parameters from the type search
        :return: None
        """
        should_add = False
        if source not in self.items.keys():
            should_add = True
            self.items[source] = {}
        if type_key not in self.items[source].keys():
            should_add = True
            self.items[source][type_key] = []
        if should_add:
            username, password, max_items_to_return = SettingsOps.get_settings()
            item_params = VectorsItemsParams(type_params.sources_params,
                                                  source, type_key)
            item_runnable = ItemRunnable(username, password, username, password, item_params)
            item_runnable.item_object.task_complete.connect(self.on_new_items)
            self.search_thread_pool.start(item_runnable)

    @pyqtSlot(object, object)
    def on_new_items(self, items_params, new_items):
        """
        Callback function for adding new items to the UI (not scalable)
        :param items_params: The VectorsItemsParams used for the item query
        :param new_items: The dictionary holding the list of ItemFeatures broken up by geometry
        :return: None
        """
        if new_items:
            self.point_vector_layer.startEditing()
            self.line_vector_layer.startEditing()
            self.polygon_vector_layer.startEditing()

            point_data_provider = self.point_vector_layer.dataProvider()
            line_data_provider = self.line_vector_layer.dataProvider()
            polygon_data_provider = self.polygon_vector_layer.dataProvider()

            if KEY_ESRI_GEOMETRY_POINT in self.geometries and self.geometries[KEY_ESRI_GEOMETRY_POINT].is_checked:
                point_data_provider.addFeatures(new_items[KEY_POINT])
            if KEY_ESRI_GEOMETRY_MULTI_POINT in self.geometries and \
                    self.geometries[KEY_ESRI_GEOMETRY_MULTI_POINT].is_checked:
                point_data_provider.addFeatures(new_items[KEY_MULTI_POINT])
            if KEY_ESRI_GEOMETRY_POLYLINE in self.geometries and self.geometries[KEY_ESRI_GEOMETRY_POLYLINE].is_checked:
                line_data_provider.addFeatures(new_items[KEY_LINE])
            if KEY_ESRI_GEOMETRY_POLYGON in self.geometries and self.geometries[KEY_ESRI_GEOMETRY_POLYGON].is_checked:
                polygon_data_provider.addFeatures(new_items[KEY_POLYGON])

            self.point_vector_layer.commitChanges()
            self.point_vector_layer.updateExtents()

            self.line_vector_layer.commitChanges()
            self.line_vector_layer.updateExtents()

            self.polygon_vector_layer.commitChanges()
            self.polygon_vector_layer.updateExtents()

            self.items[items_params.source][items_params.type_name] += new_items
        self.on_task_complete()

    @pyqtSlot(object, object)
    def on_new_json_items(self, items_params, new_items=None):
        """
        Callback function for adding new json items to the exported GeoJSON files
        :param items_params: The parameters used for the query
        :param new_items: The dictionary holding the lists of json strings to add; broken up by geometry type
        :return: None
        """
        if self.json_progress_message_bar:
            self.json_progress.setValue(self.json_progress.value() + 1)
        if new_items:
            if KEY_ESRI_GEOMETRY_POLYGON in self.geometries and self.geometries[KEY_ESRI_GEOMETRY_POLYGON].is_checked:
                for polygon in new_items[KEY_POLYGON]:
                    self.write_to_file(FILE_POLYGON, u"\n")
                    if self.written_first_polygon:
                        self.write_to_file(FILE_POLYGON, u",")
                    else:
                        self.written_first_polygon = True
                    self.write_to_file(FILE_POLYGON, polygon)
            if KEY_ESRI_GEOMETRY_POLYLINE in self.geometries and self.geometries[KEY_ESRI_GEOMETRY_POLYLINE].is_checked:
                for line in new_items[KEY_LINE]:
                    self.write_to_file(FILE_LINE, u"\n")
                    if self.written_first_line:
                        self.write_to_file(FILE_LINE, u",")
                    else:
                        self.written_first_line = True
                    self.write_to_file(FILE_LINE, line)
            if KEY_ESRI_GEOMETRY_POINT in self.geometries and self.geometries[KEY_ESRI_GEOMETRY_POINT].is_checked:
                for point in new_items[KEY_POINT]:
                    self.write_to_file(FILE_POINTS, u"\n")
                    if self.written_first_point:
                        self.write_to_file(FILE_POINTS, u",")
                    else:
                        self.written_first_point = True
                    self.write_to_file(FILE_POINTS, point)
            if KEY_ESRI_GEOMETRY_MULTI_POINT in self.geometries and\
                    self.geometries[KEY_ESRI_GEOMETRY_MULTI_POINT].is_checked:
                for point in new_items[KEY_MULTI_POINT]:
                    self.write_to_file(FILE_POINTS, u"\n")
                    if self.written_first_point:
                        self.write_to_file(FILE_POINTS, u",")
                    else:
                        self.written_first_point = True
                    self.write_to_file(FILE_POINTS, point)

        self.on_new_json_task_complete()

    def on_new_json_task_complete(self):
        """
        Callback function for testing if we're done with the GeoJSON export
        (probably not since the timeouts can take awhile)
        Resets the UI when it is actually done
        :return: None
        """
        if self.get_json_active_thread_count() > 0:
            self.json_progress.setValue(self.json_progress.value() + 1)
        else:
            # remove progress bar
            self.json_progress_message_bar = None
            self.json_progress = None
            self.iface.messageBar().clearWidgets()

            if self.json_failed:
                self.iface.messageBar().pushMessage("Error", "Error encountered during export.", level=QgsMessageBar.CRITICAL)
            else:
                self.close_file(FILE_POLYGON)
                self.close_file(FILE_LINE)
                self.close_file(FILE_POINTS)
                self.iface.messageBar().pushMessage("Info", "File export has completed to directory %s." % self.directory)

            # update tool
            self.file_dict = {}
            self.written_first_line = False
            self.written_first_point = False
            self.written_first_polygon = False

    @pyqtSlot(object)
    def cancel_json_threads(self, exception):
        self.json_failed = True

    def __init__(self, iface, dialog_base, bbox_tool):
        """
        Constructor for the DialogTool
        :param iface: The QGIS Interface
        :param dialog_base: The Dialog GUI
        :return: DialogTool
        """
        QObject.__init__(self, None)
        self.iface = iface
        self.dialog_base = dialog_base
        self.bbox_tool = bbox_tool
        self.sources = {}
        self.geometries = {}
        self.types_dict = {}
        self.items = {}
        self.search_thread_pool = QThreadPool()
        self.json_thread_pool = QThreadPool()
        self.progress_message_bar = None
        self.json_progress_message_bar = None
        self.json_progress = None
        self.json_failed = False
        self.point_vector_layer = None
        self.line_vector_layer = None
        self.polygon_vector_layer = None
        self.dialog_base.aoi_button.clicked.connect(self.aoi_button_clicked)
        self.dialog_base.export_button.clicked.connect(self.export)
        self.bbox_tool.released.connect(self.search)
        # self.query_initial_sources()
        self.file_dict = {}
        self.directory = None
        self.written_first_line = False
        self.written_first_point = False
        self.written_first_polygon = False
        # locks
        self.search_lock = Lock()
        self.json_lock = Lock()

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

    def init_vector_layers(self):
        """
        Sets up the vector layers for rendering the items
        :return: None
        """
        if self.point_vector_layer:
            QgsMapLayerRegistry.instance().removeMapLayer(self.point_vector_layer.id())
        if self.line_vector_layer:
            QgsMapLayerRegistry.instance().removeMapLayer(self.line_vector_layer.id())
        if self.polygon_vector_layer:
            QgsMapLayerRegistry.instance().removeMapLayer(self.polygon_vector_layer.id())

        self.point_vector_layer = QgsVectorLayer(KEY_POINT, "Vector Items (Points)", "memory")
        self.point_vector_layer.setCrs(QgsCoordinateReferenceSystem(4326), False)
        QgsMapLayerRegistry.instance().addMapLayer(self.point_vector_layer)

        self.line_vector_layer = QgsVectorLayer(KEY_LINE, "Vector Items (Lines)", "memory")
        self.line_vector_layer.setCrs(QgsCoordinateReferenceSystem(4326), False)
        QgsMapLayerRegistry.instance().addMapLayer(self.line_vector_layer)

        self.polygon_vector_layer = QgsVectorLayer(KEY_POLYGON, "Vector Items (Polygons)", "memory")
        self.polygon_vector_layer.setCrs(QgsCoordinateReferenceSystem(4326), False)
        QgsMapLayerRegistry.instance().addMapLayer(self.polygon_vector_layer)

        point_data_provider = self.point_vector_layer.dataProvider()
        line_data_provider = self.line_vector_layer.dataProvider()
        polygon_data_provider = self.polygon_vector_layer.dataProvider()

        attribute_fields = []
        for attribute in KEY_JSON_PROPERTIES_LIST:
            attribute_fields.append(QgsField(u'vector_' + attribute, QVariant.String))

        point_data_provider.addAttributes(attribute_fields)
        line_data_provider.addAttributes(attribute_fields)
        polygon_data_provider.addAttributes(attribute_fields)

    def aoi_button_clicked(self):
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
            self.bbox_tool.reset()
            self.iface.mapCanvas().setMapTool(self.bbox_tool)

    def search(self, top, bottom, left, right):
        """
        Action performed when the ok button is clicked
        :param bbox_tool: The bounding box tool
        :param dialog_tool: The dialog tool
        :return: None
        """
        params = VectorsSourcesParams(top=top, right=right, bottom=bottom, left=left, query=None)
        self.query_sources(params)

    def query_initial_sources(self):
        """
        Queries the sources on load (not used)
        :return: None
        """
        self.search_thread_pool.waitForDone(0)
        # self.init_vector_layers()
        username, password, max_items_to_return = SettingsOps.get_settings()
        errors = []
        SettingsOps.validate_stored_info(username, password, max_items_to_return, errors)
        if len(errors) == 0:
            source_runnable = SourceRunnable(username, password, username, password, DEFAULT_ORDER_PARAMS)
            source_runnable.source_object.task_complete.connect(self.on_new_source)
            self.init_progress_bar()
            self.search_thread_pool.start(source_runnable)

    def query_sources(self, search_params):
        """
        Queries the sources when the user clicks search; first search to run
        :param search_params: The VectorsSourcesParams for the search (the AOI)
        :return: None
        """
        self.search_thread_pool.waitForDone(0)
        # self.init_vector_layers()
        # clear out old models
        self.dialog_base.data_sources_list_view.setModel(None)
        self.dialog_base.geometry_list_view.setModel(None)
        self.dialog_base.types_list_view.setModel(None)
        self.sources.clear()
        self.geometries.clear()
        self.types_dict.clear()
        self.items.clear()
        self.written_first_line = False
        self.written_first_point = False
        self.written_first_polygon = False

        username, password, max_items_to_return = SettingsOps.get_settings()
        if VectorsProcessForm.validate_stored_settings(self.iface, username, password, username, password, max_items_to_return):
            source_runnable = SourceRunnable(username, password, username, password, search_params)
            source_runnable.source_object.task_complete.connect(self.on_new_source)
            self.init_progress_bar()
            self.search_thread_pool.start(source_runnable)

    def query_geometries(self, geometry_params):
        """
        Queries the geometries using the geometry_params
        :param geometry_params: The VectorsGeometriesParams for the search
        :return: None
        """
        username, password, max_items_to_return = SettingsOps.get_settings()
        geometry_runnable = GeometryRunnable(username, password, username, password, geometry_params)
        geometry_runnable.geometry_object.task_complete.connect(self.on_new_geometries)
        self.init_progress_bar()
        self.search_thread_pool.start(geometry_runnable)

    def query_types(self, types_params):
        """
        Queries the types using the types_params
        :param types_params: The VectorsTypesParams for the search
        :return: None
        """
        username, password, max_items_to_return = SettingsOps.get_settings()
        types_runnable = TypeRunnable(username, password, username, password, types_params)
        types_runnable.type_object.task_complete.connect(self.on_new_types)
        self.init_progress_bar()
        self.search_thread_pool.start(types_runnable)

    def query_items(self, items_params):
        """
        Queries the items using the items_params
        :param items_params: The VectorsItemsParams for the search
        :return: None
        """
        username, password, max_items_to_return = SettingsOps.get_settings()
        items_runnable = ItemRunnable(username, password, username, password, items_params)
        items_runnable.item_object.task_complete.connect(self.on_new_items)
        self.init_progress_bar()
        self.search_thread_pool.start(items_runnable)

    def on_source_checked(self, source_item):
        """
        Callback function for when the user checks/unchecks a source item in the UI
        Updates the counts of its children based on the action
        :param source_item: The individual SourceItem in the UI
        :return: None
        """
        # don't bother for non-checked events
        if not source_item.has_checked_changed():
            return
        # leave checked for as long as search is running
        if self.is_searching():
            source_item.setCheckState(Qt.Checked)
            return
        # keep to the same if exporting
        if self.is_exporting():
            if source_item.is_checked:
                source_item.setCheckState(Qt.Checked)
            else:
                source_item.setCheckState(Qt.Unchecked)
            return
        is_checked = source_item.current_state()
        for key, geometry in source_item.geometries.iteritems():
            if is_checked:
                geometry.enable_source(source_item.title)
            else:
                geometry.disable_source(source_item.title)
        for key, type_entry in source_item.type_entries.iteritems():
            if is_checked:
                type_entry.enable_source(source_item.title, self.geometries)
            else:
                type_entry.disable_source(source_item.title, self.geometries)
        source_item.update_checked()

    def on_geometry_check(self, geometry_item):
        """
        Callback function for when the user checks/unchecks a geometry item in the UI
        Updates the counts of its children based on the action
        :param geometry_item: The individual GeometryItem in the UI
        :return: None
        """
        # don't bother for non-checked events
        if not geometry_item.has_checked_changed():
            return
        # leave checked while search is running
        if self.is_searching():
            geometry_item.setCheckState(Qt.Checked)
            return
        # keep to the same if exporting
        if self.is_exporting():
            if geometry_item.is_checked:
                geometry_item.setCheckState(Qt.Checked)
            else:
                geometry_item.setCheckState(Qt.Unchecked)
            return
        is_checked = geometry_item.current_state()
        for key, type_entry in geometry_item.type_entries.iteritems():
            if is_checked:
                type_entry.enable_geometry(geometry_item.title, self.sources)
            else:
                type_entry.disable_geometry(geometry_item.title, self.sources)
        geometry_item.update_checked()

    def on_type_check(self, type_item):
        """
        Callaback function for when the user checks/unchecks a type item in the UI
        Updates the checkbox if necessary
        :param type_item: The individual TypeItem in the UI
        :return: None
        """
        # don't bother for non-checked events
        if not type_item.has_checked_changed():
            return
        # leave checked while search is running
        if self.is_searching():
            type_item.setCheckState(Qt.Checked)
            return
        # keep to same if exporting
        if self.is_exporting():
            if type_item.is_checked:
                type_item.setCheckState(Qt.Checked)
            else:
                type_item.setCheckState(Qt.Unchecked)
            return
        type_item.update_checked()

    def export(self):
        """
        Runs the items queries based on the checked items and writes the output to geojson files in the
        directory specified
        :return: None
        """
        self.clear_widgets()
        if not self.validate_export():
            return
        starting_directory = self.directory or os.path.expanduser("~")
        directory = QFileDialog.getExistingDirectory(None, "Export to directory", starting_directory)
        if not self.validate_directory(directory):
            return
        self.directory = directory

        bar_max = len(self.sources.keys()) * len(self.types_dict.keys())

        self.init_json_progress_bar(bar_max)

        username, password,  max_items_to_return = SettingsOps.get_settings()

        for source_key in self.sources.keys():
            source_item = self.sources[source_key]
            if source_item.is_checked:
                for item_key in self.types_dict.keys():
                    type_item = self.types_dict[item_key]
                    if type_item.is_checked and type_item.total_count > 0:
                        item_params = VectorsItemsParams(source_item.source_params, source_key, item_key)
                        task = JSONItemRunnable(username, password, username, password, item_params)
                        task.json_item_object.task_complete.connect(self.on_new_json_items)
                        task.json_item_object.task_cancel.connect(self.cancel_json_threads)
                        self.json_thread_pool.start(task)
                    else:
                        if self.json_progress:
                            self.json_progress.setValue(self.json_progress.value() + 1)
            else:
                if self.json_progress:
                    self.json_progress.setValue(self.json_progress.value() + len(self.types_dict.keys()))

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

    def validate_export(self):
        """
        Validates the export information before running the export
        :return: True if there are no problems; False if there are
        """
        errors = []
        # validate settings
        username, password, max_items_to_return = SettingsOps.get_settings()
        SettingsOps.validate_stored_info(username, password, max_items_to_return, errors)
        # must ensure there's something to export
        if not self.dialog_base.types_list_view.model() or not self.dialog_base.data_sources_list_view.model():
            errors.append("Please search for data before attempting to export.")
        # ensure that the current search is complete
        if self.progress_message_bar or self.is_searching():
            errors.append("Please wait until the current search is complete.")
        # ensure there's not a current export
        if self.is_exporting():
            errors.append("Please wait until the current export is complete.")
        # ensure there's less than the max to export
        total_to_export = 0
        for type_entry, type_item in self.types_dict.iteritems():
            if type_item.is_checked:
                total_to_export += type_item.total_count
            if total_to_export > max_items_to_return:
                errors.append("Number to export exceeds max of " + str(max_items_to_return)
                              + ". Please refine your search.")
                break

        if len(errors) > 0:
            self.iface.messageBar().pushMessage("Error", "The following error(s) occurred:<br />" + "<br />".join(errors),
                                                level=QgsMessageBar.CRITICAL)
            return False
        return True

    def validate_directory(self, directory):
        """
        Validate the directory
        :param directory:
        :return:
        """
        errors = []
        # ensure the directory was actually given
        if not directory:
            errors.append("No output directory given.")
        # ensure directory exists
        elif not os.path.exists(directory):
            errors.append("Path: " + directory + " does not exist.")
        # ensure path is directory
        elif not os.path.isdir(directory):
            errors.append("Path: " + directory + " is not a directory.")
        if len(errors) > 0:
            self.iface.messageBar().pushMessage("Error", "The following error(s) occurred:<br />" + "<br />".join(errors),
                                                level=QgsMessageBar.CRITICAL)
            return False
        return True

    def write_to_file(self, filename, text):
        with self.json_lock:
            file_obj = self.file_dict.get(str(filename), None)
            if not file_obj:
                file_path = os.path.join(self.directory, filename)
                file_obj = open(file_path, 'w')
                self.file_dict[str(filename)] = file_obj
                file_obj.write(GEOJSON_BEGINNING)
        file_obj.write(text)

    def close_file(self, filename):
        with self.json_lock:
            file_obj = self.file_dict.get(str(filename), None)
            if file_obj:
                file_obj.write(GEOJSON_ENDING)
                file_obj.close()

class SourceObject(QObject):
    """
    QObject for holding the signal to emit new sources
    """
    task_complete = pyqtSignal(object, object)

    def __init__(self, QObject_parent=None):
        QObject.__init__(self, QObject_parent)

class SourceRunnable(QRunnable):
    """
    Thread pool worker task for running sources queries
    """

    def __init__(self, username, password, client_id, client_secret, source_params):
        """
        Constructor
        :param username: Username for OAuth2 authentication
        :param password: Password for OAuth2 authentication
        :param client_id: Client ID for OAuth2 authentication
        :param client_secret: Client Secret for OAuth2 authentication
        :param source_params: VectorsSourcesParams for the search
        :return: SourceRunnable
        """
        QRunnable.__init__(self)
        self.username = username
        self.password = password
        self.client_id = client_id
        self.client_secret = client_secret
        self.source_params = source_params
        self.source_object = SourceObject()

    def run(self):
        """
        Runs the sources query and emits the results
        :return: None
        """
        query = VectorQuery(self.username, self.password)
        query.log_in()
        new_sources = query.query_sources(source_params=self.source_params)
        self.source_object.task_complete.emit(self.source_params, new_sources)

class GeometryObject(QObject):
    """
    QObject for holding the signal to emit new geometries
    """
    task_complete = pyqtSignal(object, object)

    def __init__(self, QObject_parent=None):
        QObject.__init__(self, QObject_parent)

class GeometryRunnable(QRunnable):
    """
    Thread pool task for running geometry queries
    """

    def __init__(self, username, password, client_id, client_secret, geometry_params):
        """
        Constructor
        :param username: Username for OAuth2 authentication
        :param password: Password for OAuth2 authentication
        :param client_id: Client ID for OAuth2 authentication
        :param client_secret: Client Secret for OAuth2 authentication
        :param geometry_params: VectorsGeometriesParams for the geometry search
        :return: GeometryRunnable
        """
        QRunnable.__init__(self)
        self.username = username
        self.password = password
        self.client_id = client_id
        self.client_secret = client_secret
        self.geometry_params = geometry_params
        self.geometry_object = GeometryObject()

    def run(self):
        """
        Runs the geometry query and emits the results
        :return: None
        """
        query = VectorQuery(self.username, self.password)
        query.log_in()
        new_geometries = query.query_geometries(geometry_params=self.geometry_params)
        self.geometry_object.task_complete.emit(self.geometry_params, new_geometries)

class TypeObject(QObject):
    """
    QObject for holding the signal to emit new types
    """
    task_complete = pyqtSignal(object, object)

    def __init__(self, QObject_parent=None):
        QObject.__init__(self, QObject_parent)

class TypeRunnable(QRunnable):
    """
    Thread pool task for running types queries
    """

    def __init__(self, username, password, client_id, client_secret, type_params):
        """
        Constructor
        :param username: Username for OAuth2 authentication
        :param password: Password for OAuth2 authentication
        :param client_id: Client ID for OAuth2 authentication
        :param client_secret: Client Secret for OAuth2 authentication
        :param type_params: VectorsTypesParams for the types query
        :return: TypeRunnable
        """
        QRunnable.__init__(self)
        self.username = username
        self.password = password
        self.client_id = client_id
        self.client_secret = client_secret
        self.type_params = type_params
        self.type_object = TypeObject()

    def run(self):
        """
        Runs the types query and emits the results
        :return: None
        """
        query = VectorQuery(self.username, self.password)
        query.log_in()
        new_types = query.query_types(self.type_params)
        self.type_object.task_complete.emit(self.type_params, new_types)

class ItemObject(QObject):
    """
    QObject for holding the signal to emit new items for rendering
    """
    task_complete = pyqtSignal(object, object)

    def __init__(self, QObject_parent=None):
        QObject.__init__(self, QObject_parent)

class ItemRunnable(QRunnable):
    """
    Thread pool task for querying items
    """

    def __init__(self, username, password, client_id, client_secret, item_params):
        """
        Constructor
        :param username: Username for OAuth2 authentication
        :param password: Password for OAuth2 authentication
        :param client_id: Client ID for OAuth2 authentication
        :param client_secret: Client Secret for OAuth2 authentication
        :param item_params: VectorsItemsParams for querying items
        :return: ItemRunnable
        """
        QRunnable.__init__(self)
        self.username = username
        self.password = password
        self.client_id = client_id
        self.client_secret = client_secret
        self.item_params = item_params
        self.item_object = ItemObject()

    def run(self):
        """
        Runs the items query and emits the results
        :return: None
        """
        query = VectorQuery(self.username, self.password)
        query.log_in()
        new_items = query.query_items(self.item_params)
        self.item_object.task_complete.emit(self.item_params, new_items)

class SortObject(QObject):
    """
    QObject for holding the sort signal
    """
    task_complete = pyqtSignal()

    def __init__(self, QObject_parent=None):
        QObject.__init__(self, QObject_parent)


class SortRunnable(QRunnable):
    """
    Thread pool task for running the sort
    """
    def __init__(self, model, ):
        """
        Constructor
        :param model: The GUI model holding the view standard items to sort
        :return: SortRunnable
        """
        QRunnable.__init__(self)
        self.model = model
        self.sort_object = SortObject()

    def run(self):
        """
        Runs the sort and emits the signal that the model is done being sorted
        :return:
        """
        self.model.sort(0)
        self.sort_object.task_complete.emit()


class JSONItemObject(QObject):
    """
    QObject for holding the signal for emitting new items in json format
    """
    task_complete = pyqtSignal(object, object)
    task_cancel = pyqtSignal(object)

    def __init__(self, QObject_parent=None):
        QObject.__init__(self, QObject_parent)


class JSONItemRunnable(QRunnable):
    """
    Thread pool task for querying for items
    """
    def __init__(self, username, password, client_id, client_secret, items_params):
        """
        Constructor
        :param username: Username for OAuth2 authentication
        :param password: Password for OAuth2 authentication
        :param client_id: Client ID for OAuth2 authentication
        :param client_secret: Client Secret for OAuth2 authentication
        :param items_params: The VectorsItemsParams for querying for items
        :return: JSONItemRunnable
        """
        QRunnable.__init__(self)
        self.username = username
        self.password = password
        self.client_id = client_id
        self.client_secret = client_secret
        self.items_params = items_params
        self.json_item_object = JSONItemObject()

    def run(self):
        """
        Runs the items query and emit the results
        :return: None
        """
        try:
            query = VectorQuery(self.username, self.password)
            query.log_in()
            new_items = query.query_items(self.items_params, True)
            self.json_item_object.task_complete.emit(self.items_params, new_items)
        except Exception, e:
            self.json_item_object.task_cancel.emit(e)

class SourceItem(QStandardItem):
    """
    Entry in the GUI list of sources
    """
    def __init__(self, title, source_params, count, *__args):
        """
        Constructor
        :param title: Name of the source (OSM, etc.)
        :param source_params: The parameters used for running the search
        :param count: The count for the given source
        :param __args: Additional args
        :return: SourceItem
        """
        QStandardItem.__init__(self, *__args)
        self._title = title
        self._count = count
        self.change_text()
        self._is_checked = True
        self.source_params = source_params
        self.geometries = {}
        self.type_entries = {}

    @property
    def title(self):
        return self._title

    @property
    def count(self):
        return self._count

    @count.setter
    def count(self, new_count):
        self._count = new_count
        self.change_text()

    @property
    def is_checked(self):
        return self._is_checked

    def current_state(self):
        """
        Gets the current state of the checkbox
        :return: True if checked; False otherwise
        """
        return self.checkState() == Qt.Checked

    def update_checked(self):
        """
        Updates the checked internal property
        """
        self._is_checked = self.checkState() == Qt.Checked

    def has_checked_changed(self):
        """
        Checks if the checkbox has changed state (e.g. checked -> unchecked)
        :return: True if it has changed state; False otherwise
        """
        current_state = self.checkState() == Qt.Checked
        return self._is_checked != current_state

    def change_text(self):
        """
        Updates the current text for the item
        """
        self.setText(WIDGET_TEXT_FMT % (self._title, self._count))

    def __hash__(self):
        return hash(self._title)

    def __eq__(self, other):
        return self._title == other.title

    def __ne__(self, other):
        return self._title != other.title

    def __le__(self, other):
        return self._title <= other.title

    def __lt__(self, other):
        return self._title < other.title

    def __ge__(self, other):
        return self._title >= other.title

    def __gt__(self, other):
        return self._title > other.title

    def __cmp__(self, other):
        return cmp(self._title, other.title)

class GeometryItem(QStandardItem):
    """
    Entry in the GUI list of geometries
    """
    def __init__(self, title, *__args):
        """
        Constructor
        :param title: Name of the geometry (Polygon, Point, etc.)
        :param __args: Additional args
        :return: Geometry Item
        """
        QStandardItem.__init__(self, *__args)
        self._title = title
        self._counts = {}
        self._total_count = 0
        self.change_text()
        self._is_checked = True
        self.type_entries = {}

    @property
    def title(self):
        return self._title

    @property
    def total_count(self):
        return self._total_count

    @property
    def is_checked(self):
        return self._is_checked

    def current_state(self):
        """
        Gets the current checkbox state
        :return: True if checked; False otherwise
        """
        return self.checkState() == Qt.Checked

    def update_checked(self):
        """
        Updates the is_checked property with the current state
        """
        self._is_checked = self.checkState() == Qt.Checked

    def has_checked_changed(self):
        """
        Checks to see if the checkbox has changed from checked to unchecked or vice versa
        :return: True if it has; False otherwise
        """
        current_state = self.checkState() == Qt.Checked
        return self._is_checked != current_state

    def update_count(self, source, count):
        """
        Updates the displayed count based on if the parent source(s) have been checked/unchecked
        """
        if source in self._counts:
            self._total_count -= self._counts[source]
        self._counts[source] = count
        self._total_count += count
        self.change_text()

    def enable_source(self, source):
        """
        Updates the count if the parent source has been checked
        :param source: The parent source
        """
        if source in self._counts:
            self._total_count += self._counts[source]
            self.change_text()

    def disable_source(self, source):
        """
        Updates the count if the parent source has been unchecked
        :param source: The parent source
        """
        if source in self._counts:
            self._total_count -= self._counts[source]
            self.change_text()

    def change_text(self):
        """
        Updates the rendered text for the item
        """
        self.setText(WIDGET_TEXT_FMT % (self._title, self._total_count))

    def __hash__(self):
        return hash(self._title)

    def __eq__(self, other):
        return self._title == other.title

    def __ne__(self, other):
        return self._title != other.title

    def __le__(self, other):
        return self._title <= other.title

    def __lt__(self, other):
        return self._title < other.title

    def __ge__(self, other):
        return self._title >= other.title

    def __gt__(self, other):
        return self._title > other.title

    def __cmp__(self, other):
        return cmp(self._title, other.title)


class TypesItem(QStandardItem):
    """
    Types entry in the GUI list of types
    """

    def __init__(self, title, *__args):
        """
        Constructor
        :param title: Name of the type
        :param __args: Additional args
        :return: TypesItem
        """
        QStandardItem.__init__(self, *__args)
        self._title = title
        self._counts = {}
        self._total_count = 0
        self._is_checked = True
        self.change_text()

    @property
    def title(self):
        return self._title

    @property
    def total_count(self):
        return self._total_count

    @property
    def is_checked(self):
        return self._is_checked

    def current_state(self):
        """
        Gets the current checkbox state
        :return: True if checked; False otherwise
        """
        return self.checkState() == Qt.Checked

    def update_checked(self):
        """
        Updates the is_checked property with the current state
        """
        self._is_checked = self.checkState() == Qt.Checked

    def has_checked_changed(self):
        """
        Checks to see if the checkbox has changed from checked to unchecked or vice versa
        :return: True if it has; False otherwise
        """
        current_state = self.checkState() == Qt.Checked
        return self._is_checked != current_state

    def update_count(self, source, geometry, count):
        """
        Updates the count given the parent source and geometry
        :param source: The parent source
        :param geometry: The parent geometry
        :param count: The count to add
        :return:
        """
        if source in self._counts:
            if geometry in self._counts[source]:
                self._total_count -= self._counts[source][geometry]
            self._counts[source][geometry] = count
        else:
            self._counts[source] = {geometry: count}
        self._total_count += count
        self.change_text()

    def enable_source(self, source, geometries):
        """
        Updates the rendered count for the type when the parent source is checked
        :param source: The source key
        :param geometries: The list of geometry items
        :return: None
        """
        if source in self._counts.keys():
            for geometry_key in self._counts[source].keys():
                if geometries[geometry_key].is_checked:
                    self._total_count += self._counts[source][geometry_key]
            self.change_text()

    def disable_source(self, source, geometries):
        """
        Updates the rendered count for the type when the parent source is unchecked
        :param source: The source key
        :param geometries: The list of geometries
        :return: None
        """
        if source in self._counts:
            for geometry_key in self._counts[source].keys():
                if geometries[geometry_key].is_checked:
                    self._total_count -= self._counts[source][geometry_key]
            self.change_text()

    def enable_geometry(self, geometry, sources):
        """
        Updates the rendered count for the type when the parent geometry is checked
        :param geometry: The geometry key
        :param sources: The list of sources
        :return: None
        """
        for source_key in self._counts.keys():
            if geometry in self._counts[source_key] and sources[source_key].is_checked:
                self._total_count += self._counts[source_key][geometry]
        self.change_text()

    def disable_geometry(self, geometry, sources):
        """
        Updates the rendered count for the type when the parent geometry is unchecked
        :param geometry:
        :param sources:
        :return:
        """
        for source_key in self._counts.keys():
            if geometry in self._counts[source_key] and sources[source_key].is_checked:
                self._total_count -= self._counts[source_key][geometry]
        self.change_text()

    def source_keys(self):
        """
        Generator for the source keys
        :return: Source key
        """
        for source_key in self._counts.keys():
            yield source_key

    def change_text(self):
        """
        Updates the text with the new count
        :return: None
        """
        new_text = WIDGET_TEXT_FMT % (self._title, self._total_count)
        if new_text != self.text():
            self.setText(new_text)

    def __hash__(self):
        return hash(self._title)

    def __eq__(self, other):
        return self._title == other.title

    def __ne__(self, other):
        return self._title != other.title

    def __le__(self, other):
        return self._title <= other.title

    def __lt__(self, other):
        return self._title < other.title

    def __ge__(self, other):
        return self._title >= other.title

    def __gt__(self, other):
        return self._title > other.title

    def __cmp__(self, other):
        return cmp(self._title, other.title)

class TypesModel(QSortFilterProxyModel):
    """
    FilterProxyModel to filter out types with count of 0
    """
    def filterAcceptsRow(self, p_int, source_parent):
        """
        Filters out a given row if the count found is 0
        :param p_int: The index
        :param source_parent: The source parent (ignored; it's None)
        :return: True if it should be shown; False if it shouldn't
        """
        index = self.sourceModel().index(p_int, 0)
        types_entry_str = index.data()
        if not types_entry_str:
            return False
        match = REGEX_DIGITS.search(types_entry_str)
        if match:
            digits_str = match.group(1)
            digits = int(digits_str)
            return digits > 0
        return False
