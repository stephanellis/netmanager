from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

from pyramid.httpexceptions import HTTPFound
from pyramid.security import Everyone, Authenticated

from .models import (
    DBSession,
    get_operator,
    asdict,
    alog,
    get_logs,
    active_nets,
    get_active_nets,
    all_nets,
    get_net,
    )

import logging
log = logging.getLogger(__name__)


@view_config(route_name='index', renderer='index.html')
def index(request):
    return dict(active_nets=active_nets(), nets=get_active_nets(), all_nets=all_nets())


@view_config(route_name='view_net', renderer='view_net.html')
def view_net(request):
    return dict(net=get_net(request.matchdict['id']))


@view_config(route_name='signin')
def signin(request):
    op_call = request.params.get("callsign", False)
    password = request.params.get("password", False)
    log.debug("signin attempt: %s / %i" % (op_call, len(password)))
    if op_call and password:
        op = get_operator(op_call.upper())
        if op is not None:
            if op.active:
                log.debug("operator account active")
                if op.check_password(password):
                    request.session['operator_call'] = op.call
                    log.info("successful signin for %s" % op.call)
                    alog(request, "signed in")
                else:
                    log.info("failed signin for %s bad password" % op.call)
            else:
                log.debug("operator account not active")
        else:
            log.debug("Lookup callsign failed.")
    else:
        log.info("signin form input was no complete")
    return HTTPFound(request.route_url('index'))


@view_config(route_name='signout')
def signout(request):
    if "operator_call" in request.session:
        alog(request, "signed out")
        del request.session["operator_call"]
    return HTTPFound(request.route_url('index'))


@view_config(route_name="activitylog", renderer="activitylog.html", permission=Authenticated)
def activitylog(request):
    return dict(logs=get_logs())
