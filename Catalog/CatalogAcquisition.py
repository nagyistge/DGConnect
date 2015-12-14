# -*- coding: utf-8 -*-
from qgis._core import QgsFeature, QgsField, QgsFields, QgsGeometry
from PyQt4.QtCore import QVariant


class CatalogAcquisitionColumn(object):
    
    def __init__(self, name, column_type=str):
        self.name = name
        self.column_type = column_type

    def __str__(self):
        return self.name


class CatalogAcquisition(object):
    """
    Entry in the GUI model of acquisitions
    """

    CATALOG_ID = "Catalog ID"
    STATUS = "Status"
    DATE = "Date"
    SATELLITE = "Satellite"
    VENDOR = "Vendor"
    IMAGE_BAND = "Image Band"
    CLOUD_COVER = "Cloud %"
    SUN_AZM = "Sun Azm."
    SUN_ELEV = "Sun Elev."
    MULTI_RES = "Multi Res."
    PAN_RES = "Pan Res."
    OFF_NADIR = "Off Nadir"

    COLUMNS = [CatalogAcquisitionColumn(CATALOG_ID),
               CatalogAcquisitionColumn(STATUS),
               CatalogAcquisitionColumn(DATE),
               CatalogAcquisitionColumn(SATELLITE),
               CatalogAcquisitionColumn(VENDOR),
               CatalogAcquisitionColumn(IMAGE_BAND),
               CatalogAcquisitionColumn(CLOUD_COVER, float),
               CatalogAcquisitionColumn(SUN_AZM, float),
               CatalogAcquisitionColumn(SUN_ELEV, float),
               CatalogAcquisitionColumn(MULTI_RES, float),
               CatalogAcquisitionColumn(PAN_RES, float),
               CatalogAcquisitionColumn(OFF_NADIR, float)]

    def __init__(self, result):
        """
        Constructor
        :param result: acquisition result json 
        :return: CatalogAcquisition
        """

        self.identifier = str(result[u"identifier"])

        properties = result.get(u"properties")

        # determine status
        available = properties.get(u"available")
        ordered = properties.get(u"ordered")
        self.status = "Available" if to_bool(available) else "Ordered" if to_bool(ordered) else "Unordered"

        # get timestamp and remove time because it's always 00:00:00
        self.timestamp = properties.get(u"timestamp")
        if self.timestamp:
            self.timestamp = self.timestamp[:10] 

        self.sensor_platform_name = properties.get(u"sensorPlatformName")
        self.vendor_name = properties.get(u"vendorName")
        self.image_bands = properties.get(u"imageBands")
        self.cloud_cover = properties.get(u"cloudCover")
        self.sun_azimuth = properties.get(u"sunAzimuth")
        self.sun_elevation = properties.get(u"sunElevation")
        self.multi_resolution = properties.get(u"multiResolution")
        self.pan_resolution = properties.get(u"panResolution")
        self.off_nadir_angle = properties.get(u"offNadirAngle")
        
        self.target_azimuth = properties.get(u"targetAzimuth")
        self.browse_url = properties.get(u"browseURL")
        self.footprint_wkt = properties.get(u"footprintWkt")

        self.column_values = []
        self.add_column_value(self.identifier)
        self.add_column_value(self.status)
        self.add_column_value(self.timestamp)
        self.add_column_value(self.sensor_platform_name)
        self.add_column_value(self.vendor_name)
        self.add_column_value(self.image_bands)
        self.add_column_value(self.cloud_cover)
        self.add_column_value(self.sun_azimuth)
        self.add_column_value(self.sun_elevation)
        self.add_column_value(self.multi_resolution)
        self.add_column_value(self.pan_resolution)
        self.add_column_value(self.off_nadir_angle)

    def __str__(self):
        return '"' + '","'.join([str(val) for val in self.column_values]) + '"'

    def get_column_value(self, column_index):
        return self.column_values[column_index]

    def add_column_value(self, column_value_text):
        column_index = len(self.column_values)
        column_type = CatalogAcquisition.COLUMNS[column_index].column_type
        column_value = None
        if column_value_text is not None:
           column_value = column_type(column_value_text)
        self.column_values.append(column_value)

    @classmethod
    def get_column(cls, column_index):
        return CatalogAcquisition.COLUMNS[column_index].name

    @classmethod
    def get_csv_header(cls):
        return ",".join([column.name for column in CatalogAcquisition.COLUMNS])


class CatalogAcquisitionFeature(QgsFeature):

    def __init__(self, row, acquisition):
        """
        Constructor
        :param acquisition: 
        :return: CatalogAcquisitionFeature
        """
        super(CatalogAcquisitionFeature, self).__init__(id=row)
        self.acquisition = acquisition
        self.init_fields()
        self.init_attributes()
        self.init_geometry()

    def init_fields(self):
        self.setFields(CatalogAcquisitionFeature.get_fields())

    def init_attributes(self):
        attributes = []
        for column_value in self.acquisition.column_values:
            attributes.append(column_value)
        self.setAttributes(attributes)

    def init_geometry(self):
        geometry = QgsGeometry.fromWkt(self.acquisition.footprint_wkt)
        self.setGeometry(geometry)

    @classmethod
    def get_fields(cls):
        fields = QgsFields()
        for column in CatalogAcquisition.COLUMNS:
            field_type = None
            if column.column_type == float:
                field_type = QVariant.Double
            else:
                field_type = QVariant.String
            fields.append(QgsField(column.name, field_type))
        return fields

def to_bool(text):
    if not text:
        return False
    return text.lower() == "true"

