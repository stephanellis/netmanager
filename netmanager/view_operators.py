from pyramid.response import Response
from pyramid.view import view_config, view_defaults

from sqlalchemy.exc import DBAPIError

from pyramid.httpexceptions import HTTPFound
from pyramid.security import Everyone, Authenticated

from .models import (
    DBSession,
    Operator,
    get_operator,
    get_operator_lastlocation,
    all_operators,
    asdict,
    alog,
    )

import logging
log = logging.getLogger(__name__)

from pyramid.security import Everyone, Authenticated, Allow, Deny, DENY_ALL


@view_defaults(permission=Authenticated)
class ViewOperators(object):
    """
    this is the operators view
    requires  authenticated operator
    """
    def __init__(self, request):
        self.request = request
        if "call" in self.request.matchdict:
            self.operator_call = self.request.matchdict["call"].upper()
        else:
            self.operator_call = ""


    @view_config(route_name="operators", renderer="operators/operators_base.html")
    def index(self):
        return dict(operators=all_operators())

    @view_config(route_name="operators_lastlocation", renderer="string")
    def lastlocation(self):
        return "Last loc for %s" % get_operator_lastlocation(self.operator_call)

    @view_config(route_name="operators_add")
    def add(self):
        call = self.request.params.get("call", False)
        name = self.request.params.get("name", False)
        email = self.request.params.get("email", False)
        phone = self.request.params.get("phone", False)

        if call:
            o = Operator(call=call.upper(), name=name, email=email, phone=phone)
            DBSession.add(o)
            alog(self.request, "added operator %s" % o.call)
        else:
            log.info("%s tried to add an operator, but the form was not complete" % self.request.operator.call)
        return HTTPFound(self.request.route_url("operators"))


    @view_config(route_name="operators_edit", renderer="operators/edit.html")
    def edit(self):
        call = self.request.matchdict['call']
        o = get_operator(call)
        return dict(o=o)


    @view_config(route_name="operators_save")
    def save(self):
        call = self.request.matchdict['call']
        o = get_operator(call)
        name = self.request.params.get('name', False)
        email = self.request.params.get('email', False)
        phone = self.request.params.get('phone', False)
        active = self.request.params.get('active', False)
        password = self.request.params.get('password', False)
        o.name = name
        o.email = email
        o.phone = phone
        if active is not False:
            o.active = True
            alog(self.request, "activated account for %s" % o.call)
        else:
            o.active = False
            alog(self.request, "deactivated account for %s" % o.call)

        if password:
            o.set_password(password)
            alog(self.request, "set password for %s" % o.call)

        DBSession.add(o)
        alog(self.request, "saved info for %s" % o.call)
        return HTTPFound(self.request.route_url('operators_edit', call=call))


    @view_config(route_name="operators_del")
    def delete(self):
        call = self.request.matchdict['call']
        o = get_operator(call)
        DBSession.delete(o)
        alog(self.request, "deleted operator %s" % o.call)
        return HTTPFound(self.request.route_url('operators'))
