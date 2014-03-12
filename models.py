import sys
import logging
from google.appengine.ext import ndb
from google.appengine.api import memcache
from google.appengine.ext import db
from dateutil.parser import parse
from dateutil import tz


class Posts(ndb.Model):
    """
    Model for storing the Facebook Posts
    """
#     id = ndb.StringProperty()
    from_ = ndb.PickleProperty()
    to = ndb.PickleProperty()
    message = ndb.TextProperty()
    message_tags = ndb.PickleProperty()
    picture = ndb.StringProperty()
    link = ndb.StringProperty()
    actions = ndb.PickleProperty()
    type = ndb.StringProperty()
    status_type = ndb.StringProperty()
    created_time = ndb.DateTimeProperty()
    updated_time = ndb.DateTimeProperty()
    shares = ndb.PickleProperty()
    likes = ndb.PickleProperty()

    @classmethod
    def save(cls, data):
        """
        
        Save an entity in DB.
        
        :param dict data: Item from the 'data' section of the dictionary that was received from
                          the Facebook API request /posts/
        :return: Nothing
        """
        record = cls.get_or_insert(
            data["id"],
            from_ = data.get("from", {}),
            to = data.get("to", {}),
            message = data.get("message", ""),
            message_tags = data.get("message_tags", {}),
            picture = data.get("picture", ""),
            link = data.get("link", ""),
            actions = data.get("actions", {}),
            type = data.get("type", ""),
            status_type = data.get("status_type", ""),
            # gae date issue solving:
            # http://hype-free.blogspot.ru/2013/02/converting-datetime-to-utc-in-python.html
            created_time = parse(data["created_time"]).astimezone(tz.tzutc()).replace(tzinfo=None),
            updated_time = parse(data["updated_time"]).astimezone(tz.tzutc()).replace(tzinfo=None),
            shares = data.get("shares", {}),
            likes = data.get("likes", {}),
            )
        return None

    @classmethod
    def refresh_db(cls, data):
        """
        
        Delete old posts and save new posts.

        :param dict data: 'data' section of the dictionary that was received from
                          the Facebook API request /posts/
        :returns: Nothing
        """
        db_keys = cls.query().fetch(keys_only=True)
        keys = [ndb.Key(cls, item["id"]) for item in data]
        old_keys = [key for key in db_keys if key not in keys]
        logging.info(str(old_keys))
        if old_keys:
            ndb.delete_multi(old_keys)
        for post in data:
            cls.save(post)
        return None

    @classmethod
    def get_posts(cls, PageSize):
        """
        
        Get the Posts from the DB
        
        :param int page_size: Limit number of the posts returned by this call
        :returns dict: Posts
        """
        qr = cls.query().order(cls.key)
        result = qr.map(lambda rec: rec.to_dict(), limit=PageSize)
        return result


class User(db.Model):
    """
    Model for storing the User Information
    """
    id = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)
    name = db.StringProperty(required=True)
    profile_url = db.StringProperty(required=True)
    access_token = db.StringProperty(required=True)

