# -*- coding: utf-8 -*-
import os
from qgis.core import QgsMessageLog
import re
from uuid import uuid4

from ..Common.ExampleLineEdit import ExampleLineEdit
from CatalogAcquisition import CatalogAcquisition
from PyQt4.QtCore import Qt, QObject, pyqtSlot, pyqtSignal, QVariant, QAbstractTableModel, SIGNAL, QDate
from PyQt4.QtGui import QComboBox, QLabel, QLineEdit, QPushButton, QGridLayout, QCheckBox, QLayout, QDateEdit, QRadioButton, QSizePolicy


FILTER_ID_KEY = "filter_id"
SATELLITE_VALUE_KEY = "satellite_value"
DATETIME_FORMAT = "yyyy-MM-ddT00:00:00.000Z"

GRID_COLUMN_OPERATOR = 0
GRID_COLUMN_WHERE = 1
GRID_COLUMN_LABEL = 2
GRID_COLUMN_VALUE = 3
GRID_COLUMN_ADD = 4

TEXT_OPERATOR_AND = "And"
TEXT_OPERATOR_OR = "Or"
TEXT_COLUMN_WHERE = "Where..."
TEXT_LABEL_BETWEEN = " between "
TEXT_LABEL_IS = " is "
TEXT_LABEL_AND = " and "
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
 
        column_item = QComboBox()
        column_item.addItem(TEXT_COLUMN_WHERE) 
        for column in CatalogAcquisition.COLUMNS:
            column_item.addItem(column.name)
        column_item.currentIndexChanged.connect(self.column_changed)
        self.layout.addWidget(column_item, row_index, GRID_COLUMN_WHERE)
        filter.column_item = column_item

        # add operator item
        # if self.model.get_num_filters() > 1:
        #     operator_item = QComboBox()
        #     operator_item.addItem(TEXT_OPERATOR_AND)
        #     operator_item.addItem(TEXT_OPERATOR_OR)
        #     self.layout.addWidget(operator_item, row_index, GRID_COLUMN_OPERATOR)
        #     filter.operator_item = operator_item

    def remove(self):
        filter_id = self.get_sender_filter_id()
        self.model.remove(filter_id)
        # if only blank filter remains then start from scratch
        if self.model.get_num_filters() <= 1:
            self.remove_all()

    def remove_all(self):
        self.model.remove_all()
        self.add_blank_filter()

    def column_changed(self, index):
        filter_id = self.get_sender_filter_id()
        filter = self.model.get_filter(filter_id)
        column = filter.column_name

        if column:
            filter.reset(reset_column=False)
            row_index = self.model.get_row_index(filter_id)

            specific_filter = None
            if column == CatalogAcquisition.CATALOG_ID:
                specific_filter = CatalogFilterId(filter_id)
            elif column == CatalogAcquisition.STATUS:
                specific_filter = CatalogFilterStatus(filter_id)
            elif column == CatalogAcquisition.DATE:
                specific_filter = CatalogFilterDate(filter_id)
            elif column == CatalogAcquisition.SATELLITE:
                specific_filter = CatalogFilterSatellite(filter_id)
            elif column == CatalogAcquisition.VENDOR:
                specific_filter = CatalogFilterText(filter_id, "vendorName", "DigitalGlobe")
            elif column == CatalogAcquisition.IMAGE_BAND:
                specific_filter = CatalogFilterText(filter_id, "imageBands", "Pan_MS1_MS2")
            elif column == CatalogAcquisition.CLOUD_COVER:
                specific_filter = CatalogFilterTextBetween(filter_id, "cloudCover", "0.0", "100.0")
            elif column == CatalogAcquisition.SUN_AZM:
                specific_filter = CatalogFilterTextBetween(filter_id, "sunAzimuth", "0.0", "360.0")
            elif column == CatalogAcquisition.SUN_ELEV:
                specific_filter = CatalogFilterTextBetween(filter_id, "sunElevation", "0.0", "90.0")
            elif column == CatalogAcquisition.MULTI_RES:
                specific_filter = CatalogFilterTextBetween(filter_id, "multiResolution", "0.0", "10.0")
            elif column == CatalogAcquisition.PAN_RES:
                specific_filter = CatalogFilterTextBetween(filter_id, "panResolution", "0.0", "2.0")
            elif column == CatalogAcquisition.OFF_NADIR:
                specific_filter = CatalogFilterTextBetween(filter_id, "offNadirAngle", "1.0", "90.0")

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
                    remove_button.clicked.connect(self.remove)
                    filter.remove_button = remove_button
                    self.layout.addWidget(remove_button, row_index, GRID_COLUMN_ADD)

            # add option to set another filter
            if self.model.is_last_column_set():
                self.add_blank_filter()
        else:
            filter.reset(reset_column=True)

    def get_sender_filter_id(self):
        return self.dialog_ui.dockWidgetContents.sender().property(FILTER_ID_KEY)

    def validate(self, errors):
        self.model.validate(errors)

    def get_query_filters(self):
        return self.model.get_query_filters()

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

    def get_num_filters(self):
        num_filters = 0
        for filter in self.filters:
            if filter:
                num_filters += 1
        return num_filters

    def get_row_index(self, filter_id):
        for i in range(0, len(self.filters)):
            if self.filters[i] and self.filters[i].id == filter_id:
                return i
        return None

    def validate(self, errors):
        for filter in self.filters:
            if filter:
                filter.validate(errors)

    def get_query_filters(self):
        filter_groups = []
        current_filter_group = None
        for filter in self.filters:
            if filter and filter.column_name:
                if current_filter_group:
                    if filter.is_operator_and:
                        filter_groups.append(current_filter_group)
                        current_filter_group = [filter]
                    else:
                        current_filter_group.append(filter)
                else:
                    current_filter_group = [filter]
        if current_filter_group:
            filter_groups.append(current_filter_group)

        query_filters = []
        for filter_group in filter_groups:
            if len(filter_group) == 1:
                query_filters.extend(filter_group[0].get_query_filters())
            elif len(filter_group) > 1:
                query_filter = ""
                for filter in filter_group:
                    query_filter += " (%s) OR " % self.get_anded_query_filter(filter.get_query_filters())
                query_filter = query_filter.strip()[:-3]
                query_filters.append(query_filter)
        return query_filters

    def get_anded_query_filter(self, query_filters):
        combined_query_filter = ""
        for query_filter in query_filters:
            combined_query_filter += " %s AND " % query_filter
        combined_query_filter = combined_query_filter.strip()[:-4]
        return combined_query_filter

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
        new_filter.column_item = self.filters[row_index].column_item
        new_filter.operator_item = self.filters[row_index].operator_item
        self.filters[row_index] = new_filter

    def remove(self, filter_id):
        row_index = self.get_row_index(filter_id)
        filter = self.filters[row_index]
        filter.reset()
        self.filters[row_index] = None

    def remove_all(self):
        for filter in self.filters:
            if filter:
                self.remove(filter.id)

    def is_last_column_set(self):
        for i in reversed(range(len(self.filters))): 
            if self.filters[i]:
                return self.filters[i].column_index >= 0
        else:
            return True


