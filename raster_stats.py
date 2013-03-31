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
    
for placename in places.keys():
    print "printing raster info for", placename
    
    MapGardening.init_logging()

    MapGardening.init_db(places[placename]['dbname'])
    
    raster = MapGardening.Raster()
    
    raster.get_raster_stats()

    