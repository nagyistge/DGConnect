# -*- coding: utf-8 -*-
from qgis._core import QgsMessageLog

__author__ = 'Michael Trotter <michael.trotter@digitalglobe.com>'

from string import Template

import re

import urllib
import urllib2
import cookielib

import json

from InfoCubeCASHTMLParser import CASFormHTMLParser
from InfoCubeOAuth2Query import OAuth2Query

INSIGHT_VECTOR_URL = "https://iipbeta.digitalglobe.com/insight-vector/api/"
VECTOR_TYPE_QUERY = Template(INSIGHT_VECTOR_URL + "aggregation?aggs=terms:ingest_source&left=$left&right=$right&upper=$upper&lower=$lower")

HEADER_CONTENT_TYPE = 'Content-Type'
CONTENT_TYPE_JSON = 'application/json'

FIELD_USERNAME = "username"
FIELD_PASSWORD = "password"
URL_MATCH = re.compile('(.*://[^/]*)')

JSON_VECTOR_AGG_KEY = u"aggregations"
JSON_VECTOR_TERMS_KEY = u"terms"
JSON_VECTOR_TERM_KEY = u"term"
JSON_VECTOR_COUNT_KEY = u"count"

TIMEOUT_IN_SECONDS = 30

NUM_TIMES_TO_TRY = 10

TAG_NAME = 'InfoCube (Vector)'

class InsightCloudParams:
    """
    Class for holding query params for InsightCloud queries
    """

    def __init__(self, top, right, bottom, left, time_begin=None, time_end=None):
        self.top = top
        self.right = right
        self.bottom = bottom
        self.left = left
        self.time_begin = time_begin
        self.time_end = time_end

class InsightCloudQuery(OAuth2Query):
    """
    Class for handling queries to InsightCloud vector data
    """
    def __init__(self, username, password, client_id, client_secret, grant_type='password'):
        super(InsightCloudQuery, self).__init__(username, password, client_id, client_secret, grant_type)

    def query_vector(self, order_params, csv_element):
        """
        Queries vector data for stats and updates the CSV element for output
        :param order_params: InsightCloud params to query for
        :param csv_element: The CSV row to update
        :return: None
        """
        result = self.get_vector_result(order_params)        
        if result:
            self.process_vector_data(result, csv_element)

    def get_vector_result(self, order_params):
        """
        Queries vector data for stats and updates the CSV element for output
        :param order_params: InsightCloud params to query for
        :param csv_element: The CSV row to update
        :return: None
        """
        result_data = None
        vector_url = VECTOR_TYPE_QUERY.substitute(upper=str(order_params.top), right=str(order_params.right),
                                               lower=str(order_params.bottom), left=str(order_params.left))        
        headers = self.headers.copy()
        headers[HEADER_CONTENT_TYPE] = CONTENT_TYPE_JSON

        for i in range(0, NUM_TIMES_TO_TRY):
            response = None
            try:
                request = urllib2.Request(vector_url, None, headers)
                response = self.opener.open(request)
                response_data = response.read()        
                result_data = json.loads(response_data, strict=False)
                self.is_login_successful = True

            except Exception, e:
                self.is_login_successful = False
                QgsMessageLog.instance().logMessage("Unable to hit the vector end point due to: " + str(e) + "; trying "
                          + str(NUM_TIMES_TO_TRY - i - 1)
                          + " more times.", TAG_NAME, level=QgsMessageLog.CRITICAL)

            if response and self.is_login_successful:
                return result_data

        return None

    def process_vector_data(self, result, csv_element):
        """
        Updates the CSV row with the OSM stats
        :param response: The string response from the server with data for the csv row
        :param csv_element: The csv row to update
        :return: None
        """
        vector_data = self.get_vector_data(result)
        for term in vector_data:
            count = vector_data[term]
            csv_element.vector_dict[term] = count

    def get_vector_data(self, json_data):
        """
        Updates the CSV row with the OSM stats
        :param response: The string response from the server with data for the csv row
        :param csv_element: The csv row to update
        :return: vector_data
        """
        vector_data = {}        
        # skip over empty fields
        if not json_data or  not JSON_VECTOR_AGG_KEY in json_data:
            return
        aggregations = json_data[JSON_VECTOR_AGG_KEY]
        if aggregations:
            terms = aggregations[0][JSON_VECTOR_TERMS_KEY]
            for term in terms:
                key = term[JSON_VECTOR_TERM_KEY]
                count = term[JSON_VECTOR_COUNT_KEY]
                vector_data[key] = count
        return vector_data
