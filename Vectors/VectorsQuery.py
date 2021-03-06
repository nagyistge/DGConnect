# -*- coding: utf-8 -*-
from PyQt4.QtCore import QVariant

__author__ = 'Michael Trotter <michael.trotter@digitalglobe.com>'

from string import Template

import re

import urllib
import urllib2
import cookielib

import json

from ..Common.OAuth2Query import OAuth2Query

from qgis.core import QgsFeature, QgsGeometry, QgsPoint, QgsFields, QgsField, QgsMessageLog

INSIGHT_VECTOR_URL = "https://vector.geobigdata.io/insight-vector/"
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

HEADER_CONTENT_TYPE = 'Content-Type'
CONTENT_TYPE_JSON = 'application/json'

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
KEY_MULTIPOINT = "MultiPoint"
KEY_POLYGON = "Polygon"
KEY_LINE = "Line"

TIMEOUT_IN_SECONDS = 30

NUM_TIMES_TO_TRY = 3

SLASH = '/'

ITEMS_TO_RETURN = 500

TAG_NAME = 'GBDX'

class VectorsSourcesParams:
    """
    Class for holding query params for source queries
    """

    def __init__(self, top, right, bottom, left, query=None):
        self.top = top
        self.right = right
        self.bottom = bottom
        self.left = left
        self.query = query

class VectorsGeometriesParams(VectorsSourcesParams):
    """
    Class for holding query params for geometry queries
    """

    def __init__(self, sources_params, source):
        VectorsSourcesParams.__init__(self, sources_params.top, sources_params.right, sources_params.bottom,
                                           sources_params.left, sources_params.query)
        self.sources_params = sources_params
        self.source = source

class VectorsTypesParams(VectorsGeometriesParams):
    """
    Class for holding query params for types queries
    """

    def __init__(self, geometries_params, geometry):
        VectorsGeometriesParams.__init__(self, geometries_params.sources_params, geometries_params.source)
        self.geometries_params = geometries_params
        self.geometry = geometry

class VectorsItemsParams(VectorsSourcesParams):
    """
    Class for holding query params for items queries
    """

    def __init__(self, sources_params, source, type_name):
        VectorsSourcesParams.__init__(self, sources_params.top, sources_params.right, sources_params.bottom,
                                           sources_params.left, sources_params.query)
        self.source = source
        self.type_name = type_name

