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
    get_logs,
    active_nets,
    get_active_nets,
    all_nets,
    get_net,
    chart_operator_activity,
    )

import logging
log = logging.getLogger(__name__)

@view_defaults()
class ReportViews(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name="reports", renderer="reports/index.html")
    def reports(request):
        return dict()

    @view_config(route_name="chart_operator_activity", renderer="json")
    def chart_operator_activity(self):
        return chart_operator_activity()
