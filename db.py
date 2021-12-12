import sqlalchemy.pool
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
# from flask import current_app
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash
from datetime import datetime

Base = declarative_base()
engine = create_engine('sqlite://',
                    connect_args = {'check_same_thread': False},
                    poolclass = sqlalchemy.pool.StaticPool)

Session = sessionmaker()
Session.configure(bind=engine)
session = Session()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)



class LogData(Base):
    __tablename__ = 'logdata'
    id = Column(Integer, primary_key=True)
    source = Column(String)
    username = Column(String)
    ip = Column(String)
    fingerPrint = Column(String)
    createdDate = Column(String)


class CompanyNetwork(Base):
    __tablename__ = 'companynetwork'
    id = Column(Integer, primary_key=True)
    range = Column(String)


class UserIP(Base):
    __tablename__ = 'userip'
    id = Column(Integer, primary_key=True)
    ip = Column(String)


class UserClient(Base):
    __tablename__ = 'userclient'
    id = Column(Integer, primary_key=True)
    fingerPrint = Column(String)


def get_db_session():
    return session
    #return engine


def init_db():
    Base.metadata.create_all(engine)

    user = User(username='UserA', password=generate_password_hash('1234', method='sha256'))
    session.add(user)

    userip = UserIP(ip='10.97.2.10')
    session.add(userip)

    ud = UserClient(fingerPrint='DefaultFingerPrint')
    session.add(ud)

    cn = CompanyNetwork(range='10.97.2.0/24')
    session.add(cn)

    cn = LogData(source='Computer', username='UserA', ip='10.97.2.10', fingerPrint='DefaultFingerPrint',
                 createdDate=datetime.now().timestamp())
    session.add(cn)

    session.commit()
    # with engine.connect() as c:
    #     with current_app.open_resource('schema.sql') as f:
    #         lines = f.readlines()
    #         for line in lines:
    #             c.execute(line.decode('utf8'))


def init_app(app):
    init_db()
