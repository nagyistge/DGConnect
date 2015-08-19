__author__ = 'mtrotter'

import UVIToolProcessForm
from InsightCloudQuery import InsightCloudSourcesParams, InsightCloudGeometriesParams, InsightCloudTypesParams,\
    InsightCloudQuery

from PyQt4.QtGui import QStandardItem, QStandardItemModel
from PyQt4.QtCore import Qt


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

class DialogTool:
    def __init__(self, iface, bbox_gui, dialog_base):
        self.iface = iface
        self.bbox_gui = bbox_gui
        self.dialog_base = dialog_base
        self.sources = {}
        self.geometries = {}
        self.types = {}
        self.query_initial_sources()

    def query_initial_sources(self):
        username, password = UVIToolProcessForm.get_settings()
        errors = []
        UVIToolProcessForm.validate_stored_info(username, password, errors)
        if len(errors) == 0:
            query = InsightCloudQuery(username, password)
            new_sources = query.query_sources(source_params=DEFAULT_ORDER_PARAMS)
            self.process_new_sources(DEFAULT_ORDER_PARAMS, new_sources)

    def query_sources(self, order_params):
        username, password = UVIToolProcessForm.get_settings()
        if UVIToolProcessForm.validate_stored_settings(self.iface, username, password):
            query = InsightCloudQuery(username, password)
            new_sources = query.query_sources(source_params=order_params)
            self.process_new_sources(order_params, new_sources)

    def process_new_sources(self, source_params, new_sources):
        if not new_sources:
            return
        examined_sources = set()
        new_model = False
        model = self.dialog_base.data_sources_list_view.model()
        if not model:
            model = QStandardItemModel(self.dialog_base.data_sources_list_view)
            new_model = True
        for key, count in new_sources.iteritems():
            if key in self.sources:
                self.sources[key].count = count
            else:
                new_item = SourceItem(key, count)
                new_item.setCheckable(True)
                new_item.setCheckState(Qt.Checked)
                model.appendRow(new_item)
                self.sources[key] = new_item
            examined_sources.add(key)
            geometry_params = InsightCloudGeometriesParams(source_params, key)
            self.query_geometries(geometry_params)

        unexamined_sources = examined_sources.difference(set(self.sources.keys()))
        for key in unexamined_sources:
            self.sources[key].count = 0
            for geometry in self.geometries.keys():
                self.geometries[geometry].update_count(key, 0)
        if new_model:
            model.itemChanged.connect(self.on_source_checked)
            self.dialog_base.data_sources_list_view.setModel(model)
        self.dialog_base.data_sources_list_view.model().sort(0)
        self.dialog_base.geometry_list_view.model().sort(0)
        self.dialog_base.types_list_view.model().sort(0)

    def query_geometries(self, geometry_params):
        username, password = UVIToolProcessForm.get_settings()
        query = InsightCloudQuery(username, password)
        new_geometries = query.query_geometries(geometry_params)
        self.process_new_geometries(geometry_params, new_geometries)

    def process_new_geometries(self, geometry_params, new_geometries):
        if not new_geometries:
            return
        examined_geometries = set()
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
            examined_geometries.add(key)
            types_params = InsightCloudTypesParams(geometry_params, key)
            self.query_types(types_params)
        unexamined_geometries = examined_geometries.difference(set(self.geometries.keys()))
        for geometry in unexamined_geometries:
            self.geometries[geometry].update_count(geometry_params.source, 0)
        if new_model:
            model.itemChanged.connect(self.on_geometry_check)
            self.dialog_base.geometry_list_view.setModel(model)

    def query_types(self, types_params):
        username, password = UVIToolProcessForm.get_settings()
        query = InsightCloudQuery(username, password)
        new_types = query.query_types(types_params)
        self.process_new_types(types_params, new_types)

    def process_new_types(self, types_params, new_types):
        if not new_types:
            return
        examined_types = set()
        new_model = False
        model = self.dialog_base.types_list_view.model()
        if not model:
            model = QStandardItemModel(self.dialog_base.types_list_view)
            new_model = True
        for key, count in new_types.iteritems():
            if key in self.types:
                self.types[key].update_count(types_params.source, types_params.geometry, count)
            else:
                type_item = TypesItem(key)
                type_item.update_count(types_params.source, types_params.geometry, count)
                type_item.setCheckable(True)
                type_item.setCheckState(Qt.Checked)
                model.appendRow(type_item)
                self.types[key] = type_item
            examined_types.add(key)
        unexamined_types = examined_types.difference(set(new_types.keys()))
        for type_key in unexamined_types:
            self.types[type_key].update_count(types_params.source, types_params.geometry, 0)
        if new_model:
            self.dialog_base.types_list_view.setModel(model)

    def on_source_checked(self, source_item):
        if not source_item.has_checked_changed():
            return
        is_checked = source_item.current_state()
        for key in self.geometries.keys():
            if is_checked:
                self.geometries[key].enable_source(source_item.title)
            else:
                self.geometries[key].disable_source(source_item.title)
        for type_key in self.types.keys():
            if is_checked:
                self.types[type_key].enable_source(source_item.title, self.geometries)
            else:
                self.types[type_key].disable_source(source_item.title, self.geometries)
        source_item.update_checked()

    def on_geometry_check(self, geometry_item):
        if not geometry_item.has_checked_changed():
            return
        is_checked = geometry_item.current_state()
        for type_key in self.types.keys():
            if is_checked:
                self.types[type_key].enable_geometry(geometry_item.title, self.sources)
            else:
                self.types[type_key].disable_geometry(geometry_item.title, self.sources)
        geometry_item.update_checked()

class SourceItem(QStandardItem):
    def __init__(self, title, count, *__args):
        QStandardItem.__init__(self, *__args)
        self._title = title
        self._count = count
        self.change_text()
        self._is_checked = True

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
                if geometries[source][geometry_key].is_checked:
                    self._total_count += self._counts[source][geometry_key]
            self.change_text()

    def disable_source(self, source, geometries):
        if source in self._counts:
            for geometry_key in self._counts[source].keys():
                if geometries[source][geometry_key].is_checked:
                    self._total_count += self._counts[source][geometry_key]
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

