from pyramid.response import Response
from pyramid.view import view_config, view_defaults

from sqlalchemy.exc import DBAPIError

from pyramid.httpexceptions import HTTPFound
from pyramid.security import Everyone, Authenticated

from .models import (
    DBSession,
    Operator,
    Net,
    CheckIn,
    get_operator,
    get_net,
    get_checkin,
    all_operators,
    all_nets,
    asdict,
    alog,
    )

import logging
log = logging.getLogger(__name__)

from pyramid.security import Everyone, Authenticated, Allow, Deny, DENY_ALL

import datetime

@view_defaults(permission=Authenticated)
class ViewNets(object):
    """
    this is the operators view
    requires  authenticated operator
    """
    def __init__(self, request):
        self.request = request


    @view_config(route_name="nets", renderer="nets/index.html")
    def index(self):
        nets = all_nets()
        return dict(nets=nets)


    @view_config(route_name="nets_begin")
    def nbegin(self):
        net = get_net(self.request.matchdict['id'])
        net.dt_begin = datetime.datetime.now()
        alog(self.request, "net %s begun" % net.desc)
        return HTTPFound(self.request.route_url('nets_console', id=net.id))


    @view_config(route_name="nets_close")
    def nclose(self):
        net = get_net(self.request.matchdict['id'])
        net.dt_close = datetime.datetime.now()
        alog(self.request, "net %s closed" % net.desc)
        return HTTPFound(self.request.route_url('nets_console', id=net.id))


    @view_config(route_name="nets_reopen")
    def nreopen(self):
        net = get_net(self.request.matchdict['id'])
        net.dt_close = None
        alog(self.request, "net %s reopened" % net.desc)
        return HTTPFound(self.request.route_url('nets_console', id=net.id))


    @view_config(route_name="nets_add")
    def add(self):
        desc = self.request.params.get("desc", False)
        if desc:
            n = Net(desc=desc, dt_create=datetime.datetime.now())
            DBSession.add(n)
        return HTTPFound(self.request.route_url("nets"))


    @view_config(route_name="nets_console", renderer="nets/console.html")
    def console(self):
        net = get_net(self.request.matchdict['id'])
        operators = all_operators()
        return dict(net=net, operators=operators)


    @view_config(route_name="nets_checkin")
    def checkin(self):
        net = get_net(self.request.matchdict['id'])
        if net is not None:
            call = self.request.params.get('call', False)
            ctype = self.request.params.get('type', False)
            notes = self.request.params.get('notes', False)

            if call and ctype:
                call = call.upper()
                operator = get_operator(call)
                if operator is None:
                    operator = Operator(call=call)
                    alog(self.request, "new operator created: %s" % operator.call)
                checkin = CheckIn(dt=datetime.datetime.now(), notes=notes, checkin_type=ctype)
                checkin.Operator = operator
                net.CheckIns.append(checkin)
                alog(self.request, "took checkin for %s type: %s notes: %s" % (operator.call, ctype, notes))
            return HTTPFound(self.request.route_url('nets_console', id=net.id))

        return HTTPFound(self.request.route_url('nets'))


    @view_config(route_name="nets_checkin_ack")
    def checkin_ack(self):
        c = get_checkin(self.request.matchdict['checkin_id'])
        net = get_net(self.request.matchdict['id'])
        if c is not None:
            c.acked = True
        return HTTPFound(self.request.route_url('nets_console', id=net.id))


    @view_config(route_name="nets_checkin_deack")
    def checkin_deack(self):
        c = get_checkin(self.request.matchdict['checkin_id'])
        net = get_net(self.request.matchdict['id'])
        if c is not None:
            c.acked = False
        return HTTPFound(self.request.route_url('nets_console', id=net.id))


    @view_config(route_name="nets_checkin_save")
    def checkin_save(self):
        c = get_checkin(self.request.matchdict['checkin_id'])
        net = get_net(self.request.matchdict['id'])
        if c is not None:
            c.notes = self.request.params.get("notes", "")
            alog(self.request, "saved checking for %s notes: %s" %(c.Operator.call, c.notes))
        return HTTPFound(self.request.route_url('nets_console', id=net.id))


    @view_config(route_name="nets_checkin_del")
    def checkin_del(self):
        c = get_checkin(self.request.matchdict['checkin_id'])
        net = get_net(self.request.matchdict['id'])
        if c is not None:
            DBSession.delete(c)
        return HTTPFound(self.request.route_url('nets_console', id=net.id))

