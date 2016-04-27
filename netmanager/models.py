from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    Boolean,
    Enum,
    DateTime,
    ForeignKey,
    desc,
    and_,
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
    backref,
    )

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

import logging
log = logging.getLogger(__name__)

import bcrypt
from sqlalchemy.orm import class_mapper

import datetime


class ActivityLog(Base):
    __tablename__ = 'logs'

    id = Column(Integer, primary_key=True)
    dt = Column(DateTime)
    ip = Column(Text)
    msg = Column(Text)
    call = Column(Text, ForeignKey('operators.call'))

    Operator = relationship('Operator', backref=backref("ActivityLogs"))


class Operator(Base):
    __tablename__ = 'operators'

    # basic info
    call = Column(Text, primary_key=True)
    name = Column(Text)
    email = Column(Text)
    phone = Column(Text)

    # account stuff
    active = Column(Boolean, default=False)
    password = Column(Text)

    def set_password(self, ctext):
        self.password = bcrypt.hashpw(ctext.encode("utf-8"), bcrypt.gensalt())


    def check_password(self, ctext):
        if bcrypt.hashpw(ctext.encode("utf-8"), self.password) == self.password:
            return True
        else:
            return False


class Role(Base):
    __tablename__ = "roles"

    operator_call = Column(Text, ForeignKey("operators.call"), primary_key=True)
    role = Column(Enum("Super User","Net Manager","Net Control"), primary_key=True)

    Operator = relationship("Operator", backref=backref("Roles"))


class Freq(Base):
    __tablename__ = "freqs"

    name = Column(Text, primary_key=True)
    desc = Column(Text)
    freq = Column(Text)
    shift = Column(Enum(' ', '+', '-'))
    offset = Column(Text)
    tone = Column(Text)


class Net(Base):
    __tablename__ = "nets"

    id = Column(Integer, primary_key=True)
    desc = Column(Text)
    dt_create = Column(DateTime)
    dt_begin = Column(DateTime)
    dt_close = Column(DateTime)


    def count_checkins(self):
        return DBSession.query(CheckIn).filter(CheckIn.net_id==self.id).group_by(CheckIn.operator_call).count()


    def count_events(self):
        return DBSession.query(CheckIn).filter(CheckIn.net_id==self.id).count()


    def checkedin_operators(self):
        return DBSession.query(CheckIn).filter(CheckIn.net_id==self.id).group_by(CheckIn.operator_call).order_by(CheckIn.operator_call).all()


class Netfreqs(Base):
    __tablename__ = "netfreqs"

    net_id = Column(Integer, ForeignKey("nets.id"), primary_key=True)
    freq_name = Column(Text, ForeignKey("freqs.name"), primary_key=True)

    Net = relationship("Net", backref=backref("freqs"))
    Freq = relationship("Freq", backref=backref("Nets"))


class CheckIn(Base):
    __tablename__ = "checkins"

    id = Column(Integer, primary_key=True)
    dt = Column(DateTime)
    checkin_type = Column(Enum("CheckIn", "ReCheck", "CheckOut", "WXReport"), default="CheckIn")
    notes = Column(Text)
    acked = Column(Boolean, default=False)


    operator_call = Column(Text, ForeignKey("operators.call"))
    net_id = Column(Integer, ForeignKey("nets.id"))


    Operator = relationship("Operator", backref=backref("CheckIns"))
    Net = relationship("Net", backref=backref("CheckIns", order_by=desc(id)))


    def tclass(self):
        if self.acked:
            return ""
        else:
            return "warning"


def asdict(obj):
    return dict((col.name, str(getattr(obj, col.name)))
        for col in class_mapper(obj.__class__).mapped_table.c)


def get_operator(op_call):
    print("running db code")
    log.info("Looking up op_call %s" % op_call)
    return DBSession.query(Operator).get(op_call)


def all_operators():
    return DBSession.query(Operator).order_by(Operator.call).all()


def all_nets():
    return DBSession.query(Net).order_by(desc(Net.dt_create)).all()


def get_net(id):
    return DBSession.query(Net).get(id)


def get_checkin(id):
    return DBSession.query(CheckIn).get(id)


def alog(request, msg):
    l = ActivityLog()
    l.dt = datetime.datetime.now()
    l.ip = request.remote_addr
    l.msg = msg
    if request.operator:
        l.Operator = request.operator
    DBSession.add(l)


def get_logs():
    return DBSession.query(ActivityLog).order_by(desc(ActivityLog.id)).limit(50)


def active_nets():
    nets = DBSession.query(Net).filter(
        and_(
            Net.dt_begin!=None,
            Net.dt_close==None
            )).count()
    if nets > 0:
        return True
    else:
        return False


def get_active_nets():
    nets = DBSession.query(Net).filter(
        and_(
            Net.dt_begin!=None,
            Net.dt_close==None
            )).all()
    return nets
