import json
from qgis._core import QgsCoordinateReferenceSystem, QgsField
from qgis._gui import QgsMessageBar

__author__ = 'mtrotter'

import UVIToolProcessForm
from InsightCloudQuery import InsightCloudSourcesParams, InsightCloudGeometriesParams, InsightCloudTypesParams,\
    InsightCloudQuery, InsightCloudItemsParams, KEY_JSON_PROPERTIES_LIST

from PyQt4.QtGui import QStandardItem, QStandardItemModel, QProgressBar, QFileDialog
from PyQt4.QtCore import Qt, QThreadPool, QRunnable, QObject, pyqtSlot, pyqtSignal, QVariant
from qgis.core import QgsVectorLayer, QgsMapLayerRegistry

import os

DEFAULT_LEFT = "-180.0"
DEFAULT_RIGHT = "180.0"
DEFAULT_TOP = "90.0"
DEFAULT_BOTTOM = "-90.0"
'''
DEFAULT_LEFT = "-74.257159"
DEFAULT_RIGHT = "-73.699215"
DEFAULT_TOP = "40.915568"
DEFAULT_BOTTOM = "40.495992"
'''

DEFAULT_ORDER_PARAMS = InsightCloudSourcesParams(top=DEFAULT_TOP, bottom=DEFAULT_BOTTOM, left=DEFAULT_LEFT, right=DEFAULT_RIGHT)

WIDGET_TEXT_FMT = "%s (%d)"

KEY_COUNT = "count"
KEY_GEOMETRY = "geometry"
KEY_ENABLED = "enabled"

KEY_POINT = "Point"
KEY_POLYGON = "Polygon"
KEY_LINE = "Line"

FILE_POINTS = u'points.json'
FILE_POLYGON = u'polygon.json'
FILE_LINE = u'line.json'

MAX_EXPORT = 50000000000

GEOJSON_BEGINNING = '{"type": "FeatureCollection", "features": ['
GEOJSON_ENDING = ']}'

