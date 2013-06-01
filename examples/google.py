#!/usr/bin/env python
import tornado.ioloop
import tornado.web
from tornado import gen
from tornado.options import options
from tornado.web import url
from tauth.google import GoogleOAuth2Mixin

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
            print "cacaca"
            authorization_code = self.get_argument("code", None)
            user = yield self.get_authenticated_user(authorization_code)

            print "Valor: %s" % user

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
        self.write("Hello, world<br><br>")
        self.write("Login Cookie Data: %s" % self.get_secure_cookie("user"))

application = tornado.web.Application([
    (r"/", MainHandler),
    url(r"/auth/google/?", AuthGoogleLoginHandler, name="auth_google"),
    ],
    debug = True,
    cookie_secret = "5Tazjk42Rd2p2K5s6AsDZOb5QUKLXUFPnB01S3W5sjM="
)

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
