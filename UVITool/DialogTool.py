__author__ = 'mtrotter'

import UVIToolProcessForm
from InsightCloudQuery import InsightCloudSourcesParams, InsightCloudGeometriesParams, InsightCloudQuery

from PyQt4.QtGui import QStandardItem, QStandardItemModel
from PyQt4.QtCore import Qt

DEFAULT_LEFT = "-180.0"
DEFAULT_RIGHT = "180.0"
DEFAULT_TOP = "90.0"
DEFAULT_BOTTOM = "-90.0"

DEFAULT_ORDER_PARAMS = InsightCloudSourcesParams(top=DEFAULT_TOP, bottom=DEFAULT_BOTTOM, left=DEFAULT_LEFT, right=DEFAULT_RIGHT)

WIDGET_TEXT_FMT = "%s (%d)"

KEY_WIDGET = "widget"

class DialogTool:
    def __init__(self, iface, bbox_gui, dialog_base):
        self.iface = iface
        self.bbox_gui = bbox_gui
        self.dialog_base = dialog_base
        self.sources = {}
        self.geometries = {}
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
            self.dialog_base.data_sources_list_view.setModel(model)

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
        unexamined_geometries = examined_geometries.difference(set(self.geometries.keys()))
        for geometry in unexamined_geometries:
            self.geometries[geometry].update_count(geometry_params.source, 0)
        if new_model:
            self.dialog_base.geometry_list_view.setModel(model)


class SourceItem(QStandardItem):
    def __init__(self, title, count, *__args):
        QStandardItem.__init__(self, *__args)
        self._title = title
        self._count = count
        self.change_text()

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

    @property
    def title(self):
        return self._title

    @property
    def total_count(self):
        return self._total_count

    def update_count(self, source, count):
        if source in self._counts:
            self._total_count -= self._counts[source]
        self._counts[source] = count
        self._total_count += count
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



