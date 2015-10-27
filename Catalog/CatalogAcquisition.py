# -*- coding: utf-8 -*-

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

    COLUMNS = [CATALOG_ID, STATUS, DATE, SATELLITE, VENDOR, IMAGE_BAND, CLOUD_COVER, SUN_AZM, SUN_ELEV, MULTI_RES, PAN_RES, OFF_NADIR]

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

        self.column_values = [self.identifier, self.status, self.timestamp, self.sensor_platform_name, self.vendor_name, self.image_bands,
                              self.cloud_cover, self.sun_azimuth, self.sun_elevation, self.multi_resolution, self.pan_resolution, self.off_nadir_angle]

    def __str__(self):
        return '"' + '","'.join(self.column_values) + '"'

    def get_column_value(self, property_index):
        return self.column_values[property_index]

    @classmethod
    def get_column(cls, column_index):
        return CatalogAcquisition.COLUMNS[column_index]

    @classmethod
    def get_csv_header(cls):
        return ",".join(CatalogAcquisition.COLUMNS)


def to_bool(text):
    if not text:
        return False
    return text.lower() == "true"