class DialogTool(QObject):
    def clear_widgets(self):
        self.progress_message_bar = None
        self.iface.messageBar().clearWidgets()

    def on_sort_complete(self):
        if self.thread_pool.activeThreadCount() == 0:
            self.clear_widgets()

    def on_task_complete(self):
        if self.thread_pool.activeThreadCount() == 0:
            source_model = self.dialog_base.data_sources_list_view.model()
            if source_model:
                source_thread = SortRunnable(source_model)
                source_thread.sort_object.task_complete.connect(self.on_sort_complete)
                self.thread_pool.start(source_thread)
            geometry_model = self.dialog_base.geometry_list_view.model()
            if geometry_model:
                geometry_thread = SortRunnable(geometry_model)
                geometry_thread.sort_object.task_complete.connect(self.on_sort_complete)
                self.thread_pool.start(geometry_thread)
            types_model = self.dialog_base.types_list_view.model()
            if types_model:
                type_thread = SortRunnable(types_model)
                type_thread.sort_object.task_complete.connect(self.on_sort_complete)
                self.thread_pool.start(type_thread)

    @pyqtSlot(object, object)
    def on_new_source(self, source_params, new_sources):
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
                geometry_params = InsightCloudGeometriesParams(source_params, key)
                self.query_geometries(geometry_params)
            if new_model:
                model.itemChanged.connect(self.on_source_checked)
                self.dialog_base.data_sources_list_view.setModel(model)
        self.on_task_complete()

    @pyqtSlot(object, object)
    def on_new_geometries(self, geometry_params, new_geometries):
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
                types_params = InsightCloudTypesParams(geometry_params, key)
                self.query_types(types_params)
            if new_model:
                model.itemChanged.connect(self.on_geometry_check)
                self.dialog_base.geometry_list_view.setModel(model)
        self.on_task_complete()

    @pyqtSlot(object, object)
    def on_new_types(self, types_params, new_types):
        if new_types:
            new_model = False
            model = self.dialog_base.types_list_view.model()
            if not model:
                model = QStandardItemModel(self.dialog_base.types_list_view)
                new_model = True
            for key, count in new_types.iteritems():
                if key in self.types_dict:
                    self.types_dict[key].update_count(types_params.source, types_params.geometry, count)
                else:
                    type_item = TypesItem(key)
                    type_item.update_count(types_params.source, types_params.geometry, count)
                    type_item.setCheckable(True)
                    type_item.setCheckState(Qt.Checked)
                    model.appendRow(type_item)
                    self.types_dict[key] = type_item
                if key not in self.sources[types_params.source].type_entries:
                    self.sources[types_params.source].type_entries[key] = self.types_dict[key]
                if key not in self.geometries[types_params.geometry].type_entries:
                    self.geometries[types_params.geometry].type_entries[key] = self.types_dict[key]
                # source = types_params.source
                # self.start_new_item(source, key, types_params)
            if new_model:
                self.dialog_base.types_list_view.setModel(model)
        self.on_task_complete()

    def start_new_item(self, source, type_key, type_params):
        should_add = False
        if source not in self.items.keys():
            should_add = True
            self.items[source] = {}
        if type_key not in self.items[source].keys():
            should_add = True
            self.items[source][type_key] = []
        if should_add:
            username, password = UVIToolProcessForm.get_settings()
            item_params = InsightCloudItemsParams(type_params.sources_params,
                                                  source, type_key)
            item_runnable = ItemRunnable(username, password, item_params)
            item_runnable.item_object.task_complete.connect(self.on_new_items)
            self.thread_pool.start(item_runnable)

    @pyqtSlot(object, object)
    def on_new_items(self, items_params, new_items):
        if new_items:
            self.point_vector_layer.startEditing()
            self.line_vector_layer.startEditing()
            self.polygon_vector_layer.startEditing()

            point_data_provider = self.point_vector_layer.dataProvider()
            line_data_provider = self.line_vector_layer.dataProvider()
            polygon_data_provider = self.polygon_vector_layer.dataProvider()

            point_data_provider.addFeatures(new_items[KEY_POINT])
            line_data_provider.addFeatures(new_items[KEY_LINE])
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
    def on_new_json_items(self, items_params, new_items):
        if self.json_progress_message_bar:
            self.json_progress.setValue(self.json_progress.value() + 1)
        if new_items:
            for polygon in new_items[KEY_POLYGON]:
                if not self.written_first_polygon:
                    self.polygon_file.write(u",")
                    self.written_first_polygon = True
                self.polygon_file.write(polygon)
            for line in new_items[KEY_LINE]:
                if not self.written_first_line:
                    self.line_file.write(u",")
                    self.written_first_line = True
                self.line_file.write(line)

            for point in new_items[KEY_POINT]:
                if not self.written_first_point:
                    self.point_file.write(u",")
                    self.written_first_point = True
                self.point_file.write(point)

        self.on_new_json_task_complete()

    def on_new_json_task_complete(self):
        if self.json_thread_pool.activeThreadCount() > 0:
            self.json_progress.setValue(self.json_progress.value() + 1)
        else:
            # close files
            self.polygon_file.write(GEOJSON_ENDING)
            self.polygon_file.close()

            self.line_file.write(GEOJSON_ENDING)
            self.line_file.close()

            self.point_file.write(GEOJSON_ENDING)
            self.point_file.close()

            # update tool
            self.line_file = None
            self.point_file = None
            self.polygon_file = None
            self.written_first_line = False
            self.written_first_point = False
            self.written_first_polygon = False

            # remove progress bar
            self.json_progress_message_bar = None
            self.json_progress = None
            self.iface.messageBar().clearWidgets()

            # update info
            self.iface.messageBar().pushMessage("INFO", "File export has completed to directory %s." % self.directory)

            self.directory = None

    def __init__(self, iface, bbox_gui, dialog_base):
        QObject.__init__(self, None)
        self.iface = iface
        self.bbox_gui = bbox_gui
        self.dialog_base = dialog_base
        self.sources = {}
        self.geometries = {}
        self.types_dict = {}
        self.items = {}
        self.thread_pool = QThreadPool()
        self.json_thread_pool = QThreadPool()
        self.progress_message_bar = None
        self.json_progress_message_bar = None
        self.json_progress = None
        self.point_vector_layer = None
        self.line_vector_layer = None
        self.polygon_vector_layer = None
        self.dialog_base.export_button.clicked.connect(self.export)
        # self.query_initial_sources()
        self.point_file = None
        self.line_file = None
        self.polygon_file = None
        self.directory = None
        self.written_first_line = False
        self.written_first_point = False
        self.written_first_polygon = False

    def init_progress_bar(self):
        if not self.progress_message_bar:
            self.progress_message_bar = self.iface.messageBar().createMessage("Querying for data")
            progress = QProgressBar()
            progress.setMinimum(0)
            progress.setMaximum(0)
            progress.setAlignment(Qt.AlignLeft | Qt.AlignCenter)
            self.progress_message_bar.layout().addWidget(progress)
            self.iface.messageBar().pushWidget(self.progress_message_bar, self.iface.messageBar().INFO)

    def init_json_progress_bar(self, bar_max):
        self.json_progress_message_bar = self.iface.messageBar().createMessage("Exporting json to " + self.directory)
        self.json_progress = QProgressBar()
        self.json_progress.setMinimum(0)
        self.json_progress.setMaximum(bar_max)
        self.json_progress.setAlignment(Qt.AlignLeft | Qt.AlignCenter)
        self.json_progress_message_bar.layout().addWidget(self.json_progress)
        self.iface.messageBar().pushWidget(self.json_progress_message_bar, self.iface.messageBar().INFO)

    def init_vector_layers(self):
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

    def query_initial_sources(self):
        self.thread_pool.waitForDone(0)
        # self.init_vector_layers()
        username, password = UVIToolProcessForm.get_settings()
        errors = []
        UVIToolProcessForm.validate_stored_info(username, password, errors)
        if len(errors) == 0:
            source_runnable = SourceRunnable(username, password, DEFAULT_ORDER_PARAMS)
            source_runnable.source_object.task_complete.connect(self.on_new_source)
            self.init_progress_bar()
            self.thread_pool.start(source_runnable)

    def query_sources(self, order_params):
        self.thread_pool.waitForDone(0)
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

        username, password = UVIToolProcessForm.get_settings()
        if UVIToolProcessForm.validate_stored_settings(self.iface, username, password):
            source_runnable = SourceRunnable(username, password, order_params)
            source_runnable.source_object.task_complete.connect(self.on_new_source)
            self.init_progress_bar()
            self.thread_pool.start(source_runnable)

    def query_geometries(self, geometry_params):
        username, password = UVIToolProcessForm.get_settings()
        geometry_runnable = GeometryRunnable(username, password, geometry_params)
        geometry_runnable.geometry_object.task_complete.connect(self.on_new_geometries)
        self.init_progress_bar()
        self.thread_pool.start(geometry_runnable)

    def query_types(self, types_params):
        username, password = UVIToolProcessForm.get_settings()
        types_runnable = TypeRunnable(username, password, types_params)
        types_runnable.type_object.task_complete.connect(self.on_new_types)
        self.init_progress_bar()
        self.thread_pool.start(types_runnable)

    def query_items(self, items_params):
        username, password = UVIToolProcessForm.get_settings()
        items_runnable = ItemRunnable(username, password, items_params)
        items_runnable.item_object.task_complete.connect(self.on_new_items)
        self.init_progress_bar()
        self.thread_pool.start(items_runnable)

    def on_source_checked(self, source_item):
        if not source_item.has_checked_changed():
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
        if not geometry_item.has_checked_changed():
            return
        is_checked = geometry_item.current_state()
        for key, type_entry in geometry_item.type_entries.iteritems():
            if is_checked:
                type_entry.enable_geometry(geometry_item.title, self.sources)
            else:
                type_entry.disable_geometry(geometry_item.title, self.sources)
        geometry_item.update_checked()

    def export(self):
        self.clear_widgets()
        if not self.validate_export():
            return
        file_dialog = QFileDialog(None)
        directory = file_dialog.getExistingDirectory(None, "Export to directory", os.path.expanduser("~"))
        if not self.validate_directory(directory):
            return
        self.directory = directory
        # set up file names
        point_file = os.path.join(self.directory, FILE_POINTS)
        polygon_file = os.path.join(self.directory, FILE_POLYGON)
        line_file = os.path.join(self.directory, FILE_LINE)

        bar_max = len(self.sources.keys()) * len(self.types_dict.keys())

        self.init_json_progress_bar(bar_max)

        username, password = UVIToolProcessForm.get_settings()

        # create file handlers
        self.polygon_file = open(polygon_file, 'w')
        self.polygon_file.write(GEOJSON_BEGINNING)

        self.line_file = open(line_file, 'w')
        self.line_file.write(GEOJSON_BEGINNING)

        self.point_file = open(point_file, 'w')
        self.point_file.write(GEOJSON_BEGINNING)

        for source_key in self.sources.keys():
            source_item = self.sources[source_key]
            if source_item.is_checked:
                for item_key in self.types_dict.keys():
                    type_item = self.types_dict[item_key]
                    if type_item.is_checked() and type_item.total_count > 0:
                        item_params = InsightCloudItemsParams(source_item.source_params, source_key, item_key)
                        task = JSONItemRunnable(username, password, item_params)
                        task.json_item_object.task_complete.connect(self.on_new_json_items)
                        self.json_thread_pool.start(task)
                    else:
                        if self.json_progress:
                            self.json_progress.setValue(self.json_progress.value() + 1)
            else:
                if self.json_progress:
                    self.json_progress.setValue(self.json_progress.value() + len(self.types_dict.keys()))

    def is_exporting(self):
        return self.json_thread_pool.activeThreadCount() > 0

    def is_searching(self):
        return self.thread_pool.activeThreadCount() > 0

    def validate_export(self):
        errors = []
        # validate settings
        username, password = UVIToolProcessForm.get_settings()
        UVIToolProcessForm.validate_stored_info(username, password, errors)
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
            if type_item.is_checked():
                total_to_export += type_item.total_count
            if total_to_export > MAX_EXPORT:
                errors.append("Number to export exceeds max of " + str(MAX_EXPORT) + ". Please refine your search.")
                break

        if len(errors) > 0:
            self.iface.messageBar().pushMessage("Error", "The following error(s) occurred:\n" + "\n".join(errors),
                                                level=QgsMessageBar.CRITICAL)
            return False
        return True

    def validate_directory(self, directory):
        errors = []
        # ensure directory exists
        if not os.path.exists(directory):
            errors.append("Path: " + directory + " does not exist.")
        # ensure path is directory
        if not os.path.isdir(directory):
            errors.append("Path: " + directory + " is not a directory.")
        if len(errors) > 0:
            self.iface.messageBar().pushMessage("Error", "The following error(s) occurred:\n" + "\n".join(errors),
                                                level=QgsMessageBar.CRITICAL)
            return False
        return True