class CatalogFilter(object):

    def __init__(self, id):
        self._id = id
        self._operator_item = None
        self._column_item = None
        self._label = None
        self._value_item = None
        self._remove_button = None

    def get_query_filters(self):
        return []

    def validate(self, errors):
        return

    def reset(self, reset_column=True):
        if reset_column:
            self.operator_item = None
            self.column_item = None
        self.label = None
        self.value_item = None
        self.remove_button = None

    def escape_value_text(self, text):
        if text:
            text = text.replace("'", "").replace('"', "")
        return text

    def expand_layout(self, layout):
        last_widget = layout.itemAt(layout.count() - 1).widget()
        self.expand_widget(last_widget)

    def expand_widget(self, widget):
        widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, new_id):
        self._id = new_id

    @property
    def operator_item(self):
        return self._operator_item

    @operator_item.setter
    def operator_item(self, new_operator_item):
        if new_operator_item:
            new_operator_item.setProperty(FILTER_ID_KEY, self._id)
        if self._operator_item:
            self._operator_item.setParent(None)
        self._operator_item = new_operator_item

    @property
    def column_item(self):
        return self._column_item

    @column_item.setter
    def column_item(self, new_column_item):
        if new_column_item:
            new_column_item.setProperty(FILTER_ID_KEY, self._id)
        if self._column_item:
            self._column_item.setParent(None)
        self._column_item = new_column_item

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
        column_name = self.column_name
        for i in range(len(CatalogAcquisition.COLUMNS)):
            if column_name == CatalogAcquisition.COLUMNS[i].name:
                return i
        return None

    @property
    def column_name(self):
        if self._column_item.currentIndex() > 0: # exclude initial non-column item
            return self._column_item.currentText()
        else:
            return None

    @property
    def is_operator_and(self):
        return not self._operator_item or self._operator_item.currentText() == TEXT_OPERATOR_AND

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

    def __init__(self, id, query_field, example_text=""):
        super(CatalogFilterText, self).__init__(id)
        self.query_field = query_field
        self.label = QLabel(TEXT_LABEL_IS)
        self.value_item = ExampleLineEdit(example_text)

    def get_query_filters(self):
        return ["%s = '%s'" % (self.query_field, self.get_value())]

    def validate(self, errors):
        if not self.get_value():
            errors.append("Value is required for %s filter." % self.column_name)
    
    def get_value(self):
        return self.escape_value_text(self.value_item.text())


