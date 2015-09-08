# -*- coding: utf-8 -*-
__author__ = 'Michael Trotter <michael.trotter@digitalglobe.com>'

from string import Template

import re

import urllib
import urllib2
import cookielib

import json

import logging as log

from InfoCubeCASHTMLParser import CASFormHTMLParser

MONOCLE_3_URL = "https://iipbeta.digitalglobe.com/monocle-3/"
VECTOR_TYPE_QUERY = Template(MONOCLE_3_URL + "app/broker/vector/api/vectors/OSM/types?left=$left&right=$right&upper=$upper&lower=$lower")
TWITTER_QUERY = Template(MONOCLE_3_URL + "app/broker/sma/sma/twitter/tweets?bbox=$left,$lower,$right,$upper")
RSS_QUERY = Template(MONOCLE_3_URL + "app/broker/sma/sma/rss/sentences?bbox=$left,$lower,$right,$upper")

URL_CAS_LOGIN_SEGMENT = "login"

KEY_HEADER_REFERRER = 'Referer'

FIELD_USERNAME = "username"
FIELD_PASSWORD = "password"
URL_MATCH = re.compile('(.*://[^/]*)')

JSON_OSM_DATA_KEY = u'data'
JSON_OSM_COUNT_KEY = u'count'
JSON_SMA_HITS_KEY = u'hits'
JSON_SMA_TOTAL_KEY = u'total'

TIMEOUT_IN_SECONDS = 30

NUM_TIMES_TO_TRY = 10

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
        return response is not None and URL_CAS_LOGIN_SEGMENT in response.geturl()

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

    def query_osm(self, order_params, csv_element):
        """
        Queries OSM data for stats and updates the CSV element for output
        :param order_params: InsightCloud params to query for
        :param csv_element: The CSV row to update
        :return: None
        """
        osm_url = VECTOR_TYPE_QUERY.substitute(upper=str(order_params.top), right=str(order_params.right),
                                               lower=str(order_params.bottom), left=str(order_params.left))
        for i in range(0, NUM_TIMES_TO_TRY):
            response = None
            try:
                request = urllib2.Request(osm_url)
                response = self.opener.open(request, timeout=TIMEOUT_IN_SECONDS)
                if self.is_on_login_page(response):
                    response = self.login_to_app(response)
            except Exception, e:
                self.is_login_successful = False
                log.error("Unable to hit the osm end point due to: " + str(e) + "; trying "
                          + str(NUM_TIMES_TO_TRY - i - 1)
                          + " more times.")
            if response and self.is_login_successful:
                self.process_osm_data(response.read(), csv_element)
                break

    def process_osm_data(self, response, csv_element):
        """
        Updates the CSV row with the OSM stats
        :param response: The string response from the server with data for the csv row
        :param csv_element: The csv row to update
        :return: None
        """
        json_data = json.loads(response, strict=False)
        # skip over empty fields
        if not json_data or JSON_OSM_DATA_KEY not in json_data:
            return
        for entry in json_data[JSON_OSM_DATA_KEY]:
            # check that count entry exists
            if JSON_OSM_COUNT_KEY in entry:
                csv_element.num_osm += entry[JSON_OSM_COUNT_KEY]

    def query_twitter(self, order_params, csv_element):
        """
        Queries for Twitter data and updates the CSV row with the stats
        :param order_params: The InsightCloud params for the query
        :param csv_element: The CSV element to update
        :return: None
        """
        twitter_url = TWITTER_QUERY.substitute(upper=str(order_params.top), lower=str(order_params.bottom),
                                               left=str(order_params.left), right=str(order_params.right))
        for i in range(0, NUM_TIMES_TO_TRY):
            response = None
            try:
                request = urllib2.Request(twitter_url)
                response = self.opener.open(request, timeout=TIMEOUT_IN_SECONDS)
                if self.is_on_login_page(response):
                    response = self.login_to_app(response)
            except Exception, e:
                self.is_login_successful = False
                log.error("Unable to hit the twitter end point due to: " + str(e) + "; trying " +
                          str(NUM_TIMES_TO_TRY - i - 1) + " more times.")
            if response and self.is_login_successful:
                self.process_twitter_data(response.read(), csv_element)
                break

    def query_rss(self, order_params, csv_element):
        """
        Queries RSS for data and updates the CSV row with the stats
        :param order_params: The InsightCloud params for the query
        :param csv_element: The CSV element to update
        :return: None
        """
        rss_url = RSS_QUERY.substitute(upper=str(order_params.top), lower=str(order_params.bottom),
                                       left=str(order_params.left), right=str(order_params.right))
        for i in range(0, NUM_TIMES_TO_TRY):
            response = None
            try:
                request = urllib2.Request(rss_url)
                response = self.opener.open(request, timeout=TIMEOUT_IN_SECONDS)
                if self.is_on_login_page(response):
                    response = self.login_to_app(response)
            except Exception, e:
                self.is_login_successful = False
                log.error("Unable to hit the rss end point due to: " + str(e) + "; trying "
                          + str(NUM_TIMES_TO_TRY - i - 1)
                          + " more times.")
            if response and self.is_login_successful:
                self.process_rss_data(response.read(), csv_element)
                break

    def process_sma_data(self, response):
        """
        Processes OSM data (including RSS and Twitter) and returns the stats field
        :param response: The str response from the server
        :return: 0 if there are no stats; else the stats
        """
        json_data = json.loads(response, strict=False)
        # skip over empty fields
        if not json_data or JSON_SMA_HITS_KEY not in json_data or JSON_SMA_TOTAL_KEY not in json_data[JSON_SMA_HITS_KEY]:
            return 0
        return json_data[JSON_SMA_HITS_KEY][JSON_SMA_TOTAL_KEY]

    def process_twitter_data(self, response, csv_element):
        """
        Updates the CSV row with the stats from the Twitter query
        :param response: The str response containing the JSON data from the query
        :param csv_element: The CSV row to update
        :return: None
        """
        csv_element.num_twitter = self.process_sma_data(response)

    def process_rss_data(self, response, csv_element):
        """
        Updates the CSV row with the stats from the RSS query
        :param response: The str response containing JSON data from the query
        :param csv_element: The CSV row to update
        :return: None
        """
        csv_element.num_rss = self.process_sma_data(response)