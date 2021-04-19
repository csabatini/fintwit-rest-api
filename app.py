from flask import Flask, request, abort, jsonify, g
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import desc
from configparser import ConfigParser
from os.path import join, expanduser
from datetime import datetime, timedelta
from logging.config import dictConfig
from config import LOG_CONFIG
import MySQLdb
import json
import logging
import time
import uuid

from models import db, Author, Status, UserProfile, UserFavorite

app = Flask(__name__)
auth = HTTPBasicAuth()
users = {}

def setup_app(application):
    cnf = join(expanduser('~'), '.my.cnf')
    cnf_parser = ConfigParser()
    cnf_parser.read(cnf)
    username = cnf_parser.get('client', 'user')
    password = cnf_parser.get('client', 'password')
    users[username] = generate_password_hash(password)
    application.config['SQLALCHEMY_DATABASE_URI'] = \
        'mysql+mysqldb://%s:%s@localhost/fintwit?charset=utf8mb4' % (username, password)
    application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'False'
    db.init_app(application)
    dictConfig(LOG_CONFIG)
    logging.getLogger('werkzeug').setLevel(logging.CRITICAL)
    app.logger.handlers = logging.getLogger().handlers


setup_app(app)

@auth.verify_password
def verify_password(username, password):
    if username in users:
        return check_password_hash(users.get(username), password)
    return False

@app.route("/", methods=['GET'])
def index():
    return "Fintwit Web Service"


@app.route('/api/v1/status', methods=['GET'])
def status():
    g._kv['action'] = 'query'
    g._kv['userguid'] = None
    filter_date = datetime.utcnow()
    guid = None
    if request.args is not None and 'max_created_at' in request.args:
        filter_date = datetime.fromtimestamp(int(request.args['max_created_at']) / 1000.0)
    results = Status.query.filter(Status.created_at < filter_date)
    if request.args is not None and 'author_id' in request.args:
        results = results.filter(Status.author_id == int(request.args['author_id']))
    if request.args is not None and 'userguid' in request.args:
        userguid = request.args['userguid']
        g._kv['userguid'] = str(userguid)
        results = results.join(UserFavorite, Status.author_id == UserFavorite.author_id) \
                         .filter(UserFavorite.user_guid == userguid) \
                         .filter(UserFavorite.active == 1)

    results = results.order_by(desc(Status.created_at)) \
        .limit(100) \
        .all()
    g._kv['count'] = len(results)

    return jsonify([r.as_dict() for r in results])

@app.route('/api/v1/author', methods=['GET'])
def author():
    g._kv['action'] = 'query'
    author_id = None
    if request.args is not None and 'author_id' in request.args:
        author_id = int(request.args['author_id'])
        result = Author.query.filter(Author.author_id == author_id).first_or_404()
        return jsonify(result.as_dict())
    else:
        return jsonify([r.as_dict() for r in Author.query.all()])


@app.route('/api/v1/user', methods=['POST'])
def user_profile():
    payload = request.get_json()
    if type(payload) is not dict or payload.get('guid', None) is None:
        abort(400)

    guid = payload.get('guid', None)
    token = payload.get('device_token', None)
    push = payload.get('push_setting', None)
    user = UserProfile.query.filter_by(guid=guid).first()
    g._kv['userguid'] = guid
    if user:
        g._kv['action'] = 'login'
        user.device_token = token
        user.push_setting = push
        user.login_time = datetime.utcnow()
        db.session.merge(user)
        db.session.commit()
    else:
        user = UserProfile(guid, push, token)
        db.session.add(user)
        db.session.commit()
        default_fav_one = UserFavorite(user.guid, 20402945, 1) # CNBC
        default_fav_two = UserFavorite(user.guid, 26574283, 1) # CNBCnow
        default_fav_three = UserFavorite(user.guid, 36992781, 1) # CNBCPro
        default_fav_four = UserFavorite(user.guid, 1278852289, 1) # TradingNation
        default_fav_five = UserFavorite(user.guid, 16451932, 1) # MadMoneyOnCNBC
        db.session.merge(default_fav_one)
        db.session.merge(default_fav_two)
        db.session.merge(default_fav_three)
        db.session.merge(default_fav_four)
        db.session.merge(default_fav_five)
        db.session.commit()
        g._kv['action'] = 'register'

    return jsonify(user.as_dict())

@app.route('/api/v1/favorite', methods=['POST'])
def favorite():
    payload = request.get_json()
    if type(payload) is not dict:
        abort(400)

    user_guid = None
    fav_list = []
    try:
        user_guid = payload['user_profile']['guid']
        fav_list = payload['favorite_list']
    except Exception as e:
        abort(400)

    user = UserProfile.query.filter_by(guid=user_guid).first_or_404()

    for fav in fav_list:
        uf = UserFavorite(user.guid, fav['author_id'], fav['active'])
        db.session.merge(uf)
    db.session.commit()

    return jsonify({'success': True})

@app.route('/api/v1/load', methods=['POST'])
@auth.login_required
def load():
    users = request.get_json().get('users', [])
    statuses = request.get_json().get('statuses', [])
    if not users or not statuses:
        return jsonify({'success': True, 'count': len(statuses)})
    db = MySQLdb.connect(read_default_file='/home/webapp/.my.cnf', db='fintwit', use_unicode=True, charset="utf8")
    cursor = db.cursor()
    cursor.execute("SET NAMES utf8mb4")
    cursor.execute("SET CHARACTER SET utf8mb4")
    cursor.execute("SET character_set_connection=utf8mb4")
    for k, v in users.items():
        cursor.execute("INSERT INTO author (author_id, screen_name, name, profile_img_url, location, description) VALUES (%s, %s, %s, %s, %s, %s) "
                       "ON DUPLICATE KEY UPDATE screen_name=values(screen_name), name=values(name), profile_img_url=values(profile_img_url), location=values(location), description=values(description)",
                       (v['author_id'], v['screen_name'], v['name'], v['profile_img_url'], v['location'], v['description']))
    db.commit()
    for s in statuses:
        cursor.execute("INSERT IGNORE INTO status (status_id, author_id, created_at, text, quote_author_id, quote_text) SELECT %s, %s, %s, %s, %s, %s",
                      (s['id'], s['author_id'], s['timestamp'], s['text'], s['quote_author_id'], s['quote_text']))
        for url in s['media_urls']:
            cursor.execute("INSERT IGNORE INTO status_media (status_id, media_url) SELECT %s, %s", (s['id'], url))
    db.commit()
    cursor.close()
    db.close()
    return jsonify({'success': True, 'count': len(statuses)})


@app.before_request
def before_request():
    # TODO: fix the hardcoding of this
    # g._kv = dict(app_id=os.environ.get('APP_ID', None))
    g._kv = dict(app_id='fintwit')
    return None


@app.after_request
def after_request(response):
    """ Logging after every request. """
    g._kv.update({
        'ip': request.remote_addr,
        'method': request.method,
        'url': request.path,
        'status': response.status,
        'user_agent': dict(request.headers).get('User-Agent', None)
    })
    app.logger.info(json.dumps(g._kv))
    return response


if __name__ == '__main__':
    app.run(host="0.0.0.0")
