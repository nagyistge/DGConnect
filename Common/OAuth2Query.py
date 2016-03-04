# -*- coding: utf-8 -*-
from base64 import b64encode
import cookielib
from datetime import timedelta, datetime
import json
from multiprocessing import Lock
from qgis.core import QgsMessageLog
from string import Template
import urllib
import urllib2


# User Agent String; let's pretend we're chromium on Ubuntu
USER_AGENT_STRING = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                    'Ubuntu Chromium/41.0.2272.76 Chrome/41.0.2272.76 Safari/537.36'

# oauth2 urls
TOP_LEVEL_URL = 'https://geobigdata.io/'
LOGIN_URL = TOP_LEVEL_URL + "auth/v1/oauth/token"

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
TAG_NAME = 'GBDX'

class OAuth2Query(object):
    """
    Class for querying to get data for Catalog
    """
    
    token_lock = Lock()
    headers = None

    def __init__(self, username, password, api_key, grant_type='password'):
        self.username = username
        self.password = password
        self.api_key = api_key
        self.grant_type = grant_type
        self.is_login_successful = False
        self.opener = None
        self.basic_header = {
            HEADER_AUTHORIZATION: 'Basic ' + api_key,
            HEADER_USER_AGENT: USER_AGENT_STRING
        }

    def log_in(self):
        """
        Log in to OAuth2 using the credentials provided to the constructor
        :return: None
        """
        if not self.opener:
            # build up request with cookie jar and basic auth handler
            cookie_jar = cookielib.LWPCookieJar()
            self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie_jar))

        if not OAuth2Query.headers:
            with OAuth2Query.token_lock:
                if not OAuth2Query.headers:
                    # prep data
                    data = {
                        'username': self.username,
                        'password': self.password,
                        'grant_type': self.grant_type
                    }
                    encoded_data = urllib.urlencode(data)
                    
                    basic_header = self.basic_header
                    basic_header[HEADER_AUTHORIZATION] = 'Basic ' + self.api_key
            
                    try:
                        request = urllib2.Request(url=LOGIN_URL, data=encoded_data, headers=basic_header)
                        response = self.opener.open(request)
                        response_data = response.read()
                        json_data = json.loads(response_data, strict=False)
                        
                        access_token = json_data[KEY_ACCESS_TOKEN].encode(JSON_ENCODING)                    
                        token_type = json_data[KEY_TOKEN_TYPE].encode(JSON_ENCODING)
                        
                        OAuth2Query.headers = {}
                        OAuth2Query.headers[HEADER_AUTHORIZATION] = "%s %s" % (token_type, access_token)
                        
                        self.is_login_successful = True
                        
                    except Exception, e:
                        self.is_login_successful = False
                        QgsMessageLog.instance().logMessage("Exception detected during log in: " + str(e), TAG_NAME, level=QgsMessageLog.CRITICAL)
        else:
            self.is_login_successful = True

    def get_opener(self):
        return self.opener

    def get_headers(self):
        return OAuth2Query.headers

