import datetime
import ipaddress
from functools import wraps

import jwt
from flask import Flask
from flask import make_response, jsonify
from flask import request
from flask_caching import Cache
from werkzeug.security import check_password_hash

import db
from db import User, LogData, CompanyNetwork, UserIP, UserClient
from db import get_db_session
from services.appgatelog import AppGateLog

cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})

app = Flask(__name__)
app.config['SECRET_KEY'] = 'AppGateSecret7567**@$%^$&&^)*(*'

with app.app_context():
    db.init_app(app)
    cache.init_app(app)


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):

        token = None

        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(' ')[1]

        if not token:
            return jsonify({'message': 'a valid token is missing'})

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            session = get_db_session()
            current_user = session.query(User).filter_by(id=data['id']).first()
        except:
            return jsonify({'message': 'token is invalid'})

        return f(*args, **kwargs)

    return decorator


@app.route('/risk/isuserknown')
def risk_isuserknown():
    username = request.args.get('username').lower()
    usernames = cache.get("usernames")

    if not usernames:
        usernames = []
        session = get_db_session()
        users = session.query(LogData.username).distinct().all()

        for user in users:
            usernames.append(user.username.lower())

        return {
            "response": username.lower() in usernames
        }
    else:
        return {
            "response": username.lower() in usernames.keys()
        }


@app.route('/risk/isipinternal')
def risk_isipinternal():
    ip = ipaddress.ip_address(request.args.get('ip'))

    session = get_db_session()
    cn = session.query(CompanyNetwork).all()

    for c in cn:
        if ip in ipaddress.ip_network(c.range):
            return {
                "response": "true"
            }

    return {
        "response": "false"
    }


@app.route('/risk/isipknown')
def risk_isipknown():
    ip = request.args.get('ip')
    ips = cache.get("ips")

    if not ips:
        ips = []
        session = get_db_session()
        userip = session.query(UserIP).all()

        for i in userip:
            ips.append(i.ip)

    return {
        "response": ip in ips
    }


@app.route('/risk/isclientknown')
def risk_isclientknown():
    client = request.args.get('client')
    clients = cache.get("clients")

    if not clients:
        clients = []
        session = get_db_session()
        userclient = session.query(UserClient).all()

        for i in userclient:
            clients.append(i.fingerPrint)

    return {
        "response": client in clients
    }


@app.route('/risk/lastsuccessfullogindate')
def risk_lastsuccessfullogindate():
    username = request.args.get('username').lower()
    usernames = cache.get("usernames")

    if not usernames:
        usernames = []
        session = get_db_session()
        lastsuccessfullogindate = session.query(LogData.logDate).filter_by(username=username, loginStatus=1).order_by(
            LogData.logDate.desc()).first()

        return {
            "response": datetime.datetime.fromtimestamp(
                lastsuccessfullogindate) if lastsuccessfullogindate else 'Not known'
        }
    else:
        return {
            "response": datetime.datetime.fromtimestamp(usernames[username]['lastsuccessfullogindate']) if
            usernames[username]['lastsuccessfullogindate'] else 'Not known'
        }


@app.route('/risk/lastfailedlogindate')
def risk_lastfailedlogindate():
    username = request.args.get('username').lower()
    usernames = cache.get("usernames")

    if not usernames:
        usernames = []
        session = get_db_session()
        lastfailedlogindate = session.query(LogData.logDate).filter_by(username=username, loginStatus=0).order_by(
            LogData.logDate.desc()).first()

        return {
            "response": datetime.datetime.fromtimestamp(lastfailedlogindate) if lastfailedlogindate else 'Not known'
        }
    else:
        return {
            "response": datetime.datetime.fromtimestamp(usernames[username]['lastfailedlogindate']) if
            usernames[username]['lastfailedlogindate'] else 'Not known'
        }


@app.route('/risk/failedlogincountlastweek')
def risk_failedlogincountlastweek():

    week_number = datetime.datetime.now().isocalendar()[1]
    stats = cache.get("stats")
    if stats and week_number in stats.keys():
        return {
            "response": stats[week_number]['failedlogincount']
        }
    else:

        session = get_db_session()

        current_time = datetime.datetime.now()
        d1 = (current_time - datetime.timedelta(weeks=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        d2 = (current_time - datetime.timedelta(weeks=2)).replace(hour=0, minute=0, second=0, microsecond=0)

        c = session.query(LogData).filter(
            LogData.logDate >= d2.timestamp(), LogData.logDate <= d1.timestamp(), LogData.loginStatus == 0).count()

        cache.set("stats", {week_number: {'failedlogincount': c}})
        return {
                "response": c
            }


@app.route('/log', methods=['POST'])
def parse_log():
    lp = AppGateLog(request.get_json(), cache)
    lp.start()
    return {
        "response": "Log received and will be processed"
    }


@app.route('/users')
def list_users():
    session = get_db_session()
    users = session.query(User).all()
    result = []

    for user in users:
        user_data = {'username': user.username}
        result.append(user_data)

    return jsonify({'users': result})


@app.route('/logdata', methods=['GET'])
# @token_required
def log_data():
    session = get_db_session()
    logs = session.query(LogData).all()

    result = []
    for log in logs:
        log_data = {'source': log.source,
                    'username': log.username,
                    'ip': log.ip,
                    'fingerPrint': log.fingerPrint,
                    'loginStatus': log.loginStatus,
                    'createdDate': datetime.datetime.fromtimestamp(log.createdDate),
                    'logDate': datetime.datetime.fromtimestamp(log.logDate),
                    }
        result.append(log_data)

    return jsonify({'logs': result})


# Auth
@app.route('/login', methods=['GET', 'POST'])
def login_user():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify', 401, {'Error': 'Auth required"'})

    session = get_db_session()
    user = session.query(User).filter_by(username=auth.username).first()

    if check_password_hash(user.password, auth.password):
        token = jwt.encode(
            {'id': user.id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},
            app.config['SECRET_KEY'], algorithm="HS256")
        return jsonify({'token': token})

    return make_response('Could not verify', 401, {'Error': 'Auth required'})
