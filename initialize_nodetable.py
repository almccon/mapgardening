#! /usr/bin/env python

import MapGardening
import optparse

usage = "usage: %prog [options]"
p = optparse.OptionParser(usage)
p.add_option('--place', '-p',
             default="all"
             )

options, arguments = p.parse_args()

if options.place == "all":

    places = MapGardening.get_all_places()

else:
   
    placename = options.place 
    place = MapGardening.get_place(placename)
    places = {placename: place}
    
MapGardening.init_logging()

for placename in places.keys():
    print "initializing node table for", placename

    MapGardening.init_db(places[placename]['dbname'])

    nodetable = MapGardening.NodeTable()

    if nodetable.initialize_rounded_coordinates(places[placename]['rastertableproj']):
	# if the function returns 1 it's an error
        print "initialize_rounded_coordinates failed"

    MapGardening.disconnect_db()
    
