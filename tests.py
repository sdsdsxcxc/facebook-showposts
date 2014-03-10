'''
Run the tests using testrunner.py script in the project root directory.

Usage: testrunner.py SDK_PATH TEST_PATH
Run unit tests for App Engine apps.

SDK_PATH    Path to the SDK installation
TEST_PATH   Path to package containing test modules

Options:
  -h, --help  show this help message and exit

'''
import unittest
import webapp2
import os
import webtest
from google.appengine.ext import testbed

from test_tools import test_helpers
from test_tools import config, routes, facebook_api_data

from models import Posts


class AppTest(unittest.TestCase, test_helpers.HandlerHelpers):
    def setUp(self):
        webapp2_config = config.config

        # create a WSGI application.
        self.app = webapp2.WSGIApplication(config=webapp2_config)
        routes.add_routes(self.app)
#        boilerplate_routes.add_routes(self.app)
        self.testapp = webtest.TestApp(self.app, extra_environ={'REMOTE_ADDR': '127.0.0.1'})

        # activate GAE stubs
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_urlfetch_stub()
        self.testbed.init_taskqueue_stub()
        self.testbed.init_mail_stub()
        self.testbed.init_blobstore_stub()
        self.testbed.init_modules_stub()
        self.mail_stub = self.testbed.get_stub(testbed.MAIL_SERVICE_NAME)
        self.taskqueue_stub = self.testbed.get_stub(testbed.TASKQUEUE_SERVICE_NAME)
        self.testbed.init_user_stub()

        self.headers = {'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) Version/6.0 Safari/536.25',
                        'Accept-Language' : 'en_US'}

    def tearDown(self):
        self.testbed.deactivate()

    def test_homepage(self):
        response = self.get('/')
        self.assertIn('Facebook Posts', response)

    def test_refresh_db(self):
        Posts.refresh_db(facebook_api_data.resp1["data"])
        self.assertEqual(Posts.query().count(), 10)
        Posts.refresh_db(facebook_api_data.resp2["data"])
        self.assertEqual(Posts.query().count(), 1)

    def test_get_posts(self):
        Posts.refresh_db(facebook_api_data.resp1["data"])
        posts = Posts.get_posts(10)
        self.assertEqual(len(posts), 10)
        self.assertIn('La Grande Bellezza', posts[0]["message"])
        

if __name__ == "__main__":
    unittest.main()
