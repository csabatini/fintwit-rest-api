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
    push_enabled = db.Column(db.Boolean)
    device_token = db.Column(db.String(200))
    created_time = db.Column(db.DateTime)

    def __init__(self, guid=None, push_enabled=None, device_token=None):
        self.guid = guid
        self.push_enabled = push_enabled
        self.device_token = device_token

    def as_dict(self):
        dict = BaseModel.as_dict(self)
        del dict['created_time']
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
    quote_screen_name = db.Column(db.String(255))
    quote_name = db.Column(db.String(255))
    quote_text = db.Column(db.String(255))

    media_urls = db.relationship("StatusMedia", backref="vw_status_author")

    def __init__(self, status_id=None, created_at=None, author_id=None, screen_name=None, name=None,
                 profile_img_url=None, text=None, quote_screen_name=None, quote_name=None, quote_text=None):
        self.status_id = status_id
        self.created_at = created_at
        self.author_id = author_id
        self.screen_name = screen_name
        self.name = name
        self.profile_img_url = profile_img_url
        self.text = text
        self.quote_screen_name = quote_screen_name
        self.quote_name = quote_name
        self.quote_text = quote_text

    def as_dict(self):
        dict = {}
        dict['status'] = BaseModel.as_dict(self)
        dict['status']['created_at'] = get_unixtime(self.created_at)
        dict['media_urls'] = [x.media_url for x in self.media_urls]
        return dict


class StatusMedia(db.Model, BaseModel):
    __tablename__ = 'status_media'
    status_media_id = db.Column(db.Integer, primary_key=True)
    status_id = db.Column(db.Integer, ForeignKey(Status.status_id))
    media_url = db.Column(db.String)

    def __init__(self, status_media_id=None, status_id=None, media_url=None):
        self.status_media_id = status_media_id
        self.status_id = status_id
        self.media_url = media_url

# class Author(db.Model, BaseModel):
#     __tablename__ = 'author'
#     user_id = db.Column(db.Integer, primary_key=True)
#     screen_name = db.Column(db.String(100))
#     name = db.Column(db.String(100))
#     profile_img_url = db.Column(db.String(500))
#     location = db.Column(db.String(200))
#     description = db.Column(db.String(500))

#     def __init__(self, tag_id=None, tag=None):
#         self.tag_id = tag_id
#         self.tag = tag


# class StatusTag(db.Model, BaseModel):
#     __tablename__ = 'status_tag_v2'
#     status_tag_v2_id = db.Column(db.Integer, primary_key=True)
#     status_id = db.Column(db.String(36), ForeignKey(Status.status_id))
#     tag_id = db.Column(db.Integer, ForeignKey(Tag.tag_id))

#     tag = db.relationship('Tag', foreign_keys='StatusTag.tag_id', lazy='joined')

#     def as_dict(self):
#         return self.tag.as_dict()


def get_unixtime(timestamp):
    epoch = datetime.utcfromtimestamp(0)
    return int((timestamp - epoch).total_seconds() * 1000.0)
