#! /usr/bin/env python
"""
Calculate statistics for each study area, and prints results to stdout.

All it prints is the number of blankspots, the number of v1 nodes, 
and the number of total nodes. Since I am no longer storing the blankspot
information in the hist_point table itself, these stats are no longer very informative.

Currently, user_analysis.py does what this script used to do. It prints the "output_totals_*"
files which contain the stats for each study area by date.
"""

import MapGardening
import optparse

usage = "usage: %prog [options]"
p = optparse.OptionParser(usage)
p.add_option('--place', '-p',
             default="all"
             )

options, arguments = p.parse_args()


possible_tables = [
                   'blankspots_1000_b',
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