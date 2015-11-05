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
TOP_LEVEL_URL = 'https://iipbeta.digitalglobe.com/'
LOGIN_URL = TOP_LEVEL_URL + "cas/oauth/token"

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
TAG_NAME = 'DGX'

class OAuth2Query(object):
    """
    Class for querying to get data for Catalog
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
        self.token_lock = Lock()

    def log_in(self):
        """
        Log in to OAuth2 using the credentials provided to the constructor
        :return: None
        """
        if not self.is_login_successful:
            with self.token_lock:
                if not self.is_login_successful:
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
                        self.headers[HEADER_AUTHORIZATION] = "%s %s" % (self.token_type, self.access_token)
                        self.is_login_successful = True
                    except Exception, e:
                        QgsMessageLog.instance().logMessage("Exception detected during log in: " + str(e), TAG_NAME, level=QgsMessageLog.CRITICAL)
                        self.is_login_successful = False

    def get_opener(self):
        return self.opener

    def get_headers(self):
        return self.headers

