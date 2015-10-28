# -*- coding: utf-8 -*-
import os
from qgis.core import QgsMessageLog
import re
from uuid import uuid4

from CatalogAcquisition import CatalogAcquisition
from PyQt4.QtCore import Qt, QObject, pyqtSlot, pyqtSignal, QVariant, QAbstractTableModel, SIGNAL, QDate
from PyQt4.QtGui import QComboBox, QLabel, QLineEdit, QPushButton, QGridLayout, QCheckBox, QLayout, QDateEdit


FILTER_ID_KEY = "filter_id"
SATELLITE_VALUE_KEY = "satellite_value"
DATETIME_FORMAT = "yyyy-MM-ddT00:00:00.000Z"

GRID_COLUMN_WHERE = 0
GRID_COLUMN_LABEL = 1
GRID_COLUMN_VALUE = 2
GRID_COLUMN_ADD = 3

TEXT_COLUMN_WHERE = "Where..."
TEXT_COLUMN_AND = "And..."
TEXT_LABEL_BETWEEN = " between "
TEXT_LABEL_IS = " is "
TEXT_STATUS_AVAILABLE = "Available"
TEXT_STATUS_ORDERED = "Ordered"
TEXT_STATUS_UNORDERED = "Unordered"
TEXT_SATELLITE_WV1 = "WorldView-1"
TEXT_SATELLITE_WV2 = "WorldView-2"
TEXT_SATELLITE_WV3 = "WorldView-3"
TEXT_SATELLITE_GEO = "GeoEye-1"
TEXT_SATELLITE_QB2 = "QuickBird"
TEXT_BAND_PAN = "Pan"
TEXT_BAND_MS1 = "Pan_MS1"
TEXT_BAND_MS2 = "Pan_MS1_MS2"
TEXT_REMOVE_BUTTON = " - "

VALUE_SATELLITE_WV1 = "WORLDVIEW01"
VALUE_SATELLITE_WV2 = "WORLDVIEW02"
VALUE_SATELLITE_WV3 = "WORLDVIEW03"
VALUE_SATELLITE_GEO = "GEOEYE01"
VALUE_SATELLITE_QB2 = "QUICKBIRD02"


