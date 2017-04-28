from pyramid.response import Response
from pyramid.view import view_config, view_defaults

from sqlalchemy.exc import DBAPIError

from pyramid.httpexceptions import HTTPFound
from pyramid.security import Everyone, Authenticated

from .models import (
    get_snfeed,
    all_snfeeds,
    add_snfeed,
    DBSession,
    )

import logging
log = logging.getLogger(__name__)

from snfilter import output_json, output_truvu, output_gr, parse_nameslist, filter_feed
import requests

@view_config(route_name="snfilter", renderer="string")
def snfilter(request):
    name = request.matchdict["name"]
    outputformat = request.matchdict["outputformat"]
    snf = get_snfeed(name)
    f = get_snfeed(name)
    r = requests.get(request.registry.settings["snfilter.url"])
    if r.ok:
        names, xlator = parse_nameslist(snf.nameslist)
        ff = filter_feed(r.text, names, translator=xlator)
        if outputformat == "gr":
            return output_gr(ff, filtername=snf.desc)
        elif outputformat == "truvu":
            return output_truvu(ff)
        else:
            return output_json(ff, indent=2)

@view_defaults(permission=Authenticated)
class SNFilterList(object):
    def __init__(self, request):
        self.request = request
        if "name" in self.request.matchdict:
            self.name = self.request.matchdict["name"]
            self.snfeed = get_snfeed(self.name)

    @view_config(route_name="snfilterlist", renderer="snfilter/snfilterlist.html")
    def index(self):
        return dict(filteredfeeds=all_snfeeds())

    @view_config(route_name="snfilterlist_add")
    def add(self):
        name = self.request.params.get("name", "")
        desc = self.request.params.get("desc", "")
        nameslist = self.request.params.get("nameslist", "")
        if name is not "" and desc is not "" and nameslist is not "":
            if get_snfeed(name) is None:
                add_snfeed(name, desc, nameslist)
        return HTTPFound(self.request.route_url("snfilterlist"))

    @view_config(route_name="snfilterlist_save")
    def save(self):
        name = self.request.matchdict['name']
        snf = get_snfeed(name)
        if snf is not None:
            snf.desc = self.request.params.get("desc", "")
            snf.nameslist = self.request.params.get("nameslist", "")
        return HTTPFound(self.request.route_url("snfilterlist"))

    @view_config(route_name="snfilterlist_del")
    def remove(self):
        name = self.request.matchdict["name"]
        snf = get_snfeed(name)
        if snf is not None:
            DBSession.delete(snf)
        return HTTPFound(self.request.route_url("snfilterlist"))
