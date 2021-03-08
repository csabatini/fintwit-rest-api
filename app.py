from flask import Flask, request, abort, jsonify, g
from sqlalchemy import desc
from ConfigParser import ConfigParser
from os.path import join, expanduser
from datetime import datetime, timedelta
from logging.config import dictConfig
from config import LOG_CONFIG
import json
import logging
import time
import uuid

from models import db, Author, Status, UserProfile, UserFavorite

app = Flask(__name__)


def setup_app(application):
    cnf = join(expanduser('~'), '.my.cnf')
    cnf_parser = ConfigParser()
    cnf_parser.read(cnf)
    username = cnf_parser.get('client', 'user')
    password = cnf_parser.get('client', 'password')
    application.config['SQLALCHEMY_DATABASE_URI'] = \
        'mysql+mysqldb://%s:%s@localhost/fintwit?charset=utf8mb4' % (username, password)
    application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'False'
    db.init_app(application)
    dictConfig(LOG_CONFIG)
    logging.getLogger('werkzeug').setLevel(logging.CRITICAL)
    app.logger.handlers = logging.getLogger().handlers


setup_app(app)


@app.route("/", methods=['GET'])
def index():
    return "Fintwit Web Service"


@app.route('/api/v1/status', methods=['GET'])
def status():
    g._kv['action'] = 'query'
    filter_date = datetime.utcnow()
    guid = None
    if request.args is not None and 'max_created_at' in request.args:
        filter_date = datetime.fromtimestamp(long(request.args['max_created_at']) / 1000.0)
    results = Status.query.filter(Status.created_at <= filter_date)
    if request.args is not None and 'max_created_at' in request.args:
        guid = request.args['guid']
        results = results.join(UserFavorite, Status.author_id == UserFavorite.author_id)
                         .filter(UserFavorite.user_guid == guid)

    results = results.order_by(desc(Status.created_at)) \
        .limit(200 if not guid else 100) \
        .all()
    g._kv['count'] = len(results)
    g._kv['userguid'] = dict(request.headers).get('Userguid', None)

    return jsonify([r.as_dict() for r in results])

@app.route('/api/v1/author', methods=['GET'])
def author():
    g._kv['action'] = 'query'
    author_id = None
    if request.args is not None and 'author_id' in request.args:
        author_id = long(request.args['author_id'])
        result = Author.query.filter(Author.author_id == author_id).first_or_404()
        return jsonify(result.as_dict())
    else:
        return jsonify([r.as_dict() for r in Author.query.all()])


@app.route('/api/v1/user', methods=['POST'])
def user_profile():
    payload = request.get_json()
    if type(payload) is not dict or payload.get('guid', None) is None:
        abort(400)

    user = UserProfile.query.filter_by(guid=payload['guid']).first()
    if user:
        g._kv['action'] = 'login'
    else:
        user = \
            UserProfile(payload['guid'], payload['push_enabled'], payload['device_token'])
        db.session.add(user)
        g._kv['action'] = 'register'

    token = payload.get('device_token', None)
    push = payload.get('push_enabled', None)

    if token and token != user.device_token:
        user.device_token = token

    if push and push != user.push_enabled:
        user.push_enabled = push
        g._kv['action'] = 'toggle_push'
        g._kv['value'] = push
    g._kv['userguid'] = str(user.guid)

    db.session.commit()
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

    # for x in y: 
    favorite = UserFavorite(user.guid, 'author_id', 'active')
    db.session.add(favorite)
    db.session.commit()

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
    response.headers['epoch_ts'] = int(time.time()*1000.0)
    app.logger.info(json.dumps(g._kv))
    return response


if __name__ == '__main__':
    app.run(host="0.0.0.0")
