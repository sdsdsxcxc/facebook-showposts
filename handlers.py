import facebook
import webapp2
import os.path
import jinja2
import urllib2
import logging

from webapp2_extras import sessions

from models import User, Posts

from config import config


jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__))
)


class BaseHandler(webapp2.RequestHandler):
    """Provides access to the active Facebook user in self.current_user

    The property is lazy-loaded on first access, using the cookie saved
    by the Facebook JavaScript SDK to determine the user ID of the active
    user. See http://developers.facebook.com/docs/authentication/ for
    more information.
    """
    @property
    def current_user(self):
        """
        :returns object: User object or None
        """
        if not hasattr(self, "_current_user"):
            logging.info("not hasattr")
            self._current_user = None
            cookie = facebook.get_user_from_cookie(
                self.request.cookies,
                self.app.config.get("FACEBOOK_APP_ID", ""),
                self.app.config.get("FACEBOOK_APP_SECRET", ""))
            logging.info(str(self.request.cookies))
            if cookie:
                logging.info("if cookie")
                # Store a local instance of the user data so we don't need
                # a round-trip to Facebook on every request
                user = User.get_by_key_name(cookie["uid"])
                if not user:
                    logging.info("if not user")
                    graph = facebook.GraphAPI(cookie["access_token"])
                    profile = graph.get_object("me")
                    user = User(key_name=str(profile["id"]),
                                id=str(profile["id"]),
                                name=profile["name"],
                                profile_url=profile["link"],
                                access_token=cookie["access_token"])
                    user.put()
                elif user.access_token != cookie["access_token"]:
                    logging.info("elif user.access_token")
                    user.access_token = cookie["access_token"]
                    user.put()
                self._current_user = user
#             else:
#                 return None
        return self._current_user


class HomeHandler(BaseHandler):
    """
    Main Handler
    """
    template = jinja_environment.get_template('templates/main.html')
    def get(self):
        self.show_main()

    def post(self):
        """
        
        Save the Posts for the given User, and delete old Posts
        
        :param str channel: User name, which posts we will save
        """
        channel = self.request.get('channel')
        graph = facebook.GraphAPI(self.current_user.access_token)
        profile = graph.get_object("me")
        logging.info(str(profile))

        posts = None
        try:
            posts = graph.get_object(channel+"/posts", limit=20)
        except Exception as e:
            logging.info(str(e))
#         else:
#             logging.info(posts["data"])
        Posts.refresh_db(posts["data"])

        self.show_main()

    def show_main(self):
        """
        Show the main page
        """
        posts = Posts.get_posts(10)
        logging.info(self.current_user)
        args = dict(current_user=self.current_user,
                    facebook_app_id=self.app.config.get("FACEBOOK_APP_ID", ""),
                    posts=posts)
        logging.info(str(args))
        self.response.out.write(self.template.render(args))


app = webapp2.WSGIApplication(
    [('/', HomeHandler), ],
    debug=True,
    config=config
)
