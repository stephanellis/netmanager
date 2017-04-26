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

from .snfilter import snfilter, gr_feed_preamble

def parse_names(names):
    nr = names.split(",")
    translator = dict()
    filter_names = list()
    for n in nr:
        nparts = n.split(":")
        if len(nparts) == 2:
            translator[nparts[0]] = nparts[1]
        filter_names.append(nparts[0])
    return filter_names, translator


def get_feed(names):
    names, translator = parse_names(names)
    return snfilter(names, translator=translator)

@view_config(route_name='snf_gr', renderer="gr.html")
def snf(request):
    request.response.content_type = "text/plain"
    name = request.matchdict['name']
    f = get_snfeed(name)
    objects = get_feed(f.names)
    return dict(name=name, p=gr_feed_preamble, objects=objects)
