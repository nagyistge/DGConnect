# -*- coding: utf-8 -*-
import os
from qgis.core import QgsMessageLog
import re
from uuid import uuid4

from CatalogAcquisition import CatalogAcquisition
from PyQt4.QtCore import Qt, QObject, pyqtSlot, pyqtSignal, QVariant, QAbstractTableModel, SIGNAL
from PyQt4.QtGui import QComboBox, QLabel, QLineEdit, QPushButton, QGridLayout, QCheckBox, QLayout


FILTER_COLUMN_INDEX_WHERE = 0
FILTER_COLUMN_INDEX_LABEL = 1
FILTER_COLUMN_INDEX_VALUE = 2
FILTER_COLUMN_INDEX_ADD = 3

FILTER_ID_KEY = "filter_id"
SATELLITE_VALUE_KEY = "satellite_value"


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
            column_combo.addItem("Where...")
        else:
            column_combo.addItem("And...")
        for column in CatalogAcquisition.COLUMNS:
            column_combo.addItem(column)
        column_combo.currentIndexChanged.connect(self.filter_where_changed)
        self.model.set_column_combo(filter_id, column_combo)

        self.layout.addWidget(column_combo, row_index, FILTER_COLUMN_INDEX_WHERE)

    def remove_filter(self):
        filter_id = self.get_sender_filter_id()
        filter = self.model.get_filter(filter_id)
        self.model.remove(filter_id)

    def filter_where_changed(self, index):
        column_index = index - 1
        filter_id = self.get_sender_filter_id()
        filter = self.model.get_filter(filter_id)

        if column_index >= 0:
            label_text = None
            value_widget = None
            row_index = self.model.get_row_index(filter_id)
            column = CatalogAcquisition.get_column(column_index)

            # TODO constants
            if column == CatalogAcquisition.CATALOG_ID:
                label_text = " is "
                value_widget = QLineEdit()
                self.layout.addWidget(value_widget, row_index, FILTER_COLUMN_INDEX_VALUE)
            elif column == CatalogAcquisition.SATELLITE:
                label_text = " is "
                value_widget = QGridLayout()
                value_widget.addWidget(self.create_satellite_checkbox("WorldView-1", "WORLDVIEW01"), 0, 0)
                value_widget.addWidget(self.create_satellite_checkbox("WorldView-2", "WORLDVIEW02"), 0, 1)
                value_widget.addWidget(self.create_satellite_checkbox("WorldView-3", "WORLDVIEW03"), 0, 2)
                value_widget.addWidget(self.create_satellite_checkbox("GeoEye-1", "GEOEYE01"), 0, 3)
                value_widget.addWidget(self.create_satellite_checkbox("QuickBird", "QUICKBIRD02"), 0, 4)
                self.layout.addLayout(value_widget, row_index, FILTER_COLUMN_INDEX_VALUE)

            if label_text:
                label = QLabel(label_text)
                self.model.set_label(filter_id, label)
                self.layout.addWidget(label, row_index, FILTER_COLUMN_INDEX_LABEL)
            if value_widget:
                self.model.set_value_widget(filter_id, value_widget)

            if not filter.remove_button:
                remove_button = QPushButton("-")
                remove_button.clicked.connect(self.remove_filter)
                self.model.set_remove_button(filter_id, remove_button)
                self.layout.addWidget(remove_button, row_index, FILTER_COLUMN_INDEX_ADD)

            if self.model.is_last_column_set():
                self.add_filter()

        else:
            self.model.reset(filter_id)

    def get_sender_filter_id(self):
        return self.dialog_ui.dockWidgetContents.sender().property(FILTER_ID_KEY)

    def get_request_filters(self):
        return self.model.get_request_filters()

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

    def set_value_widget(self, filter_id, value_widget):
        filter = self.get_filter(filter_id)
        if value_widget:
            value_widget.setProperty(FILTER_ID_KEY, filter_id)
        if filter.value_widget:
            if issubclass(type(filter.value_widget), QLayout):
                for i in reversed(range(filter.value_widget.count())): 
                    filter.value_widget.itemAt(i).widget().setParent(None)
                filter.value_widget.layout().setParent(None)
            else:
                filter.value_widget.setParent(None)
        filter.value_widget = value_widget

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
        self.set_value_widget(filter_id, None)
        self.set_remove_button(filter_id, None)

    def remove(self, filter_id):
        self.reset(filter_id)
        row_index = self.get_row_index(filter_id)
        self.filters[row_index] = None

    def is_last_column_set(self):
        if self.filters:
            return self.filters[-1].get_column_index() >= 0
        else:
            return True


class CatalogFilter(object):

    def __init__(self):
        self.id = str(uuid4())
        self.column_combo = None
        self.label = None
        self.value_widget = None
        self.remove_button = None

    def get_request_filters(self):
        request_filters = []
        column = CatalogAcquisition.get_column(self.get_column_index())
        if column == CatalogAcquisition.CATALOG_ID:
            catalog_id = self.value_widget.text()
            request_filters.append("catalogID = '%s'" % catalog_id)
        elif column == CatalogAcquisition.SATELLITE:
            for i in (0, self.value_widget.count()):
                checkbox = self.value_widget.itemAt(i)
                if not checkbox.isChecked():
                    satellite_value = checkbox.property(SATELLITE_VALUE_KEY)
                    request_filters.append("sensorPlatformName <> '%s'" % satellite_value)
        return request_filters

    def get_column_index(self):
        if self.column_combo:
            current_index = self.column_combo.currentIndex()
            if current_index > 0:
                return current_index - 1
        return None

