import datetime
import ipaddress

from db import LogData, CompanyNetwork, UserIP, UserClient
from db import get_db_session


class RiskService:

    def __init__(self, cache=None):
        self.cache = cache
        return

    def risk_isuserknown(self, username):
        usernames = []
        if self.cache:
            usernames = self.cache.get("usernames")

        if not usernames:
            usernames = []
            session = get_db_session()
            users = session.query(LogData.username).distinct().all()

            for user in users:
                usernames.append(user.username.lower())

            return username.lower() in usernames
        else:
            return username.lower() in usernames.keys()

    def risk_isipinternal(self, ip):
        ip = ipaddress.ip_address(ip)

        session = get_db_session()
        cn = session.query(CompanyNetwork).all()

        for c in cn:
            if ip in ipaddress.ip_network(c.range):
                return True

        return False

    def risk_isipknown(self, ip):
        ips = self.cache.get("ips")

        if not ips:
            ips = []
            session = get_db_session()
            userip = session.query(UserIP).all()

            for i in userip:
                ips.append(i.ip)

        return ip in ips

    def risk_isclientknown(self, client):
        clients = self.cache.get("clients")

        if not clients:
            clients = []
            session = get_db_session()
            userclient = session.query(UserClient).all()

            for i in userclient:
                clients.append(i.fingerPrint)

        return client in clients

    def risk_lastsuccessfullogindate(self, username):
        username = username.lower()
        usernames = self.cache.get("usernames")

        if not usernames:
            usernames = []
            session = get_db_session()
            lastsuccessfullogindate = session.query(LogData.logDate).filter_by(username=username,
                                                                               loginStatus=1).order_by(
                LogData.logDate.desc()).first()

            return datetime.datetime.fromtimestamp(
                lastsuccessfullogindate) if lastsuccessfullogindate else 'Not known'
        else:
            return datetime.datetime.fromtimestamp(usernames[username]['lastsuccessfullogindate']) if \
            usernames[username]['lastsuccessfullogindate'] else 'Not known'

    def risk_lastfailedlogindate(self, username):
        username = username.lower()
        usernames = self.cache.get("usernames")

        if not usernames:
            usernames = []
            session = get_db_session()
            lastfailedlogindate = session.query(LogData.logDate).filter_by(username=username, loginStatus=0).order_by(
                LogData.logDate.desc()).first()

            return datetime.datetime.fromtimestamp(lastfailedlogindate) if lastfailedlogindate else 'Not known'
        else:
            return datetime.datetime.fromtimestamp(usernames[username]['lastfailedlogindate']) if \
                usernames[username]['lastfailedlogindate'] else 'Not known'

    def risk_failedlogincountlastweek(self, current_week):

        stats = self.cache.get("stats")
        if stats and current_week in stats.keys():
            return stats[current_week]['failedlogincountlastweek']
        else:
            session = get_db_session()
            current_time = datetime.datetime.now()
            d1 = (current_time - datetime.timedelta(weeks=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            d2 = (current_time - datetime.timedelta(weeks=2)).replace(hour=0, minute=0, second=0, microsecond=0)

            c = session.query(LogData).filter(
                LogData.logDate >= d2.timestamp(), LogData.logDate <= d1.timestamp(), LogData.loginStatus == 0).count()

            self.cache.set("stats", {current_week: {'failedlogincountlastweek': c}})
            return c