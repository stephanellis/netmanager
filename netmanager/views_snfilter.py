from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

from pyramid.httpexceptions import HTTPFound
from pyramid.security import Everyone, Authenticated

from .models import (
    get_snfeed
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
        names, xlator = parse_nameslist(snf.names)
        ff = filter_feed(r.text, names, translator=xlator)
        if outputformat == "gr":
            return output_gr(ff)
        elif outputformat == "truvu":
            return output_truvu(ff)
        else:
            return output_json(ff, indent=2)
