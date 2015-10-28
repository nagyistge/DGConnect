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
        self.add_blank_filter()

    def add_blank_filter(self):
        filter = self.model.add()
        row_index = self.model.get_row_index(filter.id)

        column_combo = QComboBox()
        if row_index == 0:
            column_combo.addItem(TEXT_COLUMN_WHERE)
        else:
            column_combo.addItem(TEXT_COLUMN_AND)
        for column in CatalogAcquisition.COLUMNS:
            column_combo.addItem(column)
        column_combo.currentIndexChanged.connect(self.filter_where_changed)
        filter.column_combo = column_combo

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
            filter.reset(reset_column=False)
            row_index = self.model.get_row_index(filter_id)
            column = CatalogAcquisition.get_column(column_index)

            specific_filter = None
            if column == CatalogAcquisition.CATALOG_ID:
                specific_filter = CatalogFilterText(filter_id, "catalogID")
            elif column == CatalogAcquisition.STATUS:
                specific_filter = CatalogFilterStatus(filter_id)
            elif column == CatalogAcquisition.DATE:
                specific_filter = CatalogFilterDate(filter_id)
            elif column == CatalogAcquisition.SATELLITE:
                specific_filter = CatalogFilterSatellite(filter_id)
            elif column == CatalogAcquisition.VENDOR:
                specific_filter = CatalogFilterText(filter_id, "vendorName")
            elif column == CatalogAcquisition.IMAGE_BAND:
                specific_filter = CatalogFilterBand(filter_id)
            elif column == CatalogAcquisition.CLOUD_COVER:
                specific_filter = CatalogFilterTextBetween(filter_id, "cloudCover")
            elif column == CatalogAcquisition.SUN_AZM:
                specific_filter = CatalogFilterTextBetween(filter_id, "sunAzimuth")
            elif column == CatalogAcquisition.SUN_ELEV:
                specific_filter = CatalogFilterTextBetween(filter_id, "sunElevation")
            elif column == CatalogAcquisition.MULTI_RES:
                specific_filter = CatalogFilterTextBetween(filter_id, "multiResolution")
            elif column == CatalogAcquisition.PAN_RES:
                specific_filter = CatalogFilterTextBetween(filter_id, "panResolution")
            elif column == CatalogAcquisition.OFF_NADIR:
                specific_filter = CatalogFilterTextBetween(filter_id, "offNadirAngle")

            if specific_filter:
                filter = specific_filter
                self.model.set(filter_id, specific_filter)
                # add label
                self.layout.addWidget(filter.label, row_index, GRID_COLUMN_LABEL)
                # add value item
                if issubclass(type(filter.value_item), QLayout):
                    self.layout.addLayout(filter.value_item, row_index, GRID_COLUMN_VALUE)
                else:
                    self.layout.addWidget(filter.value_item, row_index, GRID_COLUMN_VALUE)
                # add remove button
                if not filter.remove_button:
                    remove_button = QPushButton(TEXT_REMOVE_BUTTON)
                    remove_button.clicked.connect(self.remove_filter)
                    filter.remove_button = remove_button
                    self.layout.addWidget(remove_button, row_index, GRID_COLUMN_ADD)

            # add option to set another filter
            if self.model.is_last_column_set():
                self.add_blank_filter()
        else:
            filter.reset(reset_column=True)

    def get_sender_filter_id(self):
        return self.dialog_ui.dockWidgetContents.sender().property(FILTER_ID_KEY)

    def get_request_filters(self):
        return self.model.get_request_filters()

    def get_datetime_begin(self):
        return self.model.get_datetime_begin()

    def get_datetime_end(self):
        return self.model.get_datetime_end()    


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
            if filter and type(filter) == CatalogFilterDate:
                return filter.get_datetime_begin()
        return None       

    def get_datetime_end(self):
        for filter in self.filters:
            if filter and type(filter) == CatalogFilterDate:
                return filter.get_datetime_end()
        return None              

    def add(self):
        filter = CatalogFilter(str(uuid4()))
        self.filters.append(filter)
        return filter

    def set(self, filter_id, new_filter):
        row_index = self.get_row_index(filter_id)
        new_filter.id = filter_id
        new_filter.column_combo = self.filters[row_index].column_combo
        self.filters[row_index] = new_filter

    def remove(self, filter_id):
        row_index = self.get_row_index(filter_id)
        filter = self.filters[row_index]
        filter.reset()
        self.filters[row_index] = None

    def is_last_column_set(self):
        for i in reversed(range(len(self.filters))): 
            if self.filters[i]:
                return self.filters[i].column_index >= 0
        else:
            return True


