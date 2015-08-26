# -*- coding: utf-8 -*-
from PyQt4.QtCore import QVariant

__author__ = 'Michael Trotter <michael.trotter@digitalglobe.com>'

from string import Template

import re

import urllib
import urllib2
import cookielib

import json

import logging as log

from CASHTMLParser import CASFormHTMLParser

from qgis.core import QgsFeature, QgsGeometry, QgsPoint, QgsFields, QgsField

MONOCLE_3_URL = "https://iipbeta.digitalglobe.com/monocle-3/"
INSIGHT_VECTOR_URL = "https://iipbeta.digitalglobe.com/insight-vector/"
SOURCES_QUERY = Template(INSIGHT_VECTOR_URL + "api/esri/sources?left=$left&right=$right&upper=$upper&lower=$lower")
GEOMETRY_QUERY = Template(INSIGHT_VECTOR_URL +
                          "api/esri/$source/geometries?left=$left&right=$right&upper=$upper&lower=$lower")
TYPES_QUERY = Template(INSIGHT_VECTOR_URL +
                       "api/esri/$source/$geometry/types?left=$left&right=$right&upper=$upper&lower=$lower")
ITEMS_GET_PAGING_ID = Template(INSIGHT_VECTOR_URL +
                               "api/vectors/$source/$type_name/paging?left=$left&right=$right&upper=$upper&lower=$lower"
                               "&ttl=5m&count=500")
ITEMS_POST_PAGING_ID = INSIGHT_VECTOR_URL + "api/vectors/paging"

URL_CAS_LOGIN_SEGMENT = "login"

KEY_HEADER_REFERRER = 'Referer'
KEY_HEADER_PAGING_ID = 'Vector-Paging-Id'

FIELD_USERNAME = "username"
FIELD_PASSWORD = "password"
URL_MATCH = re.compile('(.*://[^/]*)')

KEY_JSON_DATA = u'data'
KEY_JSON_NAME = u'name'
KEY_JSON_COUNT = u'count'

KEY_JSON_PAGING_ID = u'pagingId'

KEY_JSON_GEOMETRY = u'geometry'
KEY_JSON_GEOMETRY_COORDINATES = u'coordinates'
KEY_JSON_GEOMETRY_TYPE = u'type'

KEY_JSON_PROPERTIES = u'properties'
KEY_JSON_PROPERTIES_LIST = [u'name', u'itemType', u'source']

KEY_JSON_ATTRIBUTES = u'attributes'

KEY_JSON_PREFIX_MAIN_PROPERTIES = u'vector_'
KEY_JSON_PREFIX_ATTRIBUTES = u'item_'

ENCODING_UTF8 = 'utf8'
ENCODING_ASCII = 'ascii'
ENCODING_IGNORE = 'ignore'

KEY_POINT = "Point"
KEY_POLYGON = "Polygon"
KEY_LINE = "Line"

TIMEOUT_IN_SECONDS = 30

NUM_TIMES_TO_TRY = 3

SLASH = '/'

ITEMS_TO_RETURN = 500

class InsightCloudSourcesParams:
    """
    Class for holding query params for InsightCloud queries
    """

    def __init__(self, top, right, bottom, left, query=None):
        self.top = top
        self.right = right
        self.bottom = bottom
        self.left = left
        self.query = query

class InsightCloudGeometriesParams(InsightCloudSourcesParams):
    def __init__(self, sources_params, source):
        InsightCloudSourcesParams.__init__(self, sources_params.top, sources_params.right, sources_params.bottom,
                                           sources_params.left, sources_params.query)
        self.sources_params = sources_params
        self.source = source

class InsightCloudTypesParams(InsightCloudGeometriesParams):
    def __init__(self, geometries_params, geometry):
        InsightCloudGeometriesParams.__init__(self, geometries_params.sources_params, geometries_params.source)
        self.geometries_params = geometries_params
        self.geometry = geometry

class InsightCloudItemsParams(InsightCloudSourcesParams):
    def __init__(self, sources_params, source, type_name):
        InsightCloudSourcesParams.__init__(self, sources_params.top, sources_params.right, sources_params.bottom,
                                           sources_params.left, sources_params.query)
        self.source = source
        self.type_name = type_name