class SourceObject(QObject):
    task_complete = pyqtSignal(object, object)

    def __init__(self, QObject_parent=None):
        QObject.__init__(self, QObject_parent)

class SourceRunnable(QRunnable):

    def __init__(self, username, password, source_params):
        QRunnable.__init__(self)
        self.username = username
        self.password = password
        self.source_params = source_params
        self.source_object = SourceObject()

    def run(self):
        query = InsightCloudQuery(self.username, self.password)
        new_sources = query.query_sources(source_params=self.source_params)
        self.source_object.task_complete.emit(self.source_params, new_sources)

class GeometryObject(QObject):
    task_complete = pyqtSignal(object, object)

    def __init__(self, QObject_parent=None):
        QObject.__init__(self, QObject_parent)

class GeometryRunnable(QRunnable):
    def __init__(self, username, password, geometry_params):
        QRunnable.__init__(self)
        self.username = username
        self.password = password
        self.geometry_params = geometry_params
        self.geometry_object = GeometryObject()

    def run(self):
        query = InsightCloudQuery(self.username, self.password)
        new_geometries = query.query_geometries(geometry_params=self.geometry_params)
        self.geometry_object.task_complete.emit(self.geometry_params, new_geometries)

class TypeObject(QObject):
    task_complete = pyqtSignal(object, object)

    def __init__(self, QObject_parent=None):
        QObject.__init__(self, QObject_parent)

