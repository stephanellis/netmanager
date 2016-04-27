from pyramid.response import Response
from pyramid.view import view_config, view_defaults

from sqlalchemy.exc import DBAPIError

from pyramid.httpexceptions import HTTPFound
from pyramid.security import Everyone, Authenticated

from .models import (
    DBSession,
    get_operator,
    asdict,
    alog,
    )

import logging
log = logging.getLogger(__name__)

from pyramid.security import Everyone, Authenticated


@view_defaults(permission=Authenticated)
class ViewSettings(object):
    """
    this is the settings view
    requires  authenticated operator
    """
    def __init__(self, request):
        self.request = request


    @view_config(route_name="settings_index", renderer="settings/index.html")
    def index(self):
        return dict()


    @view_config(route_name="settings_chpw")
    def chpw(self):
        pw1 = self.request.params.get("pw1", False)
        pw2 = self.request.params.get("pw2", False)
        if pw1 and pw2:
            if pw1 == pw2:
                self.request.operator.set_password(pw1)
                log.info("%s changed password" % self.request.operator.call)
                alog(self.request, "changed password")
            else:
                log.info("%s attempted to change password, but they did not match" % self.request.operator.call)
                alog(self.request, "attempted to change password, but they did not match")
        else:
            log.info("%s tried to change password, but the form was incomplete")
            alog(self.request, "attempt to change password, but form was not complete")
        return HTTPFound(self.request.route_url('settings_index'))


    @view_config(route_name="settings_basic")
    def basic(self):
        name = self.request.params.get("name", False)
        email = self.request.params.get("email", False)
        phone = self.request.params.get("phone", False)
        if name and email:
            self.request.operator.name = name
            self.request.operator.email = email
            self.request.operator.phone = phone
            log.info("%s updated basic info")
            alog(self.request, "updated basic info")
        else:
            log.info("%s tried to update settings, but the form was incomplete")
        return HTTPFound(self.request.route_url('settings_index'))