class CatalogFilter(object):

    def __init__(self, id): # TODO should id be empty CatalogFilter
        self._id = id
        self._column_combo = None # TODO column_item
        self._label = None
        self._value_item = None
        self._remove_button = None

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, new_id):
        self._id = new_id

    @property
    def column_combo(self):
        return self._column_combo

    @column_combo.setter
    def column_combo(self, new_column_combo):
        if new_column_combo:
            new_column_combo.setProperty(FILTER_ID_KEY, self._id)
        if self._column_combo:
            self._column_combo.setParent(None)
        self._column_combo = new_column_combo

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, new_label):
        if new_label:
            new_label.setProperty(FILTER_ID_KEY, self._id)
        if self._label:
            self._label.setParent(None)
        self._label = new_label

    @property
    def value_item(self):
        return self._value_item

    @value_item.setter
    def value_item(self, new_value_item):
        if new_value_item:
            new_value_item.setProperty(FILTER_ID_KEY, self._id)
        if self._value_item:
            if issubclass(type(self._value_item), QLayout):
                for i in reversed(range(self._value_item.count())):
                    self._value_item.itemAt(i).widget().setParent(None)
                self._value_item.layout().setParent(None)
            else:
                self._value_item.setParent(None)
        self._value_item = new_value_item

    @property
    def remove_button(self):
        return self._remove_button

    @remove_button.setter
    def remove_button(self, new_remove_button):
        if new_remove_button:
            new_remove_button.setProperty(FILTER_ID_KEY, self._id)
        if self._remove_button:
            self._remove_button.setParent(None)
        self._remove_button = new_remove_button

    @property
    def column_index(self):
        if self._column_combo:
            current_index = self._column_combo.currentIndex()
            if current_index > 0:
                return current_index - 1
        return None

    def get_request_filters(self):
        return []

    def merge(self, other_filter):
        self._id = other_filter.id
        return self

    def reset(self, reset_column=True):
        if reset_column:
            self.column_combo = None
        self.label = None
        self.value_item = None
        self.remove_button = None

    def escape_value_text(self, text):
        if text:
            text = text.replace("'", "").replace('"', "")
        return text

    def __str__(self):
        return self._id

    def __hash__(self):
        return hash(self._id)

    def __eq__(self, other):
        return self._id == other.id

    def __ne__(self, other):
        return self._id != other.id

    def __le__(self, other):
        return self._id <= other.id

    def __lt__(self, other):
        return self._id < other.id

    def __ge__(self, other):
        return self._id >= other.id

    def __gt__(self, other):
        return self._id > other.id

    def __cmp__(self, other):
        return cmp(self._id, other.id)


class CatalogFilterText(CatalogFilter):

    def __init__(self, id, request_key):
        super(self.__class__, self).__init__(id)
        self.request_key = request_key
        self.label = QLabel(TEXT_LABEL_IS)
        self.value_item = QLineEdit()

    def get_request_filters(self):
        value_text = self.escape_value_text(self.value_item.text())
        return ["%s = '%s'" % (self.request_key, value_text)]


class CatalogFilterStatus(CatalogFilter):

    def __init__(self, id):
        super(self.__class__, self).__init__(id)
        self.label = QLabel(TEXT_LABEL_IS)
        self.available_checkbox = QCheckBox(TEXT_STATUS_AVAILABLE)
        self.ordered_checkbox = QCheckBox(TEXT_STATUS_ORDERED)
        self.unordered_checkbox = QCheckBox(TEXT_STATUS_UNORDERED)

        value_item = QGridLayout()
        value_item.addWidget(self.available_checkbox, 0, 0)
        value_item.addWidget(self.ordered_checkbox, 0, 1)
        value_item.addWidget(self.unordered_checkbox, 0, 2)
        self.value_item = value_item

    def get_request_filters(self):
        available = self.available_checkbox.isChecked()
        ordered = self.ordered_checkbox.isChecked()
        unordered = self.unordered_checkbox.isChecked()

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
            return [request_filter]
        else:
            return []


