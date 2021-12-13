import sqlalchemy.pool
from sqlalchemy import Column, Integer, String
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
engine = create_engine('sqlite://',
                       connect_args={'check_same_thread': False},
                       poolclass=sqlalchemy.pool.StaticPool)

Session = sessionmaker()
Session.configure(bind=engine)
session = Session()


class LogData(Base):
    __tablename__ = 'logdata'
    id = Column(Integer, primary_key=True)
    source = Column(String)
    username = Column(String)
    ip = Column(String)
    fingerPrint = Column(String)
    loginStatus = Column(Integer)
    logDate = Column(Integer)
    createdDate = Column(Integer)


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


def init_db():
    Base.metadata.create_all(engine)

    userip = UserIP(ip='10.97.2.10')
    session.add(userip)

    ud = UserClient(fingerPrint='DefaultFingerPrint')
    session.add(ud)

    cn = CompanyNetwork(range='10.97.2.0/24')
    session.add(cn)

    # cn = LogData(source='Computer',
    #              username='UserA',
    #              ip='10.97.2.10',
    #              fingerPrint='DefaultFingerPrint',
    #              logDate=datetime(2020, 12, 1, 0, 0).timestamp(),
    #              createdDate=datetime.now().timestamp())
    # session.add(cn)

    session.commit()


def init_app(app):
    init_db()
