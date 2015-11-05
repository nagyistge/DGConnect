# -*- coding: utf-8 -*-
__author__ = 'Michael Trotter <michael.trotter@digitalglobe.com>'

from string import Template

from datetime import timedelta, datetime

import json

import urllib
import urllib2
import cookielib

from qgis.core import QgsMessageLog

from base64 import b64encode

# User Agent String; let's pretend we're chromium on Ubuntu
USER_AGENT_STRING = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                    'Ubuntu Chromium/41.0.2272.76 Chrome/41.0.2272.76 Safari/537.36'

# oauth2 urls
TOP_LEVEL_URL = 'https://iipbeta.digitalglobe.com/'
LOGIN_URL = TOP_LEVEL_URL + "cas/oauth/token"
TEST_LOGIN_URL = TOP_LEVEL_URL + "insight-vector/api/version"

# json keys
JSON_ENCODING = 'utf8'
KEY_ACCESS_TOKEN = 'access_token'
KEY_TOKEN_TYPE = 'token_type'

# http headers
HEADER_AUTHORIZATION = 'Authorization'
HEADER_USER_AGENT = 'User-Agent'
HEADER_CONTENT_TYPE = 'Content-Type'

CONTENT_TYPE_JSON = 'application/json'

# tag name
TAG_NAME = 'InfoCube (GBD)'

class OAuth2Query(object):
    """
    Class for querying to get data for InfoCube
    """

    def __init__(self, username, password, client_id, client_secret, grant_type='password'):
        self.username = username
        self.password = password
        self.client_id = client_id
        self.client_secret = client_secret
        self.grant_type = grant_type
        self.access_token = None
        self.token_type = None
        self.headers = {
            HEADER_AUTHORIZATION: 'Basic ' + b64encode(self.client_id + ':' + self.client_secret),
            HEADER_USER_AGENT: USER_AGENT_STRING
        }
        self.opener = None
        self.is_login_successful = False

    def log_in(self):
        """
        Log in to OAuth2 using the credentials provided to the constructor
        :return: None
        """
        # prep data
        data = {
            'username': self.username,
            'password': self.password,
            'grant_type': self.grant_type
        }
        encoded_data = urllib.urlencode(data)

        # build up request with cookie jar and basic auth handler
        cookie_jar = cookielib.LWPCookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie_jar))
        
        headers = self.headers
        headers[HEADER_AUTHORIZATION] = 'Basic ' + b64encode(self.client_id + ':' + self.client_secret)

        try:
            request = urllib2.Request(url=LOGIN_URL, data=encoded_data, headers=headers)
            response = self.opener.open(request)
            response_data = response.read()
            json_data = json.loads(response_data, strict=False)
            self.access_token = json_data[KEY_ACCESS_TOKEN].encode(JSON_ENCODING)
            self.token_type = json_data[KEY_TOKEN_TYPE].encode(JSON_ENCODING)
            self.update_headers_with_access_info()
        except Exception, e:
            QgsMessageLog.instance().logMessage("Exception detected during log in: " + str(e), TAG_NAME,
                                                level=QgsMessageLog.CRITICAL)
            self.is_login_successful = False

    def update_headers_with_access_info(self):
        """
        Helper method for updating the authorization header after log-in
        :return:
        """
        self.headers[HEADER_AUTHORIZATION] = "%s %s" % (self.token_type, self.access_token)

    def hit_test_endpoint(self):
        """
        Hits the test end point for checking if the credentials provided are valid;
        Must be done after logging in first
        :return: None
        """
        try:
            request = urllib2.Request(TEST_LOGIN_URL, headers=self.headers)
            response = self.opener.open(request)
            if len(response.read()) > 0:
                self.is_login_successful = True
        except Exception, e:
            QgsMessageLog.instance().logMessage("Exception detected during endpoint test: " + str(e),
                                                TAG_NAME, level=QgsMessageLog.CRITICAL)
            self.is_login_successful = False
    
    def get_opener(self):
        return self.opener
    
    def get_headers(self):
        return self.headers