class VectorQuery(OAuth2Query):
    """
    Class for handling queries to vector data
    """

    def __init__(self, username, password, api_key, grant_type='password'):
        super(VectorQuery, self).__init__(username, password, api_key, grant_type)

    def prep_param(self, param):
        """
        Strips slashes from the params used for query
        :param param: The parameter
        :return: The stripped parameter
        """
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
        """
        Queries geometries and returns a dictionary of (geometry => count)
        :param geometry_params: The params for the geometry query
        :return: A dictionary of (geometry => count) if there are results
        """
        geometries_url = GEOMETRY_QUERY.substitute(upper=str(geometry_params.top), lower=str(geometry_params.bottom),
                                              left=str(geometry_params.left), right=str(geometry_params.right),
                                              source=self.prep_param(str(geometry_params.source)))
        return self.make_query(geometries_url)
    
    def query_types(self, types_params):
        """
        Queries types and returns a dictionary of (types => count)
        :param types_params: The params for the types query
        :return: A dictionary of (type => count) if there are results
        """
        types_url = TYPES_QUERY.substitute(upper=str(types_params.top), lower=str(types_params.bottom),
                                           left=str(types_params.left), right=str(types_params.right),
                                           source=self.prep_param(str(types_params.source)),
                                           geometry=self.prep_param((str(types_params.geometry))))
        return self.make_query(types_url)

    def query_items(self, items_params, json_export=False):
        """
        Queries items and returns a list of items
        :param items_params: The params for the items query
        :param json_export: Boolean if this is exporting to JSON or not
        :return: A list of items or None if the search is unsuccessful
        """
        paging_url = ITEMS_GET_PAGING_ID.substitute(upper=str(items_params.top), lower=str(items_params.bottom),
                                                    left=str(items_params.left), right=str(items_params.right),
                                                    source=urllib.quote(str(items_params.source), safe=''),
                                                    type_name=self.prep_param(
                                                        str(items_params.type_name
                                                            .encode(ENCODING_UTF8, ENCODING_IGNORE))))
        return self.make_paging_query(paging_url, json_export)

    def make_query(self, url):
        """
        Runs a source/geometry/type query and returns the results
        :param url: The url to query
        :return: A dictionary of name => count if successful; None if not
        """
        response = None
        headers = self.get_headers().copy()
        headers[HEADER_CONTENT_TYPE] = CONTENT_TYPE_JSON
                
        for i in range(0, NUM_TIMES_TO_TRY):
            try:
                request = urllib2.Request(url=url, headers=headers)
                response = self.get_opener().open(request, timeout=TIMEOUT_IN_SECONDS)
                self.is_login_successful = True
            except Exception, e:
                self.is_login_successful = False
                QgsMessageLog.instance().logMessage("Unable to hit url: " + url + " due to: " + str(e) + "; trying " +
                                                    str(NUM_TIMES_TO_TRY - i - 1) + " more times.", TAG_NAME,
                                                    level=QgsMessageLog.CRITICAL)
            
            if response and self.is_login_successful:
                return self.process_json_data(response.read())
        return None

    def make_paging_query(self, url, json_export):
        """
        Runs an item query and returns the results
        :param url: The url to query
        :param json_export: True if exporting; False if rendering
        :return: A list of items if successful; None if not
        """
        response = None
        headers = self.get_headers().copy()
        headers[HEADER_CONTENT_TYPE] = CONTENT_TYPE_JSON
        for i in range(0, NUM_TIMES_TO_TRY):
            try:
                request = urllib2.Request(url=url, headers=headers)
                response = self.get_opener().open(request, timeout=TIMEOUT_IN_SECONDS)
                self.is_login_successful = True
            except Exception, e:
                self.is_login_successful = False
                QgsMessageLog.instance().logMessage("Unable to run get on url: " + url + " due to: " + str(e)
                                                    + "; trying " + str(NUM_TIMES_TO_TRY - i - 1) + " times",
                                                    TAG_NAME, level=QgsMessageLog.CRITICAL)
            if response and self.is_login_successful:
                paging_id = self.process_paging_request(response.read())
                if paging_id:
                    return self.query_for_pages(paging_id, json_export)
                return None
        raise Exception("unable to make paging query on url:" + url)

    def query_for_pages(self, paging_id, json_export):
        """
        Runs paging queries until there is nothing left to find
        :param paging_id: The pagingId for the intial page
        :param json_export: True if exporting to JSON; False if rendering
        :return: A list of returned items if successful; None if not
        """
        response = None
        headers = self.get_headers().copy()
        total_data = {
            KEY_POINT: [],
            KEY_POLYGON: [],
            KEY_LINE: [],
            KEY_MULTIPOINT: [],
        }
        continue_querying = True
        while continue_querying:
            data = {'pagingId': paging_id}
            for i in range(0, NUM_TIMES_TO_TRY):
                try:
                    request = urllib2.Request(ITEMS_POST_PAGING_ID, urllib.urlencode(data), headers)
                    response = self.get_opener().open(request)
                    self.is_login_successful = True
                    response_body = response.read()

                    paging_id = self.process_paging_request(response_body)
                    new_data = self.process_paging_json_data(response_body, json_export)
                    total_data[KEY_LINE] += new_data[KEY_LINE]
                    total_data[KEY_POLYGON] += new_data[KEY_POLYGON]
                    total_data[KEY_POINT] += new_data[KEY_POINT]

                    continue_querying = len(new_data) >= ITEMS_TO_RETURN
                    break;

                except Exception, e:
                    self.is_login_successful = False
                    QgsMessageLog.instance().logMessage("Unable to post to url: " + ITEMS_POST_PAGING_ID +
                                                        " due to: " + str(e) + "; trying "
                                                        + str(NUM_TIMES_TO_TRY - i - 1) + " times", TAG_NAME,
                                                        level=QgsMessageLog.CRITICAL)
                    if (NUM_TIMES_TO_TRY - i - 1) <= 0:
                        raise e

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
        """
        Extracts the initial pagingId from the response
        :param response: The response to extract
        :return: The paging id
        """
        json_data = json.loads(response, strict=False)
        if not json_data or KEY_JSON_PAGING_ID not in json_data:
            return None
        return json_data[KEY_JSON_PAGING_ID]

    def process_paging_json_data(self, response, json_export):
        """
        Extracts the json information from the response
        :param response: The response from the server
        :param json_export: True if exporting to JSON; False if rendering
        """
        new_data = {
            KEY_POINT: [],
            KEY_MULTIPOINT: [],
            KEY_LINE: [],
            KEY_POLYGON: [],
        }
        json_data = json.loads(response, strict=False)
        for vector_item in json_data[KEY_JSON_DATA]:
            new_item = None
            if json_export:
                new_item = self.build_geojson_entry(vector_item)
            else:
                new_item = self.build_qgis_feature(vector_item)
            if new_item.geometry_type == u'Point':
                if json_export:
                    new_data[KEY_POINT].append(json.dumps(new_item.__dict__))
                else:
                    new_data[KEY_POINT].append(new_item)
            elif new_item.geometry_type == u'MultiPoint':
                if json_export:
                    new_data[KEY_MULTIPOINT].append(json.dumps(new_item.__dict__))
                else:
                    new_data[KEY_MULTIPOINT].append(new_item)
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
        """
        Constructs a QGIS feature for rendering
        :param vector_item: The item returned
        :return a VectorFeature that can be rendered by QGIS
        """

        feature = VectorFeature()
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
            QgsMessageLog.instance().logMessage(u"Encountered odd geometry type: " + geometry_type, TAG_NAME,
                                                level=QgsMessageLog.CRITICAL)
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
        """
        Constructs a GeoJSON object from the vector item
        :param vector_item: The vector item returned by the REST call
        :return: A GeoJSON holding the vector data
        """
        entry = GeoJSONEntry()
        geometry = vector_item[KEY_JSON_GEOMETRY]
        geometry_type = geometry[KEY_JSON_GEOMETRY_TYPE]
        entry.geometry = geometry
        entry.geometry_type = geometry_type
        entry.properties = self.clean_properties_from_json(vector_item[KEY_JSON_PROPERTIES])
        return entry

    def get_point_from_json(self, coordinates):
        """
        Converts a coordinates list to a QgsPoint
        :param coordinates: The coordinates list
        :return: QgsPoint for that pair of coordinates
        """
        return QgsPoint(coordinates[1], coordinates[0])

    def get_linestring_from_json(self, coordinates):
        """
        Converts a line string list to a list of QgsPoints
        :param coordinates: The coordinates from the GeoJSON
        :return: List of QgsPoints
        """
        points = []
        for coordinate in coordinates:
            points.append(self.get_point_from_json(coordinate))
        return points

    def get_polygon_from_json(self, coordinates):
        """
        Converts a polygon list of coordinates to a list of list of QgsPoints
        :param coordinates: The coordinates from the GeoJSON
        :return: List of List of QgsPoints
        """
        points = []
        for coordinate in coordinates:
            points.append(self.get_linestring_from_json(coordinate))
        return points

    def get_multipolygon_from_json(self, coordinates):
        """
        Converts of a list of polygon coordinates to a list of list of list of QgsPoints
        :param coordinates: The coordinates from the GeoJSON
        :return: List of List of List of QgsPoints
        """
        points = []
        for coordinate in coordinates:
            points.append(self.get_polygon_from_json(coordinate))
        return points

    def get_attributes_from_json(self, properties):
        """
        Converts to properties from the GeoJSON to match the esri format
        Brings up attributes one level and prefixes the attributes and properties appropriately
        :param properties: The properties map
        :return: A map containing the modified properties
        """
        attributes = {}
        for main_attribute in KEY_JSON_PROPERTIES_LIST:
            if main_attribute in properties:
                attributes[KEY_JSON_PREFIX_MAIN_PROPERTIES + main_attribute] = properties[main_attribute]
        if KEY_JSON_ATTRIBUTES in properties:
            for attribute in properties[KEY_JSON_ATTRIBUTES]:
                attributes[KEY_JSON_PREFIX_ATTRIBUTES + attribute] = properties[KEY_JSON_ATTRIBUTES][attribute]
        return attributes

    def clean_properties_from_json(self, props):
        """
        Removes extra info from the GeoJSON for rendering
        :param props: The properties map
        :return: The cleaned up map
        """
        new_properties = {}
        for prop in KEY_JSON_PROPERTIES_LIST:
            if prop in props:
                new_properties[prop] = props[prop]
        if KEY_JSON_ATTRIBUTES in props:
            for key, value in props[KEY_JSON_ATTRIBUTES].iteritems():
                new_properties[key] = value
        return new_properties

class VectorFeature(QgsFeature):
    """
    QgsFeature with special geometry_type used for filtering
    """
    def __init__(self, *__args):
        QgsFeature.__init__(self, *__args)
        self.geometry_type = None

class GeoJSONEntry:
    """
    Object representation of the GeoJSON used for export
    """
    def __init__(self):
        self.geometry_type = None
        self.geometry = None
        self.properties = None
        self.type = "Feature"
