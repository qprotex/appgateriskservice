import datetime

from flask import Flask
from flask import jsonify
from flask import request
from flask_caching import Cache

import db
from db import LogData
from db import get_db_session
from services.appgatelog import AppGateLog
from services.riskservice import RiskService

cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})

app = Flask(__name__)

with app.app_context():
    db.init_app(app)
    cache.init_app(app)

rs = RiskService(cache)


@app.route('/risk/isuserknown')
def risk_isuserknown():
    username = request.args.get('username').lower()
    r = rs.risk_isuserknown(username)
    return {
        "response": r
    }


@app.route('/risk/isipinternal')
def risk_isipinternal():
    ip = request.args.get('ip')
    r = rs.risk_isipinternal(ip)
    return {
        "response": r
    }


@app.route('/risk/isipknown')
def risk_isipknown():
    ip = request.args.get('ip')
    r = rs.risk_isipknown(ip)
    return {
        "response": r
    }


@app.route('/risk/isclientknown')
def risk_isclientknown():
    client = request.args.get('client')
    r = rs.risk_isclientknown(client)
    return {
        "response": r
    }


@app.route('/risk/lastsuccessfullogindate')
def risk_lastsuccessfullogindate():
    username = request.args.get('username')
    r = rs.risk_lastsuccessfullogindate(username)
    return {
        "response": r
    }


@app.route('/risk/lastfailedlogindate')
def risk_lastfailedlogindate():
    username = request.args.get('username')
    r = rs.risk_lastfailedlogindate(username)
    return {
        "response": r
    }


@app.route('/risk/failedlogincountlastweek')
def risk_failedlogincountlastweek():
    current_week = datetime.datetime.now().isocalendar()[1]
    r = rs.risk_failedlogincountlastweek(current_week)
    return {
        "response": r
    }


@app.route('/log', methods=['POST'])
def parse_log():
    lp = AppGateLog(request.get_json(), cache)
    lp.start()
    return {
        "response": "Log received and will be processed"
    }


@app.route('/logdata', methods=['GET'])
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
