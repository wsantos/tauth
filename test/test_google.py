from tornado.testing import AsyncHTTPTestCase
import tornado.web
from tornado.options import options
from tauth.google import GoogleOAuth2Mixin
import tauth.google
from tornado import gen
from tornado.web import url
from tornado.concurrent import return_future

fake_google_return = None

#Monkey Path
@return_future
def get_authenticated_user(s, code, callback):
    global fake_google_return
    callback(fake_google_return)


GoogleOAuth2Mixin.get_authenticated_user = get_authenticated_user
GoogleOAuth2Mixin.authorize_redirect = lambda s, perms, redirect_uri: s.redirect("/")



tornado.options.define('google_redirect_uri', type=str, help=(
    "Google Redirect URI"), default="http://localhost:8888/auth/google")

tornado.options.define('google_consumer_key', type=str, help=(
    "Google App ID/API Key"), default="147200258126.apps.googleusercontent.com")

tornado.options.define('google_consumer_secret', type=str, help=(
    "Google App Secret"), default="3uSdIb4k4kT6Sqq3SkpQYj8y")

tornado.options.define('google_permissions', type=str, help=(
    "Google App Permissions"), default="https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email")



class AuthGoogleLoginHandler(tornado.web.RequestHandler, GoogleOAuth2Mixin):
    @tornado.web.asynchronous
    @gen.coroutine
    def get(self):
        my_url = (self.request.protocol + "://" + self.request.host +
                  "/auth/google")

        if self.get_argument("code", None):
            authorization_code = self.get_argument("code", None)
            user = yield self.get_authenticated_user(authorization_code)

            if not user:
                raise tornado.web.HTTPError(500, "Google auth failed")

            self.set_secure_cookie("user", tornado.escape.json_encode(user))
            self.redirect(self.get_secure_cookie("next") or "/")
        else:
            self.set_secure_cookie(
                "next",
                self.get_argument("next", "/")
            )
            self.authorize_redirect(
                options.google_permissions,
                redirect_uri = my_url
            )

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("")

class TestGoogleOAuth2(AsyncHTTPTestCase):

    def get_app(self):
        return tornado.web.Application([
            (r"/", MainHandler),
            url(r"/auth/google/?", AuthGoogleLoginHandler, name="auth_google"),
            ],
            debug = True,
            cookie_secret = "5Tazjk42Rd2p2K5s6AsDZOb5QUKLXUFPnB01S3W5sjM="
        )

    def test_call_google_auth_url(self):
        global fake_google_return
       # Test authenticate_redirect
        self.http_client.fetch(
            self.get_url('/auth/google'), self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200,
            "authenticate_redirect: Response not equal 200"
        )

        # Test get_authenticated_user without user
        self.http_client.fetch(
            self.get_url('/auth/google?code=x'), self.stop)
        response = self.wait()
        self.assertEqual(response.code, 500,
            "get_authenticated_user: Response not equal 500, without user"
        )

        # Test get_authenticated_user with user
        fake_google_return = dict(
            name="Teste rating",
            email="teste@teste.com",
            id="100000000000000000000"
        )

        self.http_client.fetch(
            self.get_url('/auth/google?code=x'), self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200,
                         "get_authenticated_user: Response not equal 200")