class CatalogFilterId(CatalogFilterText):

    def __init__(self, id):
        super(CatalogFilterId, self).__init__(id, "catalogID", "104001234567A890")

    def get_query_filters(self):
        query_filter = ""
        cat_ids = [val.strip() for val in self.get_value().split(",")]
        for cat_id in cat_ids:
            query_filter += " %s = '%s' OR " % (self.query_field, self.escape_value_text(cat_id))
        return [query_filter.strip()[:-3]]


class CatalogFilterStatus(CatalogFilter):

    def __init__(self, id):
        super(CatalogFilterStatus, self).__init__(id)
        self.label = QLabel(TEXT_LABEL_IS)
        self.available_checkbox = QCheckBox(TEXT_STATUS_AVAILABLE)
        self.ordered_checkbox = QCheckBox(TEXT_STATUS_ORDERED)
        self.unordered_checkbox = QCheckBox(TEXT_STATUS_UNORDERED)

        value_item = QGridLayout()
        value_item.addWidget(self.available_checkbox, 0, 0)
        value_item.addWidget(self.ordered_checkbox, 0, 1)
        value_item.addWidget(self.unordered_checkbox, 0, 2)
        self.expand_layout(value_item)
        self.value_item = value_item

    def get_query_filters(self):
        available = self.available_checkbox.isChecked()
        ordered = self.ordered_checkbox.isChecked()
        unordered = self.unordered_checkbox.isChecked()

        query_filter = ""
        if available and ordered and unordered:
            # don't add any filter because everything selected
            query_filter = None
        else:
            if available:
                query_filter += (" OR " if query_filter else "") + "available = 'true'"
            if ordered:
                query_filter += (" OR " if query_filter else "") + "(ordered = 'true' AND available <> 'true')"
            if unordered:
                query_filter += (" OR " if query_filter else "") + "(ordered <> 'true' AND available <> 'true')"
        if query_filter:
            query_filters.append("(%s)" % query_filter)
            return [query_filter]
        else:
            return []

    def validate(self, errors):
        available = self.available_checkbox.isChecked()
        ordered = self.ordered_checkbox.isChecked()
        unordered = self.unordered_checkbox.isChecked()
        if not available and not ordered and not unordered:
            errors.append("At least one value must be selected for %s filter." % self.column_name)


class CatalogFilterDate(CatalogFilter):

    def __init__(self, id):
        super(CatalogFilterDate, self).__init__(id)
        self.label = QLabel(TEXT_LABEL_BETWEEN)

        self.datetime_begin_edit = QDateEdit(QDate.currentDate())
        self.datetime_end_edit = QDateEdit(QDate.currentDate())
        self.expand_widget(self.datetime_begin_edit)
        self.expand_widget(self.datetime_end_edit)

        value_item = QGridLayout()
        value_item.addWidget(self.datetime_begin_edit, 0, 0)
        value_item.addWidget(QLabel(TEXT_LABEL_AND), 0, 1)
        value_item.addWidget(self.datetime_end_edit, 0, 2)
        self.value_item = value_item

    def get_query_filters(self):
        # date request filter values are returned by get_datetime_begin/end
        return []

    def validate(self, errors):
        datetime_begin = self.datetime_begin_edit.dateTime()
        datetime_end = self.datetime_end_edit.dateTime()
        if datetime_begin.daysTo(datetime_end) < 0:
            errors.append("First value must be less than or equal to second for %s filter." % self.column_name)

    def get_datetime_begin(self):
        return self.datetime_begin_edit.dateTime().toString(DATETIME_FORMAT)

    def get_datetime_end(self):
        return self.datetime_end_edit.dateTime().toString(DATETIME_FORMAT)


