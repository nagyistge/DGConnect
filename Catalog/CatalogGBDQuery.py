# -*- coding: utf-8 -*-
__author__ = 'Michael Trotter <michael.trotter@digitalglobe.com>'

from base64 import b64encode
import cookielib
from datetime import timedelta, datetime
import json
from qgis.core import QgsMessageLog
from string import Template
import urllib
import urllib2

from ..Common.OAuth2Query import OAuth2Query


# User Agent String; let's pretend we're chromium on Ubuntu
USER_AGENT_STRING = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                    'Ubuntu Chromium/41.0.2272.76 Chrome/41.0.2272.76 Safari/537.36'

# polygon template for gbd ordering
POLYGON_TEMPLATE = Template("POLYGON (($left $bottom, $left $top, $right $top, $right $bottom, $left $bottom))")

# gbd urls
TOP_LEVEL_URL = 'https://geobigdata.io/'
ACQUISITION_SEARCH_URL = TOP_LEVEL_URL + "/catalog/v1/search?includeRelationships=false"

# data format for parsing
ISO_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'

# json keys
JSON_ENCODING = 'utf8'
KEY_ACCESS_TOKEN = 'access_token'
KEY_TOKEN_TYPE = 'token_type'

# http headers
HEADER_AUTHORIZATION = 'Authorization'
HEADER_USER_AGENT = 'User-Agent'
HEADER_CONTENT_TYPE = 'Content-Type'
CONTENT_TYPE_JSON = 'application/json'

# data keys and some values
KEY_DATA_SEARCH_AREA_WKT = 'searchAreaWkt'
KEY_DATA_START_DATE = 'startDate'
KEY_DATA_END_DATE = 'endDate'
KEY_DATA_FILTERS = 'filters'
KEY_DATA_TAG_RESULTS = 'tagResults'
VALUE_DATA_TAG_RESULTS = False
KEY_DATA_TYPES = 'types'
VALUE_DATA_TYPES = ['DigitalGlobeAcquisition']

# JSON Keys
KEY_JSON_RESULTS = u'results'
KEY_JSON_PROPERTIES = u'properties'
KEY_JSON_TIMESTAMP = u'timestamp'

# tag name
TAG_NAME = 'GBDX'


class GBDOrderParams:
    """
    Class for managing GBD params
    """

    def __init__(self, top, bottom, left, right, time_begin=None, time_end=None, filters=None):
        self.top = top
        self.bottom = bottom
        self.left = left
        self.right = right
        self.time_begin = time_begin
        self.time_end = time_end
        self.filters = filters
        self.polygon = self.build_polygon()

    def build_polygon(self):
        """
        Builds the polygon field from the POLYGON_TEMPLATE
        :return: The polygon field
        """
        return POLYGON_TEMPLATE.substitute(top=str(self.top), right=(str(self.right)), bottom=str(self.bottom), left=str(self.left))


class GBDQuery(OAuth2Query):
    """
    Class for querying GBD raster data
    """

    def __init__(self, username, password, api_key, grant_type='password'):
        super(GBDQuery, self).__init__(username, password, api_key, grant_type)

    def acquisition_search(self, order_params):
        """
        Performs a search for acquisitions.
        :param order_params: The order params for the GBD query
        :return:
        """
        self.log_in()

        # build request body json
        request_body = {
            KEY_DATA_SEARCH_AREA_WKT: order_params.polygon,
            KEY_DATA_FILTERS: order_params.filters,
            KEY_DATA_TAG_RESULTS: VALUE_DATA_TAG_RESULTS,
            KEY_DATA_TYPES: VALUE_DATA_TYPES
        }
        if order_params.time_begin:
            request_body[KEY_DATA_START_DATE] = order_params.time_begin
        if order_params.time_end:
            request_body[KEY_DATA_END_DATE] = order_params.time_end
        request_body_json = json.dumps(request_body)

        # build header
        headers = self.headers.copy()
        headers[HEADER_CONTENT_TYPE] = CONTENT_TYPE_JSON

        try:
            request = urllib2.Request(ACQUISITION_SEARCH_URL, request_body_json, headers)
            response = self.opener.open(request)
            response_data = response.read()
            result_data = json.loads(response_data, strict=False)
            return result_data
        except Exception, e:
            QgsMessageLog.instance().logMessage("Exception during acquisition search: " + str(e), TAG_NAME, level=QgsMessageLog.CRITICAL)

        return None

    @classmethod
    def update_csv_data(cls, end_date, json_data, csv_element):
        """
        Writes the data obtain from the GBD to the CSV element
        :param end_date: End date of the query (usually the time when the query was kicked off)
        :param json_data: The data retrieved from GBD
        :param csv_element: The element to update
        :return: None
        """
        # don't bother with empty data
        if not json_data or KEY_JSON_RESULTS not in json_data or len(json_data[KEY_JSON_RESULTS]) <= 0:
            return
        # explore the results
        for result in json_data[KEY_JSON_RESULTS]:
            # skip over records w/o timestamps (probably not an issue but whatevs)
            if KEY_JSON_PROPERTIES not in result or KEY_JSON_TIMESTAMP not in result[KEY_JSON_PROPERTIES]:
                continue
            timestamp_str = result[KEY_JSON_PROPERTIES][KEY_JSON_TIMESTAMP].encode(JSON_ENCODING)
            timestamp = datetime.strptime(timestamp_str, ISO_FORMAT)

            # get the time delta
            delta = end_date - timestamp

            if delta.days <= 1:
                csv_element.num_gbd_1_day += 1
            elif delta.days <= 3:
                csv_element.num_gbd_3_day += 1
            elif delta.days <= 7:
                csv_element.num_gbd_7_day += 1
            elif delta.days <= 30:
                csv_element.num_gbd_30_day += 1
            else:
                csv_element.num_gbd_60_day += 1

