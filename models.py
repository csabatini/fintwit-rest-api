from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, ForeignKey
from datetime import datetime

db = SQLAlchemy()


class BaseModel(object):
    def as_dict(self):
        return {c.key: getattr(self, c.key)
                for c in inspect(self).mapper.column_attrs}


class UserProfile(db.Model, BaseModel):
    __tablename__ = 'user_profile'
    guid = db.Column(db.String(36), primary_key=True)
    push_setting = db.Column(db.Integer)
    device_token = db.Column(db.String(200))
    created_time = db.Column(db.DateTime, default=datetime.utcnow)
    login_time = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, guid=None, push_setting=None, device_token=None):
        self.guid = guid
        self.push_setting = push_setting
        self.device_token = device_token

    def as_dict(self):
        dict = BaseModel.as_dict(self)
        del dict['created_time']
        del dict['login_time']
        return dict


class Status(db.Model, BaseModel):
    __tablename__ = 'vw_status_author'
    status_id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime)
    author_id = db.Column(db.Integer)
    screen_name = db.Column(db.String(255))
    name = db.Column(db.String(255))
    profile_img_url = db.Column(db.String(255))
    text = db.Column(db.String(255))
    quote_author_id = db.Column(db.Integer)
    quote_screen_name = db.Column(db.String(255))
    quote_name = db.Column(db.String(255))
    quote_text = db.Column(db.String(255))

    media_urls = db.relationship("StatusMedia", backref="vw_status_author")

    def as_dict(self):
        dict = {}
        dict['status'] = BaseModel.as_dict(self)
        dict['status']['created_at'] = get_unixtime(self.created_at)
        dict['media_urls'] = [x.media_url for x in self.media_urls]
        return dict


class StatusMedia(db.Model, BaseModel):
    __tablename__ = 'status_media'
    status_id = db.Column(db.Integer, ForeignKey(Status.status_id), primary_key=True)
    media_url = db.Column(db.String, primary_key=True)

    def __init__(self, status_id=None, media_url=None):
        self.status_id = status_id
        self.media_url = media_url

class Author(db.Model, BaseModel):
    __tablename__ = 'author'
    author_id = db.Column(db.Integer, primary_key=True)
    screen_name = db.Column(db.String(100))
    name = db.Column(db.String(100))
    profile_img_url = db.Column(db.String(500))
    location = db.Column(db.String(255))
    description = db.Column(db.String(500))

class UserFavorite(db.Model, BaseModel):
    __tablename__ = 'user_favorite'
    user_guid = db.Column(db.Integer, ForeignKey(UserProfile.guid), primary_key=True)
    author_id = db.Column(db.Integer, ForeignKey(Author.author_id), primary_key=True)
    active = db.Column(db.Integer)

    def __init__(self, user_guid=None, author_id=None, active=None):
        self.user_guid = user_guid
        self.author_id = author_id
        self.active = active

def get_unixtime(timestamp):
    epoch = datetime.utcfromtimestamp(0)
    return int((timestamp - epoch).total_seconds() * 1000.0)
