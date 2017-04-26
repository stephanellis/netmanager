#! /usr/bin/env python

import requests
import logging
import json
import sys
import csv

log = logging.getLogger(__name__)

gr_feed_preamble = """

Refresh: 1
Threshold: 999
Title: Spotter Network Positions - Filtered by Netmanager
Font: 1, 11, 0, "Courier New"
IconFile: 1, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/spotternet.png"
IconFile: 2, 15, 25, 8, 25, "http://www.spotternetwork.org/icon/arrows.png"
IconFile: 6, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/spotternet_new.png"

"""

def get_sngrfeedraw():
    log.debug("making the http request")
    r = requests.get("http://www.spotternetwork.org/feeds/gr.txt")
    if r.ok:
        log.debug("request was ok")
        return r.text
    else:
        log.debug("request failed")
        return ""

def parse_objectlines(olines):
    log.debug("parsing a set of object lines")
    #parse the individual lines of the object
    #build up a datastructure of the elements
    ds = dict()
    ds["origlines"] = olines

    # these keys are for the TruVu csv output
    ds["Temperature"] = ""
    ds["Weather"] = ""
    ds["Station Name"] = ""
    for l in olines:
        if l.startswith("Object:"):
            oparts = l.split(":")
            if len(oparts) == 2:
                llparts = oparts[1].split(",")
                if len(llparts) == 2:
                    ds['Latitude'] = float(llparts[0])
                    ds['Longitude'] = float(llparts[1])
        if l.startswith("Text:"):
            tparts = l.split(",")
            if len(tparts) == 4:
                ds["name"] = tparts[3].strip('"').lstrip(" ").lstrip("\"")
                ds["Station Name"] = ds["name"] # TruVu CSV output
    return ds

def parse_raw_feed(raw):
    lines = raw.split("\n")
    # build up chunks of the data structure, we need to takes lines between
    # object and end and pass those to the chunk parser
    objects = list()
    objectlines = list()
    have_object = False
    for l in lines:
        log.debug("line is: \"%s\"", l)
        log.debug("have_object var is %s", have_object)
        l = l.strip()
        if l.startswith("Object:"):
            log.debug("have an object now")
            have_object = True
        if have_object:
            log.debug("adding line to object")
            objectlines.append(l)
            if l.startswith("End"):
                log.debug("end of object")
                have_object = False
                objects.append(parse_objectlines(objectlines))
                objectlines = list()
    return objects

def filter_objects_byname(objects, namelist, translator=dict()):
    lower_names = [ x.lower() for x in namelist ]
    filtered = list()
    for o in objects:
        if o["name"].lower() in lower_names:
            if o["name"] in translator:
                o["name"] = translator[o["name"]]
            filtered.append(o)
    return filtered

def filtered_feed(names):
    objects = filter_objects_byname(parse_raw_feed(get_sngrfeedraw()), names)
    text = gr_feed_preamble
    for o in objects:
        for l in o['origlines']:
            text = text + l + "\n"
        text = text + "\n"
    return text

def truvu_csv(names, f=sys.stdout, translator=dict()):
    column_names = ["ID", "Station Name", "Latitude", "Longitude", "Temperature", "Weather"]
    writer = csv.DictWriter(f, fieldnames=column_names)

    rows = list()
    c = 0
    for o in filter_objects_byname(parse_raw_feed(get_sngrfeedraw()), names):
        del(o["origlines"])
        del(o["name"])
        if o["Station Name"] in translator:
            o["Station Name"] = translator[o["Station Name"]]
        c += 1
        o["ID"] = c
        writer.writerow(o)

def snfilter(names, translator=dict()):
    objects = parse_raw_feed(get_sngrfeedraw())
    filtered_objects = filter_objects_byname(objects, names, translator=translator)
    return filtered_objects

if __name__ == "__main__":
    log.setLevel(logging.INFO)
    fh = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    log.addHandler(fh)
    log.info("Filtering now...")
    #objects = parse_raw_feed(get_sngrfeedraw())
    names = ["w5zfq", "Daniel Shaw", "Ben Holcomb", "KF5UXA"]
    translations = dict(KF5UXA="Matt Dipirro")
    #filtered_objects = filter_objects_byname(objects, names)
    #print(filtered_feed(names))
    truvu_csv(names, translator=translations)