class CatalogFilterSatellite(CatalogFilter):

    def __init__(self, id):
        super(CatalogFilterSatellite, self).__init__(id)
        self.checkboxes = []
        self.label = QLabel(TEXT_LABEL_IS)

        value_item = QGridLayout()
        value_item.addWidget(self.create_satellite_checkbox(TEXT_SATELLITE_WV1, VALUE_SATELLITE_WV1), 0, 0)
        value_item.addWidget(self.create_satellite_checkbox(TEXT_SATELLITE_WV2, VALUE_SATELLITE_WV2), 0, 1)
        value_item.addWidget(self.create_satellite_checkbox(TEXT_SATELLITE_WV3, VALUE_SATELLITE_WV3), 0, 2)
        value_item.addWidget(self.create_satellite_checkbox(TEXT_SATELLITE_GEO, VALUE_SATELLITE_GEO), 0, 3)
        value_item.addWidget(self.create_satellite_checkbox(TEXT_SATELLITE_QB2, VALUE_SATELLITE_QB2), 0, 4)
        self.expand_layout(value_item)
        self.value_item = value_item

    def get_query_filters(self):
        query_filter = ""
        for checkbox in self.checkboxes:
            if checkbox.isChecked():
                satellite_value = checkbox.property(SATELLITE_VALUE_KEY)
                query_filter += (" OR " if query_filter else "") + ("sensorPlatformName = '%s'" % satellite_value)
        if query_filter:
            query_filter = "(%s)" % query_filter
            return [query_filter]
        else:
            return []

    def validate(self, errors):
        at_least_one_checkbox_checked = False
        for checkbox in self.checkboxes:
            if checkbox.isChecked():
                at_least_one_checkbox_checked = True
                break
        if not at_least_one_checkbox_checked:
            errors.append("At least one value must be selected for %s filter." % self.column_name)

    def create_satellite_checkbox(self, display_text, value_text):
        checkbox = QCheckBox(display_text)
        checkbox.setProperty(SATELLITE_VALUE_KEY, value_text)
        self.checkboxes.append(checkbox)
        return checkbox


class CatalogFilterTextBetween(CatalogFilter):

    def __init__(self, id, query_field, from_example_text="", to_example_text=""):
        super(CatalogFilterTextBetween, self).__init__(id)
        self.query_field = query_field
        self.label = QLabel(TEXT_LABEL_BETWEEN)
        self.from_edit = ExampleLineEdit(from_example_text)
        self.to_edit = ExampleLineEdit(to_example_text)

        value_item = QGridLayout()
        value_item.addWidget(self.from_edit, 0, 0)
        value_item.addWidget(QLabel(TEXT_LABEL_AND), 0, 1)
        value_item.addWidget(self.to_edit, 0, 2)
        self.value_item = value_item

    def get_query_filters(self):
        query_filters = []
        from_value = self.get_from_value()
        to_value = self.get_to_value()
        if from_value:
            query_filters.append("%s >= '%s'" % (self.query_field, from_value))
        if to_value:
            query_filters.append("%s <= '%s'" % (self.query_field, to_value))
        return query_filters

    def validate(self, errors):
        from_value = self.get_from_value()
        if from_value:
                try:
                    from_value = float(from_value)
                except ValueError:
                    errors.append("First value is invalid for %s filter." % self.column_name)
                    from_value = None
        else:
            from_value = None
        to_value = self.get_to_value()
        if to_value:
                try:
                    to_value = float(to_value)
                except ValueError:
                    errors.append("Second value is invalid for %s filter." % self.column_name)
                    from_value = None
        else:
            to_value = None

        if from_value is None and to_value is None:
            errors.append("At least one value is required for %s filter." % self.column_name)
        elif from_value is not None and to_value is not None and from_value > to_value:
            errors.append("First value must be less than or equal to second for %s filter." % self.column_name)

    def get_from_value(self):
        return self.from_edit.text()

    def get_to_value(self):
        return self.to_edit.text()

