#! /usr/bin/env python

import MapGardening
import optparse

usage = "usage: %prog [options]"
p = optparse.OptionParser(usage)
p.add_option('--place', '-p',
             default="all"
             )

options, arguments = p.parse_args()


possible_tables = [
                   'hist_point',
                   'hist_point_250m',
                   'hist_point_500m',
                   'hist_point_1000m',
                   'hist_point_proximity',
                   ]

if options.place == "all":

    places = MapGardening.get_all_places()

else:
   
    placename = options.place 
    place = MapGardening.get_place(placename)
    places = {placename: place}
    
MapGardening.init_logging()

for placename in places.keys():
    print "printing blankspot info for", placename

    MapGardening.init_db(places[placename]['dbname'])
   
    for table in possible_tables: 
        nodetable = MapGardening.NodeTable(table) # Table may not exist, but object will still be created
        nodetable.get_blankspot_stats()

    MapGardening.disconnect_db()