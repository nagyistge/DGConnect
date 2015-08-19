# -*- coding: utf-8 -*-
__author__ = 'Michael Trotter <michael.trotter@digitalglobe.com>'

from string import Template

import re

import urllib
import urllib2
import cookielib

import json

import logging as log

from CASHTMLParser import CASFormHTMLParser

MONOCLE_3_URL = "https://iipbeta.digitalglobe.com/monocle-3/"
INSIGHT_VECTOR_URL = "https://iipbeta.digitalglobe.com/insight-vector/"
SOURCES_QUERY = Template(INSIGHT_VECTOR_URL + "api/esri/sources?left=$left&right=$right&upper=$upper&lower=$lower")
GEOMETRY_QUERY = Template(INSIGHT_VECTOR_URL +
                          "api/esri/$source/geometries?left=$left&right=$right&upper=$upper&lower=$lower")
TYPES_QUERY = Template(INSIGHT_VECTOR_URL +
                       "api/esri/$source/$geometry/types?left=$left&right=$right&upper=$upper&lower=$lower")
ITEMS_QUERY = Template(INSIGHT_VECTOR_URL +
                       "api/vectors/$source/$geometry?left=$left&right=$right&upper=$upper&lower=$lower")

URL_CAS_LOGIN_SEGMENT = "login"

KEY_HEADER_REFERRER = 'Referer'

FIELD_USERNAME = "username"
FIELD_PASSWORD = "password"
URL_MATCH = re.compile('(.*://[^/]*)')

KEY_JSON_DATA = u'data'
KEY_JSON_NAME = u'name'
KEY_JSON_COUNT = u'count'

ENCODING_UTF8 = 'utf8'
ENCODING_ASCII = 'ascii'
ENCODING_IGNORE = 'ignore'

TIMEOUT_IN_SECONDS = 30

NUM_TIMES_TO_TRY = 10



class InsightCloudSourcesParams:
    """
    Class for holding query params for InsightCloud queries
    """

    def __init__(self, top, right, bottom, left):
        self.top = top
        self.right = right
        self.bottom = bottom
        self.left = left

class InsightCloudGeometriesParams(InsightCloudSourcesParams):
    def __init__(self, sources_params, source):
        InsightCloudSourcesParams.__init__(self, sources_params.top, sources_params.right, sources_params.bottom,
                                           sources_params.left)
        self.sources_params = sources_params
        self.source = source

class InsightCloudTypesParams(InsightCloudGeometriesParams):
    def __init__(self, geometries_params, geometry):
        InsightCloudGeometriesParams.__init__(self, geometries_params.sources_params, geometries_params.source)
        self.geometries_params = geometries_params
        self.geometry = geometry



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
                                              source=urllib.quote(str(geometry_params.source), safe=''))
        return self.make_query(geometries_url)
    
    def query_types(self, types_params):
        types_url = TYPES_QUERY.substitute(upper=str(types_params.top), lower=str(types_params.bottom),
                                           left=str(types_params.left), right=str(types_params.right),
                                           source=urllib.quote(str(types_params.source), safe=''),
                                           geometry=urllib.quote(str(types_params.geometry), safe=''))
        return self.make_query(types_url)

    def make_query(self, url):
        response = None
        for i in range(1, NUM_TIMES_TO_TRY):
            try:
                request = urllib2.Request(url)
                response = self.opener.open(request, timeout=TIMEOUT_IN_SECONDS)
                if self.is_on_login_page(response):
                    response = self.login_to_app(response)
            except Exception, e:
                self.is_login_successful = False
                log.error("Unable to hit url: " + url + " due to: " + str(e) + "; trying " +
                          str(NUM_TIMES_TO_TRY - i)
                          + " more times.")
            if response and self.is_login_successful:
                return self.process_json_data(response.read())
            return None

    def process_json_data(self, response):
        """
        Builds up a dictionary of sources from the response
        :param response: The string response from the server with data for the dictionary
        :return: The dictionary in the form (source => count)
        """
        sources = {}
        json_data = json.loads(response, strict=False)
        if not json_data or KEY_JSON_DATA not in json_data:
            return sources
        for data in json_data[KEY_JSON_DATA]:
            if KEY_JSON_NAME not in data or KEY_JSON_COUNT not in data:
                continue
            name = data[KEY_JSON_NAME].encode(ENCODING_ASCII, ENCODING_IGNORE)
            count = data[KEY_JSON_COUNT]
            sources[name] = count
        return sources