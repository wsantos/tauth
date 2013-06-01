import tornado.auth
from tornado import httpclient
from tornado import httputil
from tornado.httputil import url_concat
from tornado.options import options
from tornado import escape
from tornado.concurrent import Future
from tornado import gen
import logging
import urllib

class GoogleOAuth2Mixin(tornado.auth.OAuth2Mixin):

    access_token = ""
    _OAUTH_AUTHENTICATE_URL = "https://accounts.google.com/o/oauth2/auth"
    _OAUTH_ACCESS_TOKEN_URL = "https://accounts.google.com/o/oauth2/token"
    _OAUTH_TOKEN_VALIDATION_URL = "https://www.googleapis.com/oauth2/v1/tokeninfo"
    _OAUTH_USERINFO_URL = "https://www.googleapis.com/oauth2/v1/userinfo"
    _USER_INFO_URL = "https://www.googleapis.com/oauth2/v1/userinfo"

    @property
    def httpclient_instance(self):
        return httpclient.AsyncHTTPClient()

    @property
    def authorization_header(self):
        return {
            "Authorization": "Bearer "+GoogleOAuth2Mixin.access_token
        }


    def authorize_redirect(self, scope, **kwargs):
        args = {
          "redirect_uri": options.google_redirect_uri,
          "client_id": options.google_consumer_key,
          "response_type": "code",
          "scope": scope
        }
        if kwargs: args.update(kwargs)
        self.redirect(url_concat(self._OAUTH_AUTHENTICATE_URL, args))

    @gen.coroutine
    def get_session(self, authorization_code):
        args = {
            "redirect_uri": options.google_redirect_uri,
            "client_id": options.google_consumer_key,
            "code": authorization_code,
            "client_secret": options.google_consumer_secret,
            "grant_type": "authorization_code"
        }

        request = httpclient.HTTPRequest(
            self._OAUTH_ACCESS_TOKEN_URL,
            method="POST",
            body=urllib.urlencode(args)
        )

        response = yield self.httpclient_instance.fetch(request)

        session = escape.json_decode(response.body)
        GoogleOAuth2Mixin.access_token = session['access_token']

        raise gen.Return(session)



    @gen.coroutine
    def validate_token(self, session):
        response = yield self.httpclient_instance.fetch(
            self._OAUTH_TOKEN_VALIDATION_URL+"?access_token="+session['access_token'],
        )

        raise gen.Return(False if response.error else True)

    @gen.coroutine
    def get_authenticated_user(self, authorization_code, callback):
        session = yield self.get_session(authorization_code)
        valid_token = yield self.validate_token(session)
        if valid_token:
            response = yield self.httpclient_instance.fetch(
                self._OAUTH_USERINFO_URL+"?access_token="+session['access_token'],
                headers=self.authorization_header
            )

            raise gen.Return(escape.json_decode(response.body))