class CatalogFilterDate(CatalogFilter):

    def __init__(self, id):
        super(self.__class__, self).__init__(id)
        self.label = QLabel(TEXT_LABEL_BETWEEN)
        self.datetime_begin_edit = QDateEdit(QDate.currentDate())
        self.datetime_end_edit = QDateEdit(QDate.currentDate())

        value_item = QGridLayout()
        value_item.addWidget(self.datetime_begin_edit, 0, 0)
        value_item.addWidget(self.datetime_end_edit, 0, 1)
        self.value_item = value_item

    def get_request_filters(self):
        return []

    def get_datetime_begin(self):
        return self.datetime_begin_edit.dateTime().toString(DATETIME_FORMAT)

    def get_datetime_end(self):
        return self.datetime_end_edit.dateTime().toString(DATETIME_FORMAT)


class CatalogFilterSatellite(CatalogFilter):

    def __init__(self, id):
        super(self.__class__, self).__init__(id)
        self.checkboxes = []
        self.label = QLabel(TEXT_LABEL_IS)

        value_item = QGridLayout()
        value_item.addWidget(self.create_satellite_checkbox(TEXT_SATELLITE_WV1, VALUE_SATELLITE_WV1), 0, 0)
        value_item.addWidget(self.create_satellite_checkbox(TEXT_SATELLITE_WV2, VALUE_SATELLITE_WV2), 0, 1)
        value_item.addWidget(self.create_satellite_checkbox(TEXT_SATELLITE_WV3, VALUE_SATELLITE_WV3), 0, 2)
        value_item.addWidget(self.create_satellite_checkbox(TEXT_SATELLITE_GEO, VALUE_SATELLITE_GEO), 0, 3)
        value_item.addWidget(self.create_satellite_checkbox(TEXT_SATELLITE_QB2, VALUE_SATELLITE_QB2), 0, 4)
        self.value_item = value_item

    def get_request_filters(self):
        request_filter = ""
        for checkbox in self.checkboxes:
            if checkbox.isChecked():
                satellite_value = checkbox.property(SATELLITE_VALUE_KEY)
                request_filter += (" OR " if request_filter else "") + ("sensorPlatformName = '%s'" % satellite_value)
        if request_filter:
            request_filter = "(%s)" % request_filter
            return [request_filter]
        else:
            return []

    def create_satellite_checkbox(self, display_text, value_text):
        checkbox = QCheckBox(display_text)
        checkbox.setProperty(SATELLITE_VALUE_KEY, value_text)
        self.checkboxes.append(checkbox)
        return checkbox


class CatalogFilterBand(CatalogFilter):

    def __init__(self, id):
        super(self.__class__, self).__init__(id)
        self.checkboxes = []
        self.label = QLabel(TEXT_LABEL_IS)

        value_item = QComboBox()
        value_item.addItem(TEXT_BAND_PAN)
        value_item.addItem(TEXT_BAND_MS1)
        value_item.addItem(TEXT_BAND_MS2)
        self.value_item = value_item

    def get_request_filters(self):
        band_index = self.value_item.currentIndex()
        if band_index == 0:
            return ["(imageBands = 'Pan' OR imageBands = 'Pan_MS1' OR imageBands = 'Pan_MS1_MS2')"]
        elif band_index == 1:
            return ["(imageBands = 'Pan_MS1' OR imageBands = 'Pan_MS1_MS2')"]
        elif band_index == 2:
            return ["(imageBands = 'Pan_MS1_MS2')"]
        return []


class CatalogFilterTextBetween(CatalogFilter):

    def __init__(self, id, request_key):
        super(self.__class__, self).__init__(id)
        self.request_key = request_key
        self.label = QLabel(TEXT_LABEL_BETWEEN)
        self.from_edit = QLineEdit()
        self.to_edit = QLineEdit()

        value_item = QGridLayout()
        value_item.addWidget(self.from_edit, 0, 0)
        value_item.addWidget(self.to_edit, 0, 1)
        self.value_item = value_item

    def get_request_filters(self):
        request_filters = []
        from_value = self.from_edit.text()
        to_value = self.to_edit.text()
        request_filters.append("%s >= '%s'" % (self.request_key, from_value))
        request_filters.append("%s <= '%s'" % (self.request_key, to_value))
        return request_filters

