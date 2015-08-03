__author__ = 'Michael Trotter <michael.trotter@digitalglobe.com>'

from string import Template

from datetime import timedelta, datetime

import json

import urllib
import urllib2
import cookielib

import logging as log

# User Agent String; let's pretend we're chromium on Ubuntu
USER_AGENT_STRING = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                    'Ubuntu Chromium/41.0.2272.76 Chrome/41.0.2272.76 Safari/537.36'

# polygon template for gbd ordering
POLYGON_TEMPLATE = Template("POLGON (($left $bottom, $left $top, $right $top, $right $bottom $left $bottom))")

# gbd urls
GBD_TOP_LEVEL_URL = 'https://geobigdata.io/'
GBD_LOGIN_URL = GBD_TOP_LEVEL_URL + "auth/v1/oauth/token/"
GBD_TEST_LOGIN_URL = GBD_TOP_LEVEL_URL + "workflows/v1/authtest"
GBD_SEARCH_AOI_AND_TIME_URL = GBD_TOP_LEVEL_URL + "catalog/v1/search"

# data format for parsing
ISO_FORMAT = '%Y-%m-%dT%H:%M%S.%fZ'

# json keys
JSON_ENCODING = 'utf8'
KEY_ACCESS_TOKEN = 'access_token'
KEY_TOKEN_TYPE = 'token_type'

# http headers
HEADER_AUTHORIZATION = 'Authorization'
HEADER_USER_AGENT = 'User-Agent'

class OrderParams:
    def __init__(self, top, bottom, left, right):
        self.top = top
        self.bottom = bottom
        self.left = left
        self.right = right
        self.template = self.build_polygon()

    def build_polygon(self):
        return POLYGON_TEMPLATE.substitute(top=str(self.top), right=(str(self.right)), bottom=str(self.bottom),
                                           left=str(self.left))

class GBDQuery:
    def __init__(self, auth_token, username, password, grant_type='password'):
        self.auth_token = auth_token
        self.username = username
        self.password = password
        self.grant_type = grant_type
        self.access_token = None
        self.token_type = None
        self.headers = {
            HEADER_AUTHORIZATION: 'Basic ' + self.auth_token,
            HEADER_USER_AGENT: USER_AGENT_STRING
        }
        self.opener = None
        self.is_login_successful = False

    def log_in(self):
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

        try:
            request = urllib2.Request(GBD_LOGIN_URL, encoded_data, headers=self.headers)
            response = self.opener.open(request)
            response_data = response.read()
            json_data = json.loads(response_data)
            self.access_token = json_data[KEY_ACCESS_TOKEN].encode(JSON_ENCODING)
            self.token_type = json_data[KEY_TOKEN_TYPE].encode(JSON_ENCODING)
            self.update_headers_with_access_info()
        except Exception, e:
            log.error("Exception detected during log in: " + str(e))
            self.is_login_successful = False

    def update_headers_with_access_info(self):
        self.headers[HEADER_AUTHORIZATION] = "%s %s" % (self.token_type, self.access_token)

    def hit_test_endpoint(self):
        try:
            request = urllib2.Request(GBD_TEST_LOGIN_URL, headers=self.headers)
            response = self.opener.open(request)
            if len(response.read()) > 0:
                self.is_login_successful = True
        except Exception, e:
            log.error("Exception detected during endpoint text: " + str(e))
            self.is_login_successful = False
