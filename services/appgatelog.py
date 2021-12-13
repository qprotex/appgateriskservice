import datetime
import threading

from db import LogData, UserIP, UserClient
from db import get_db_session
from services.logparser import LogParser, ssh_parser


class AppGateLog(threading.Thread):

    def __init__(self, data, cache):
        threading.Thread.__init__(self)
        self.data = data
        self.cache = cache
        return

    def run(self):

        cache_ips = self.cache.get("ips") if self.cache.get("ips") else []
        cache_clients = self.cache.get("clients") if self.cache.get("clients") else []
        cache_usernames = self.cache.get("usernames") if self.cache.get("usernames") else {}

        # save data
        session = get_db_session()

        for entry in self.data:

            # parse
            lp = None
            parsed_data = None
            if entry['source'] == 'ssh':
                lp = LogParser(ssh_parser)
                parsed_data = lp.execute(entry['message'])
            else:
                continue

            log_date = datetime.datetime.strptime(entry['logDate'], '%Y-%m-%d').timestamp()
            ld = LogData(source=entry['source'],
                         fingerPrint=entry['fingerPrint'],
                         logDate=log_date,
                         ip=parsed_data['ip'],
                         loginStatus=parsed_data['loginStatus'],
                         username=parsed_data['username'],
                         createdDate=datetime.datetime.now().timestamp(),
                         )
            session.add(ld)

            # update db and cache
            if parsed_data['username'] not in cache_usernames.keys():
                if parsed_data['loginStatus'] == 1:
                    cache_usernames[parsed_data['username']] = {"lastsuccessfullogindate": log_date, 'lastfailedlogindate': None}
                else:
                    cache_usernames[parsed_data['username']] = {"lastsuccessfullogindate": None, 'lastfailedlogindate': log_date}
            else:
                if parsed_data['loginStatus'] == 1:
                    cache_usernames[parsed_data['username']]["lastsuccessfullogindate"] = log_date
                else:
                    cache_usernames[parsed_data['username']]["lastfailedlogindate"] = log_date

            if parsed_data['ip'] not in cache_ips:
                up = UserIP(ip=parsed_data['ip'])
                session.add(up)
                cache_ips.append(parsed_data['ip'])

            if entry['fingerPrint'] not in cache_clients:
                up = UserClient(fingerPrint=entry['fingerPrint'])
                session.add(up)
                cache_clients.append(entry['fingerPrint'])

        self.cache.set("usernames", cache_usernames)
        self.cache.set("clients", cache_clients)
        self.cache.set("ips", cache_ips)

        session.commit()