class InsightCloudQuery:
    """
    Class for handling queries to InsightCloud vector data
    """

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.CookieJar()))
        self.is_login_successful = True

    @classmethod
    def is_on_login_page(cls, response):
        """
        Check to see if the current response is for the CAS log in page
        :param response: The HTTP response received
        :return: True if the responses' url points to the log in page; else False
        """
        return response and URL_CAS_LOGIN_SEGMENT in response.geturl()

    @classmethod
    def build_form_info(cls, response_url, form_data):
        """
        Parses the CAS page and pulls out the relevant information
        :param response_url: The url of the current page
        :param form_data: The HTML code of the page as a str
        :return: A tuple containing ( the url to post the CAS info to , a map of data to post to CAS )
        """
        parser = CASFormHTMLParser()
        parser.feed(form_data)
        action = parser.action
        match = re.match(URL_MATCH, response_url)
        if match:
            return match.group(0) + action, parser.hidden_data
        return None

    def post_login_credentials_to_app(self, url_data, redirect_header):
        """
        Posts the data to CAS as part of the log in sequence
        :param url_data: Additional CAS form data to post
        :param redirect_header: url to redirect from CAS
        :return: A new HTTP response as a result of the POST
        """
        # post the credentials
        response = None
        try:
            unencoded_data = dict({FIELD_USERNAME : self.username, FIELD_PASSWORD : self.password}.items() + url_data[1].items())
            data = urllib.urlencode(unencoded_data)
            request = urllib2.Request(url=url_data[0], data=data, headers={KEY_HEADER_REFERRER: redirect_header})
            response = self.opener.open(request, data, timeout=TIMEOUT_IN_SECONDS)
        except Exception, e:
            self.is_login_successful = False
            log.error("Unable to post login credentials due to: " + str(e))
        return response

    def login_to_app(self, response):
        """
        Attempts to log into the InsightCloud platform based on the current HTTP response
        :param response: The current HTTP response
        :return: An update HTTP response from the CAS log in
        """
        url_data = self.build_form_info(response.geturl(), response.read())
        response = self.post_login_credentials_to_app(url_data, response.geturl())
        if isinstance(response, basestring):
            self.is_login_successful = False
            log.error("Error response received: " + str(response))
        elif URL_CAS_LOGIN_SEGMENT in response.geturl():
            self.is_login_successful = False
            log.error("Unable to login with credentials: (username: %s, password %s)" % self.username, self.password)
        return response

    def log_into_monocle_3(self):
        """
        Attempts to log into Monocle-3; used to validate credentials and intialize the log-in so that future
        communication doesn't need to log on
        :return: The HTML page as a str if successful; None otherwise
        """
        response = None
        try:
            request = urllib2.Request(MONOCLE_3_URL)
            response = self.opener.open(request, timeout=TIMEOUT_IN_SECONDS)
            if self.is_on_login_page(response):
                response = self.login_to_app(response)
        except Exception, e:
            self.is_login_successful = False
            log.error("Unable to log into Monocle-3 due to: " + str(e))
        if response and self.is_login_successful:
            return response.read()
        return None

    def prep_param(self, param):
        new_param = param.replace(SLASH, '')
        return urllib.quote(new_param, safe='')

    def query_sources(self, source_params):
        """
        Queries sources and returns a dictionary of (source => count)
        :param source_params: The params for the source query
        :return: A dictionary of (source => count) if there are results
        """
        sources_url = SOURCES_QUERY.substitute(upper=str(source_params.top), right=str(source_params.right),
                                               lower=str(source_params.bottom), left=str(source_params.left))
        return self.make_query(sources_url)

    def query_geometries(self, geometry_params):
        geometries_url = GEOMETRY_QUERY.substitute(upper=str(geometry_params.top), lower=str(geometry_params.bottom),
                                              left=str(geometry_params.left), right=str(geometry_params.right),
                                              source=self.prep_param(str(geometry_params.source)))
        return self.make_query(geometries_url)
    
    def query_types(self, types_params):
        types_url = TYPES_QUERY.substitute(upper=str(types_params.top), lower=str(types_params.bottom),
                                           left=str(types_params.left), right=str(types_params.right),
                                           source=self.prep_param(str(types_params.source)),
                                           geometry=self.prep_param((str(types_params.geometry))))
        return self.make_query(types_url)

    def query_items(self, items_params, json_export=False):
        paging_url = ITEMS_GET_PAGING_ID.substitute(upper=str(items_params.top), lower=str(items_params.bottom),
                                                    left=str(items_params.left), right=str(items_params.right),
                                                    source=urllib.quote(str(items_params.source), safe=''),
                                                    type_name=self.prep_param(
                                                        str(items_params.type_name
                                                            .encode(ENCODING_UTF8, ENCODING_IGNORE))))
        return self.make_paging_query(paging_url, json_export)

    def make_query(self, url):
        response = None
        for i in range(0, NUM_TIMES_TO_TRY):
            try:
                request = urllib2.Request(url)
                response = self.opener.open(request, timeout=TIMEOUT_IN_SECONDS)
                if self.is_on_login_page(response):
                    response = self.login_to_app(response)
            except Exception, e:
                self.is_login_successful = False
                log.error("Unable to hit url: " + url + " due to: " + str(e) + "; trying " +
                          str(NUM_TIMES_TO_TRY - i - 1)
                          + " more times.")
            if response and self.is_login_successful:
                return self.process_json_data(response.read())
        return None

    def make_paging_query(self, url, json_export):
        response = None
        for i in range(0, NUM_TIMES_TO_TRY):
            try:
                request = urllib2.Request(url)
                response = self.opener.open(request, timeout=TIMEOUT_IN_SECONDS)
                if self.is_on_login_page(response):
                    response = self.login_to_app(response)
            except Exception, e:
                self.is_login_successful = False
                log.error("Unable to run get on url: " + url + " due to: " + str(e) + "; trying "
                          + str(NUM_TIMES_TO_TRY - i - 1) +
                          " times")
            if response and self.is_login_successful:
                paging_id = self.process_paging_request(response.read())
                if paging_id:
                    return self.query_for_pages(paging_id, json_export)
                return None
        return None

    def query_for_pages(self, paging_id, json_export):
        response = None
        total_data = {
            KEY_POINT: [],
            KEY_POLYGON: [],
            KEY_LINE: [],
        }
        continue_querying = True
        while continue_querying:
            data = {'pagingId': paging_id}
            log.info("Using paging id: " + str(paging_id))
            for i in range(0, NUM_TIMES_TO_TRY):
                try:
                    request = urllib2.Request(ITEMS_POST_PAGING_ID, urllib.urlencode(data))
                    response = self.opener.open(request)
                    if self.is_on_login_page(response):
                        response = self.login_to_app(response)
                except Exception, e:
                    self.is_login_successful = False
                    log.error("Unable to post to url: " + ITEMS_POST_PAGING_ID + " due to: " + str(e) + "; trying " +
                              str(NUM_TIMES_TO_TRY - i - 1) + " times")
                    if (NUM_TIMES_TO_TRY - i - 1) <= 0:
                        return None
                if response and self.is_login_successful:
                    paging_id = response.info().getheader(KEY_HEADER_PAGING_ID)
                    new_data = self.process_paging_json_data(response.read(), json_export)
                    total_data[KEY_LINE] += new_data[KEY_LINE]
                    total_data[KEY_POLYGON] += new_data[KEY_POLYGON]
                    total_data[KEY_POINT] += new_data[KEY_POINT]
                    continue_querying = len(new_data) >= ITEMS_TO_RETURN
                    break
            if not self.is_login_successful:
                continue_querying = False
        return total_data

    def process_json_data(self, response):
        """
        Builds up a dictionary of sources from the response
        :param response: The string response from the server with data for the dictionary
        :return: The dictionary in the form (source => count)
        """
        processed_data = {}
        json_data = json.loads(response, strict=False)
        if not json_data or KEY_JSON_DATA not in json_data:
            return processed_data
        for data in json_data[KEY_JSON_DATA]:
            if KEY_JSON_NAME not in data or KEY_JSON_COUNT not in data:
                continue
            name = data[KEY_JSON_NAME]  # .encode(ENCODING_ASCII, ENCODING_IGNORE)
            count = data[KEY_JSON_COUNT]
            processed_data[name] = count
        return processed_data

    def process_paging_request(self, response):
        json_data = json.loads(response, strict=False)
        if not json_data or KEY_JSON_PAGING_ID not in json_data:
            return None
        return json_data[KEY_JSON_PAGING_ID]

    def process_paging_json_data(self, response, json_export):
        new_data = {
            KEY_POINT: [],
            KEY_LINE: [],
            KEY_POLYGON: [],
        }
        json_data = json.loads(response, strict=False)
        for vector_item in json_data:
            new_item = None
            if json_export:
                new_item = self.build_geojson_entry(vector_item)
            else:
                new_item = self.build_qgis_feature(vector_item)
            if new_item.geometry_type == u'Point' or new_item.geometry_type == u'MultiPoint':
                if json_export:
                    new_data[KEY_POINT].append(json.dumps(new_item.__dict__))
                else:
                    new_data[KEY_POINT].append(new_item)
            elif new_item.geometry_type == u'LineString' or new_item.geometry_type == u'MultiLineString':
                if json_export:
                    new_data[KEY_LINE].append(json.dumps(new_item.__dict__))
                else:
                    new_data[KEY_LINE].append(new_item)
            else:
                if json_export:
                    new_data[KEY_POLYGON].append(json.dumps(new_item.__dict__))
                else:
                    new_data[KEY_POLYGON].append(new_item)
        return new_data

    def build_qgis_feature(self, vector_item):
        feature = UVIFeature()
        geometry = vector_item[KEY_JSON_GEOMETRY]
        coordinates = geometry[KEY_JSON_GEOMETRY_COORDINATES]
        geometry_type = geometry[KEY_JSON_GEOMETRY_TYPE]
        if geometry_type == u'Point':
            feature.setGeometry(QgsGeometry.fromPoint(self.get_point_from_json(coordinates)))
        elif geometry_type == u'LineString':
            feature.setGeometry(QgsGeometry.fromPolyline(self.get_linestring_from_json(coordinates)))
        elif geometry_type == u'MultiPoint':
            feature.setGeometry(QgsGeometry.fromMultiPoint(self.get_linestring_from_json(coordinates)))
        elif geometry_type == u'Polygon':
            feature.setGeometry(QgsGeometry.fromPolygon(self.get_polygon_from_json(coordinates)))
        elif geometry_type == u'MultiLineString':
            feature.setGeometry(QgsGeometry.fromMultiPolyline(self.get_polygon_from_json(coordinates)))
        elif geometry_type == u'MultiPolygon':
            feature.setGeometry(QgsGeometry.fromMultiPolygon(self.get_multipolygon_from_json(coordinates)))
        else:
            log.error(u"Encountered odd geometry type: " + geometry_type)
        feature.geometry_type = geometry_type
        attributes = self.get_attributes_from_json(vector_item[KEY_JSON_PROPERTIES])
        fields = QgsFields()
        values = []
        for key, value in attributes.iteritems():
            type_value = None
            if key.endswith(u'int'):
                type_value = QVariant.Int
            elif key.endswith(u'dbl'):
                type_value = QVariant.Double
            else:
                type_value = QVariant.String
            fields.append(QgsField(key, type_value))
            values.append(value)
        feature.setFields(fields)
        feature.setAttributes(values)
        return feature

    def build_geojson_entry(self, vector_item):
        entry = GeoJSONEntry()
        geometry = vector_item[KEY_JSON_GEOMETRY]
        geometry_type = geometry[KEY_JSON_GEOMETRY_TYPE]
        entry.geometry = geometry
        entry.geometry_type = geometry_type
        entry.properties = self.clean_properties_from_json(vector_item[KEY_JSON_PROPERTIES])
        return entry

    def get_point_from_json(self, coordinates):
        return QgsPoint(coordinates[1], coordinates[0])

    def get_linestring_from_json(self, coordinates):
        points = []
        for coordinate in coordinates:
            points.append(self.get_point_from_json(coordinate))
        return points

    def get_polygon_from_json(self, coordinates):
        points = []
        for coordinate in coordinates:
            points.append(self.get_linestring_from_json(coordinate))
        return points

    def get_multipolygon_from_json(self, coordinates):
        points = []
        for coordinate in coordinates:
            points.append(self.get_polygon_from_json(coordinate))
        return points

    def get_attributes_from_json(self, properties):
        attributes = {}
        for main_attribute in KEY_JSON_PROPERTIES_LIST:
            if main_attribute in properties:
                attributes[KEY_JSON_PREFIX_MAIN_PROPERTIES + main_attribute] = properties[main_attribute]
        if KEY_JSON_ATTRIBUTES in properties:
            for attribute in properties[KEY_JSON_ATTRIBUTES]:
                attributes[KEY_JSON_PREFIX_ATTRIBUTES + attribute] = properties[KEY_JSON_ATTRIBUTES][attribute]
        return attributes

    def clean_properties_from_json(self, props):
        new_properties = {}
        for prop in KEY_JSON_PROPERTIES_LIST:
            if prop in props:
                new_properties[prop] = props[prop]
        if KEY_JSON_ATTRIBUTES in props:
            new_properties[KEY_JSON_ATTRIBUTES] = props[KEY_JSON_ATTRIBUTES]
        return new_properties

class UVIFeature(QgsFeature):
    def __init__(self, *__args):
        QgsFeature.__init__(self, *__args)
        self.geometry_type = None

class GeoJSONEntry:
    def __init__(self):
        self.geometry_type = None
        self.geometry = None
        self.properties = None
        self.type = "Feature"