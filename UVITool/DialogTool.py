__author__ = 'mtrotter'

import UVIToolProcessForm
from InsightCloudQuery import InsightCloudParams, InsightCloudQuery

from PyQt4.QtGui import QStandardItem, QStandardItemModel
from PyQt4.QtCore import Qt

DEFAULT_LEFT = "-180.0"
DEFAULT_RIGHT = "180.0"
DEFAULT_TOP = "90.0"
DEFAULT_BOTTOM = "-90.0"

DEFAULT_ORDER_PARAMS = InsightCloudParams(top=DEFAULT_TOP, bottom=DEFAULT_BOTTOM, left=DEFAULT_LEFT, right=DEFAULT_RIGHT)

WIDGET_TEXT_FMT = "%s (%d)"

KEY_WIDGET = "widget"

class DialogTool:
    def __init__(self, iface, bbox_gui, dialog_base):
        self.iface = iface
        self.bbox_gui = bbox_gui
        self.dialog_base = dialog_base
        self.sources = {}
        self.query_initial_sources()

    def query_initial_sources(self):
        username, password = UVIToolProcessForm.get_settings()
        errors = []
        UVIToolProcessForm.validate_stored_info(username, password, errors)
        if len(errors) == 0:
            query = InsightCloudQuery(username, password)
            new_sources = query.query_sources(order_params=DEFAULT_ORDER_PARAMS)
            self.process_new_sources(new_sources)

    def query_sources(self, order_params):
        username, password = UVIToolProcessForm.get_settings()
        if UVIToolProcessForm.validate_stored_settings(self.iface, username, password):
            query = InsightCloudQuery(username, password)
            new_sources = query.query_sources(order_params=order_params)
            self.process_new_sources(new_sources)

    def process_new_sources(self, new_sources):
        if not new_sources:
            return
        examined_sources = set()
        model = QStandardItemModel(self.dialog_base.data_sources_list_view)
        for key, count in new_sources.iteritems():
            if key in self.sources:
                self.sources[key].count = count
            else:
                new_item = DialogItem(key, count)
                new_item.setCheckable(True)
                new_item.setCheckState(Qt.Checked)
                model.appendRow(new_item)
                self.sources[key] = new_item
            examined_sources.add(key)
        unexamined_sources = examined_sources.difference(set(self.sources.keys()))
        for key in unexamined_sources:
            self.sources[key].count = 0
        self.dialog_base.data_sources_list_view.setModel(model)

class DialogItem(QStandardItem):
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


