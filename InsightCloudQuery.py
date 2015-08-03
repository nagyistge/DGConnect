__author__ = 'Michael Trotter <michael.trotter@digitalglobe.com>'

from string import Template

import re

import urllib
import urllib2
import cookielib

import logging as log

from CASHTMLParser import CASFormHTMLParser

MONOCLE_3_URL = "https://iipbeta.digitalglboe.com/monocle-3/"
VECTOR_TYPE_QUERY = Template(MONOCLE_3_URL + "app/broker/vector/api/vectors/OSM/types?left=$left&right=$right&upper=$upper&lower=$lower")
TWITTER_QUERY = Template(MONOCLE_3_URL + "app/broker/sma/sma/twitter/tweets?bbox=$left,$lower,$right,$upper&daterange=$time_begin-$time_end&dimensionality=stats")
RSS_QUERY = Template(MONOCLE_3_URL + "app/broker/sma/sma/rss/sentences?bbox=$left,$lower,$right,$upper&daterange=$time_begin-$time_end&dimensionality=stats")

URL_CAS_LOGIN_SEGMENT = "login"

KEY_HEADER_REFERRER = 'Referer'

FIELD_USERNAME = "username"
FIELD_PASSWORD = "password"
URL_MATCH = re.compile('(.*://[^/]*)')

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
            response = self.opener.open(MONOCLE_3_URL)
            if self.is_on_login_page(response):
                response = self.login_to_app(response)
        except Exception, e:
            self.is_login_successful = False
            log.error("Unable to log into Monocle-3 due to: " + str(e))
        if response and self.is_login_successful:
            return response.read()
        return None