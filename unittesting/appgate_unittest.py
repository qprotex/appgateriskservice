import datetime
import json
import time
import unittest

from flask import Flask
from flask_caching import Cache

import db
from services.riskservice import RiskService


class AppGateUnitTest(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})
        app = Flask(__name__)
        with app.app_context():
            db.init_app(app)
            cache.init_app(app)

        self.rs = RiskService(cache)

        with open('log.txt', 'r') as content_file:
            content = content_file.read()

        self.rs.parse_log(json.loads(content))
        time.sleep(1)

    def test_risk_isuserknown_valid(self):
        r = self.rs.risk_isuserknown('UserA')
        self.assertTrue(r)

    def test_risk_isuserknown_invalid(self):
        r = self.rs.risk_isuserknown('UserB')
        self.assertFalse(r)

    def test_risk_isipinternal_valid(self):
        r = self.rs.risk_isipinternal('10.97.2.15')
        self.assertTrue(r)

    def test_risk_isipinternal_invalid(self):
        r = self.rs.risk_isipinternal('10.97.3.15')
        self.assertFalse(r)

    def test_risk_isipknown_valid(self):
        r = self.rs.risk_isipknown('10.97.2.10')
        self.assertTrue(r)

    def test_risk_isipknown_invalid(self):
        r = self.rs.risk_isipknown('10.97.3.15')
        self.assertFalse(r)

    def test_risk_isclientknown_valid(self):
        r = self.rs.risk_isclientknown('12:f8:7e:78:61:b4:bf:e2:de:24:15:96:4e:d4:72:53')
        self.assertTrue(r)

    def test_risk_isclientknown_invalid(self):
        r = self.rs.risk_isclientknown('11:f8:7e:78:61:b4:bf:e2:de:24:15:96:4e:d4:72:52')
        self.assertFalse(r)

    def test_risk_lastsuccessfullogindate(self):
        r = self.rs.risk_lastsuccessfullogindate('UserA')
        self.assertEqual(r, datetime.datetime(2021, 12, 10, 0, 0))

    def test_risk_lastfailedlogindate(self):
        r = self.rs.risk_lastfailedlogindate('Miguel')
        self.assertEqual(r, datetime.datetime(2021, 12, 6, 0, 0))

    def test_risk_failedlogincountlastweek(self):
        current_week = datetime.datetime.now().isocalendar()[1]
        r = self.rs.risk_failedlogincountlastweek(current_week)
        self.assertEqual(r, 2)


if __name__ == '__main__':
    unittest.main()
