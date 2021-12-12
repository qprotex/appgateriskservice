import datetime
import threading

from db import LogData, User, UserIP, UserClient
from db import get_db_session


class LogParser(threading.Thread):

    def __init__(self, data, cache):
        threading.Thread.__init__(self)
        self.data = data
        self.cache = cache
        return

    def run(self):

        cache_ips = self.cache.get("ips") if self.cache.get("ips") else []
        cache_clients = self.cache.get("clients") if self.cache.get("clients") else []
        cache_usernames = self.cache.get("usernames") if self.cache.get("usernames") else []

        # save data
        session = get_db_session()
        ld = LogData(source=self.data['source'],
                       username=self.data['username'],
                       ip=self.data['ip'],
                       fingerPrint=self.data['fingerPrint'],
                       createdDate=datetime.datetime.now().timestamp(),
                       )
        session.add(ld)

        # update db and cache
        if self.data['username'] not in cache_usernames:
            up = User(username=self.data['username'])
            session.add(up)
            cache_usernames.append(self.data['username'])
            self.cache.set("username", cache_usernames)

        if self.data['ip'] not in cache_ips:
            up = UserIP(ip=self.data['ip'])
            session.add(up)
            cache_ips.append(self.data['ip'])
            self.cache.set("ips", cache_ips)

        if self.data['fingerPrint'] not in cache_clients:
            up = UserClient(fingerPrint=self.data['fingerPrint'])
            session.add(up)
            cache_clients.append(self.data['fingerPrint'])
            self.cache.set("clients", cache_clients)

        session.commit()