class CatalogFilters(object):

    def __init__(self, dialog_ui):
        self.dialog_ui = dialog_ui
        self.model = CatalogFilterModel()
        self.layout = dialog_ui.filters_layout

    def add_filter(self):
        filter_id = self.model.add()
        row_index = self.model.get_row_index(filter_id)

        column_combo = QComboBox()
        if row_index == 0:
            column_combo.addItem(TEXT_COLUMN_WHERE)
        else:
            column_combo.addItem(TEXT_COLUMN_AND)
        for column in CatalogAcquisition.COLUMNS:
            column_combo.addItem(column)
        column_combo.currentIndexChanged.connect(self.filter_where_changed)
        self.model.set_column_combo(filter_id, column_combo)

        self.layout.addWidget(column_combo, row_index, GRID_COLUMN_WHERE)

    def remove_filter(self):
        filter_id = self.get_sender_filter_id()
        filter = self.model.get_filter(filter_id)
        self.model.remove(filter_id)

    def filter_where_changed(self, index):
        column_index = index - 1
        filter_id = self.get_sender_filter_id()
        filter = self.model.get_filter(filter_id)

        if column_index >= 0:
            row_index = self.model.get_row_index(filter_id)
            column = CatalogAcquisition.get_column(column_index)

            # set label
            label_text = None
            if column in [CatalogAcquisition.DATE]:
                label_text = TEXT_LABEL_BETWEEN
            else:
                label_text = TEXT_LABEL_IS
            label = QLabel(label_text)
            self.model.set_label(filter_id, label)
            self.layout.addWidget(label, row_index, GRID_COLUMN_LABEL)

            # determine value item
            value_item = None
            if column in [CatalogAcquisition.CATALOG_ID, CatalogAcquisition.VENDOR]:
                value_item = QLineEdit()
            elif column == CatalogAcquisition.STATUS:
                value_item = QGridLayout()
                value_item.addWidget(QCheckBox(TEXT_STATUS_AVAILABLE), 0, 0)
                value_item.addWidget(QCheckBox(TEXT_STATUS_ORDERED), 0, 1)
                value_item.addWidget(QCheckBox(TEXT_STATUS_UNORDERED), 0, 2)
            elif column == CatalogAcquisition.DATE:
                value_item = QGridLayout()
                value_item.addWidget(QDateEdit(QDate.currentDate()), 0, 0)
                value_item.addWidget(QDateEdit(QDate.currentDate()), 0, 1)
            elif column == CatalogAcquisition.SATELLITE:
                value_item = QGridLayout()
                value_item.addWidget(self.create_satellite_checkbox(TEXT_SATELLITE_WV1, VALUE_SATELLITE_WV1), 0, 0)
                value_item.addWidget(self.create_satellite_checkbox(TEXT_SATELLITE_WV2, VALUE_SATELLITE_WV2), 0, 1)
                value_item.addWidget(self.create_satellite_checkbox(TEXT_SATELLITE_WV3, VALUE_SATELLITE_WV3), 0, 2)
                value_item.addWidget(self.create_satellite_checkbox(TEXT_SATELLITE_GEO, VALUE_SATELLITE_GEO), 0, 3)
                value_item.addWidget(self.create_satellite_checkbox(TEXT_SATELLITE_QB2, VALUE_SATELLITE_QB2), 0, 4)
            elif column == CatalogAcquisition.IMAGE_BAND:
                value_item = QComboBox()
                value_item.addItem(TEXT_BAND_PAN)
                value_item.addItem(TEXT_BAND_MS1)
                value_item.addItem(TEXT_BAND_MS2)

            # set value item
            if value_item:
                if issubclass(type(value_item), QLayout):
                    self.layout.addLayout(value_item, row_index, GRID_COLUMN_VALUE)
                else:
                    self.layout.addWidget(value_item, row_index, GRID_COLUMN_VALUE)
                self.model.set_value_item(filter_id, value_item)

            # set remove button
            if not filter.remove_button:
                remove_button = QPushButton(TEXT_REMOVE_BUTTON)
                remove_button.clicked.connect(self.remove_filter)
                self.model.set_remove_button(filter_id, remove_button)
                self.layout.addWidget(remove_button, row_index, GRID_COLUMN_ADD)

            # add option to set another filter
            if self.model.is_last_column_set():
                self.add_filter()

        else:
            self.model.reset(filter_id)

    def get_sender_filter_id(self):
        return self.dialog_ui.dockWidgetContents.sender().property(FILTER_ID_KEY)

    def get_request_filters(self):
        return self.model.get_request_filters()

    def get_datetime_begin(self):
        return self.model.get_datetime_begin()

    def get_datetime_end(self):
        return self.model.get_datetime_end()

    def create_satellite_checkbox(self, display_text, value_text):
        checkbox = QCheckBox(display_text)
        checkbox.setProperty(SATELLITE_VALUE_KEY, value_text)
        return checkbox


class CatalogFilterModel(object):

    def __init__(self):
        self.filters = []

    def get_filter(self, filter_id):
        for filter in self.filters:
            if filter and filter.id == filter_id:
                return filter
        return None

    def get_row_index(self, filter_id):
        for i in range(0, len(self.filters)):
            if self.filters[i] and self.filters[i].id == filter_id:
                return i
        return None

    def get_request_filters(self):
        request_filters = []
        for filter in self.filters:
            if filter:
                request_filters.extend(filter.get_request_filters())
        return request_filters

    def get_datetime_begin(self):
        for filter in self.filters:
            if filter:
                datetime_begin = filter.get_datetime_begin()
                if datetime_begin:
                    return datetime_begin
        return None       

    def get_datetime_end(self):
        for filter in self.filters:
            if filter:
                datetime_end = filter.get_datetime_end()
                if datetime_end:
                    return datetime_end
        return None       

    def add(self):
        filter = CatalogFilter()
        self.filters.append(filter)
        return filter.id

    def set_column_combo(self, filter_id, column_combo):
        filter = self.get_filter(filter_id)
        if column_combo:
            column_combo.setProperty(FILTER_ID_KEY, filter_id)
        if filter.column_combo:
            filter.column_combo.setParent(None)
        filter.column_combo = column_combo

    def set_label(self, filter_id, label):
        filter = self.get_filter(filter_id)
        if label:
            label.setProperty(FILTER_ID_KEY, filter_id)
        if filter.label:
            filter.label.setParent(None)
        filter.label = label

    def set_value_item(self, filter_id, value_item):
        filter = self.get_filter(filter_id)
        if value_item:
            value_item.setProperty(FILTER_ID_KEY, filter_id)
        if filter.value_item:
            # TODO recursive
            if issubclass(type(filter.value_item), QLayout):
                for i in reversed(range(filter.value_item.count())):
                    filter.value_item.itemAt(i).widget().setParent(None)
                filter.value_item.layout().setParent(None)
            else:
                filter.value_item.setParent(None)
        filter.value_item = value_item

    def set_remove_button(self, filter_id, remove_button):
        filter = self.get_filter(filter_id)
        if remove_button:
            remove_button.setProperty(FILTER_ID_KEY, filter_id)
        if filter.remove_button:
            filter.remove_button.setParent(None)
        filter.remove_button = remove_button

    def reset(self, filter_id):
        self.set_column_combo(filter_id, None)
        self.set_label(filter_id, None)
        self.set_value_item(filter_id, None)
        self.set_remove_button(filter_id, None)

    def remove(self, filter_id):
        self.reset(filter_id)
        row_index = self.get_row_index(filter_id)
        self.filters[row_index] = None

    def is_last_column_set(self):
        for i in reversed(range(len(self.filters))): 
            if self.filters[i]:
                return self.filters[i].get_column_index() >= 0
        else:
            return True


