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
SOURCES_QUERY = Template(INSIGHT_VECTOR_URL + "api/vectors/sources?left=$left&right=$right&upper=$upper&lower=$lower")

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



class InsightCloudParams:
    """
    Class for holding query params for InsightCloud queries
    """

    def __init__(self, top, right, bottom, left):
        self.top = top
        self.right = right
        self.bottom = bottom
        self.left = left

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

    def query_sources(self, order_params):
        """
        Queries OSM data for stats and updates the CSV element for output
        :param order_params: InsightCloud params to query for
        :param csv_element: The CSV row to update
        :return: None
        """
        sources_url = SOURCES_QUERY.substitute(upper=str(order_params.top), right=str(order_params.right),
                                               lower=str(order_params.bottom), left=str(order_params.left))
        for i in range(1, NUM_TIMES_TO_TRY):
            response = None
            try:
                request = urllib2.Request(sources_url)
                response = self.opener.open(request, timeout=TIMEOUT_IN_SECONDS)
                if self.is_on_login_page(response):
                    response = self.login_to_app(response)
            except Exception, e:
                self.is_login_successful = False
                log.error("Unable to hit the osm end point due to: " + str(e) + "; trying " + str(NUM_TIMES_TO_TRY - i)
                          + " more times.")
            if response and self.is_login_successful:
                return self.process_osm_data(response.read())
        return None

    def process_osm_data(self, response):
        """
        Updates the CSV row with the OSM stats
        :param response: The string response from the server with data for the csv row
        :param csv_element: The csv row to update
        :return: None
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

