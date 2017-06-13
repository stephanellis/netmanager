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
    subqueryload,
    joinedload
    )

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

import logging
log = logging.getLogger(__name__)

import bcrypt
from sqlalchemy.orm import class_mapper

import datetime
from pyramid.decorator import reify

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

def get_operator_lastlocation(operator_call):
    if operator_call is not None:
        results = DBSession.query(CheckIn).filter(CheckIn.operator_call==operator_call).order_by(desc(CheckIn.id)).all()
        for r in results:
            if r.location != "" and r.location is not None:
                return r.location
    return ""


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


class SNFeed(Base):
    __tablename__ = "snfeeds"

    name = Column(Text, primary_key=True)
    desc = Column(Text)
    nameslist = Column(Text)

def get_snfeed(name):
    try:
        return DBSession.query(SNFeed).get(name)
    except:
        return None

def all_snfeeds():
    return DBSession.query(SNFeed).all()

def add_snfeed(name, desc, nameslist):
    DBSession.add(SNFeed(name=name, desc=desc, nameslist=nameslist))

def pretty_time_delta(seconds):
    sign_string = '-' if seconds < 0 else ''
    seconds = abs(int(seconds))
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    if days > 0:
        return '%s%dd %dh %dm %ds' % (sign_string, days, hours, minutes, seconds)
    elif hours > 0:
        return '%s%dh %dm %ds' % (sign_string, hours, minutes, seconds)
    elif minutes > 0:
        return '%s%dm %ds' % (sign_string, minutes, seconds)
    else:
        return '%s%ds' % (sign_string, seconds)


class Net(Base):
    __tablename__ = "nets"

    id = Column(Integer, primary_key=True)
    desc = Column(Text)
    dt_create = Column(DateTime)
    dt_begin = Column(DateTime)
    dt_close = Column(DateTime)


    @reify
    def dtf_create(self):
        return self.dt_create.strftime("%Y-%m-%d %H:%M:%S")


    @reify
    def dtf_begin(self):
        return self.dt_begin.strftime("%Y-%m-%d %H:%M:%S")


    @reify
    def dtf_close(self):
        return self.dt_close.strftime("%Y-%m-%d %H:%M:%S")


    @reify
    def duration(self):
        if self.dt_begin:
            td = None
            if self.dt_close:
                td = self.dt_close - self.dt_begin
            else:
                td = datetime.datetime.now() - self.dt_begin
            #return "%s:%s:%s" % (td.hours, td.minutes, td.seconds)
            return pretty_time_delta(td.seconds)
        else:
            return "N/A"


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
    location = Column(Text)
    notes = Column(Text)
    acked = Column(Boolean, default=False)


    operator_call = Column(Text, ForeignKey("operators.call"))
    net_id = Column(Integer, ForeignKey("nets.id"))


    Operator = relationship("Operator", backref=backref("CheckIns"))
    Net = relationship("Net", backref=backref("CheckIns", order_by=desc(id)))


    @reify
    def dtf(self):
        return self.dt.strftime("%Y-%m-%d %H:%M:%S")


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
    return DBSession.query(Net).order_by(desc(Net.dt_create)).options(joinedload('CheckIns')).all()


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
