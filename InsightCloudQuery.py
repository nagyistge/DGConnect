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
JSON_TWITTER_HITS_KEY = u'hits'
JSON_TWITTER_TOTAL_KEY = u'total'

class InsightCloudParams:
    def __init__(self, top, right, bottom, left, time_begin=None, time_end=None):
        self.top = top
        self.right = right
        self.bottom = bottom
        self.left = left
        self.time_begin = time_begin
        self.time_end = time_end

class InsightCloudQuery:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.CookieJar()))
        self.is_login_successful = True

    @classmethod
    def is_on_login_page(cls, response):
        return URL_CAS_LOGIN_SEGMENT in response.geturl()

    @classmethod
    def build_form_info(cls, response_url, form_data):
        parser = CASFormHTMLParser()
        parser.feed(form_data)
        action = parser.action
        match = re.match(URL_MATCH, response_url)
        if match:
            return match.group(0) + action, parser.hidden_data
        return None

    def post_login_credentials_to_app(self, url_data, redirect_header):
        # post the credentials
        response = None
        try:
            unencoded_data = dict({FIELD_USERNAME : self.username, FIELD_PASSWORD : self.password}.items() + url_data[1].items())
            data = urllib.urlencode(unencoded_data)
            request = urllib2.Request(url=url_data[0], data=data, headers={KEY_HEADER_REFERRER: redirect_header})
            response = self.opener.open(request, data)
        except Exception, e:
            self.is_login_successful = False
            log.error("Unable to post login credentials due to: " + str(e))
        return response

    def login_to_app(self, response):
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
        response = None
        try:
            request = urllib2.Request(MONOCLE_3_URL)
            response = self.opener.open(request)
            if self.is_on_login_page(response):
                response = self.login_to_app(response)
        except Exception, e:
            self.is_login_successful = False
            log.error("Unable to log into Monocle-3 due to: " + str(e))
        if response and self.is_login_successful:
            return response.read()
        return None

    def query_osm(self, order_params, csv_element):
        osm_url = VECTOR_TYPE_QUERY.substitute(top=str(order_params.top), right=str(order_params.right),
                                               bottom=str(order_params.bottom), left=str(order_params.left))
        response = None
        try:
            request = urllib2.Request(osm_url)
            response = self.opener.open(request)
            if self.is_on_login_page(response):
                response = self.login_to_app(response)
        except Exception, e:
            self.is_login_successful = False
            log.error("Unable to hit the osm end point due to: " + str(e))
        if response and self.is_login_successful:
            self.process_osm_data(response.read(), csv_element)

    def process_osm_data(self, response, csv_element):
        json_data = json.loads(response, strict=False)
        # skip over empty fields
        if not json_data or JSON_OSM_DATA_KEY not in json_data:
            return
        for entry in json_data[JSON_OSM_DATA_KEY]:
            # check that count entry exists
            if JSON_OSM_COUNT_KEY in entry:
                csv_element.num_osm += entry[JSON_OSM_COUNT_KEY]

    def query_twitter(self, order_params, csv_element):
        twitter_url = TWITTER_QUERY.substitute(upper=str(order_params.top), lower=str(order_params.bottom),
                                               left=str(order_params.left), right=str(order_params.right))
        response = None
        try:
            request = urllib2.Request(twitter_url)
            response = self.opener.open(request)
            if self.is_on_login_page(response):
                response = self.login_to_app(response)
        except Exception, e:
            self.is_login_successful = False
            log.error("Unable to hit the twitter end point due to: " + str(e))
        if response and self.is_login_successful:
            self.process_twitter_data(response.read(), csv_element)

    def process_twitter_data(self, response, csv_element):
        json_data = json.loads(response, strict=False)
        # skip over empty fields
        if not json_data or JSON_TWITTER_HITS_KEY not in json_data or JSON_TWITTER_TOTAL_KEY not in json_data[JSON_TWITTER_HITS_KEY]:
            return
        csv_element.num_twitter = json_data[JSON_TWITTER_HITS_KEY][JSON_TWITTER_TOTAL_KEY]