class TypeRunnable(QRunnable):
    def __init__(self, username, password, type_params):
        QRunnable.__init__(self)
        self.username = username
        self.password = password
        self.type_params = type_params
        self.type_object = TypeObject()

    def run(self):
        query = InsightCloudQuery(self.username, self.password)
        new_types = query.query_types(self.type_params)
        self.type_object.task_complete.emit(self.type_params, new_types)

class ItemObject(QObject):
    task_complete = pyqtSignal(object, object)

    def __init__(self, QObject_parent=None):
        QObject.__init__(self, QObject_parent)

class ItemRunnable(QRunnable):
    def __init__(self, username, password, item_params):
        QRunnable.__init__(self)
        self.username = username
        self.password = password
        self.item_params = item_params
        self.item_object = ItemObject()

    def run(self):
        query = InsightCloudQuery(self.username, self.password)
        new_items = query.query_items(self.item_params)
        self.item_object.task_complete.emit(self.item_params, new_items)

class SortObject(QObject):
    task_complete = pyqtSignal()

    def __init__(self, QObject_parent=None):
        QObject.__init__(self, QObject_parent)


class SortRunnable(QRunnable):
    def __init__(self, model, ):
        QRunnable.__init__(self)
        self.model = model
        self.sort_object = SortObject()

    def run(self):
        self.model.sort(0)
        self.sort_object.task_complete.emit()