class CatalogFilter(object): # TODO properties?

    def __init__(self):
        self.id = str(uuid4())
        self.column_combo = None
        self.label = None
        self.value_item = None
        self.remove_button = None

    def get_request_filters(self):
        request_filters = []
        column_index = self.get_column_index()
        if column_index >= 0:
            column = CatalogAcquisition.get_column(column_index)

            if column == CatalogAcquisition.CATALOG_ID:
                catalog_id = self.escape_value_text(self.value_item.text())
                request_filters.append("catalogID = '%s'" % catalog_id)

            elif column == CatalogAcquisition.STATUS:
                available = self.value_item.itemAt(0).widget().isChecked()
                ordered = self.value_item.itemAt(1).widget().isChecked()
                unordered = self.value_item.itemAt(2).widget().isChecked()

                request_filter = ""
                if available and ordered and unordered:
                    # don't add any filter because everything selected
                    request_filter = None
                else:
                    # TODO ordered and available don't always exist
                    if available:
                        request_filter += (" OR " if request_filter else "") + "available = 'true'"
                    if ordered:
                        request_filter += (" OR " if request_filter else "") + "(ordered = 'true' AND available <> 'true')"
                    if unordered:
                        request_filter += (" OR " if request_filter else "") + "(ordered <> 'true' AND available <> 'true')"
                if request_filter:
                    request_filters.append("(%s)" % request_filter)

            elif column == CatalogAcquisition.SATELLITE:
                request_filter = ""
                for i in range(self.value_item.count()):
                    checkbox = self.value_item.itemAt(i).widget()
                    if checkbox.isChecked():
                        satellite_value = checkbox.property(SATELLITE_VALUE_KEY)
                        request_filter += (" OR " if request_filter else "") + ("sensorPlatformName = '%s'" % satellite_value)
                if request_filter:
                    request_filters.append("(%s)" % request_filter)

            elif column == CatalogAcquisition.VENDOR:
                vendor = self.escape_value_text(self.value_item.text())
                request_filters.append("vendorName = '%s'" % vendor)

            elif column == CatalogAcquisition.IMAGE_BAND:
                band_index = self.value_item.currentIndex()
                if band_index == 0:
                    request_filters.append("(imageBands = 'Pan' OR imageBands = 'Pan_MS1' OR imageBands = 'Pan_MS1_MS2')")
                elif band_index == 1:
                    request_filters.append("(imageBands = 'Pan_MS1' OR imageBands = 'Pan_MS1_MS2')")
                elif band_index == 2:
                    request_filters.append("(imageBands = 'Pan_MS1_MS2')")

        return request_filters

    def get_column_index(self):
        if self.column_combo:
            current_index = self.column_combo.currentIndex()
            if current_index > 0:
                return current_index - 1
        return None

    def get_datetime_begin(self):
        return self.get_datetime(0)

    def get_datetime_end(self):
        return self.get_datetime(1)

    def get_datetime(self, datetime_index):
        column_index = self.get_column_index()
        if column_index >= 0:
            column = CatalogAcquisition.get_column(column_index)
            if column == CatalogAcquisition.DATE:
                return self.value_item.itemAt(datetime_index).widget().dateTime().toString(DATETIME_FORMAT)
        return None

    def escape_value_text(self, text):
        if text:
            text = text.replace("'", "").replace('"', "")
        return text