class JSONItemObject(QObject):
    task_complete = pyqtSignal(object, object)

    def __init__(self, QObject_parent=None):
        QObject.__init__(self, QObject_parent)


class JSONItemRunnable(QRunnable):
    def __init__(self, username, password, items_params):
        QRunnable.__init__(self)
        self.username = username
        self.password = password
        self.items_params = items_params
        self.json_item_object = JSONItemObject()

    def run(self):
        query = InsightCloudQuery(self.username, self.password)
        new_items = query.query_items(self.items_params, True)
        self.json_item_object.task_complete.emit(self.items_params, new_items)

class SourceItem(QStandardItem):
    def __init__(self, title, source_params, count, *__args):
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
        return self.checkState() == Qt.Checked

    def update_checked(self):
        self._is_checked = self.checkState() == Qt.Checked

    def has_checked_changed(self):
        current_state = self.checkState() == Qt.Checked
        return self._is_checked != current_state

    def change_text(self):
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
    def __init__(self, title, *__args):
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
        return self.checkState() == Qt.Checked

    def update_checked(self):
        self._is_checked = self.checkState() == Qt.Checked

    def has_checked_changed(self):
        current_state = self.checkState() == Qt.Checked
        return self._is_checked != current_state

    def update_count(self, source, count):
        if source in self._counts:
            self._total_count -= self._counts[source]
        self._counts[source] = count
        self._total_count += count
        self.change_text()

    def enable_source(self, source):
        if source in self._counts:
            self._total_count += self._counts[source]
            self.change_text()

    def disable_source(self, source):
        if source in self._counts:
            self._total_count -= self._counts[source]
            self.change_text()

    def change_text(self):
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
    def __init__(self, title, *__args):
        QStandardItem.__init__(self, *__args)
        self._title = title
        self._counts = {}
        self._total_count = 0
        self.change_text()

    @property
    def title(self):
        return self._title

    @property
    def total_count(self):
        return self._total_count

    def is_checked(self):
        return self.checkState() == Qt.Checked

    def update_count(self, source, geometry, count):
        if source in self._counts:
            if geometry in self._counts[source]:
                self._total_count -= self._counts[source][geometry]
            self._counts[source][geometry] = count
        else:
            self._counts[source] = {geometry: count}
        self._total_count += count
        self.change_text()

    def enable_source(self, source, geometries):
        if source in self._counts.keys():
            for geometry_key in self._counts[source].keys():
                if geometries[geometry_key].is_checked:
                    self._total_count += self._counts[source][geometry_key]
            self.change_text()

    def disable_source(self, source, geometries):
        if source in self._counts:
            for geometry_key in self._counts[source].keys():
                if geometries[geometry_key].is_checked:
                    self._total_count -= self._counts[source][geometry_key]
            self.change_text()

    def enable_geometry(self, geometry, sources):
        for source_key in self._counts.keys():
            if geometry in self._counts[source_key] and sources[source_key].is_checked:
                self._total_count += self._counts[source_key][geometry]
        self.change_text()

    def disable_geometry(self, geometry, sources):
        for source_key in self._counts.keys():
            if geometry in self._counts[source_key] and sources[source_key].is_checked:
                self._total_count -= self._counts[source_key][geometry]
        self.change_text()

    def source_keys(self):
        for source_key in self._counts.keys():
            yield source_key

    def change_text(self):
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

