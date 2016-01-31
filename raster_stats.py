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
    print "printing raster info for", placename

    MapGardening.init_db(places[placename]['dbname'])

    bstm = MapGardening.BlankSpotTableManager()

    params = {
        'runtype': 'raster',
        'resolution': '1000'
    }

    # Only use the most recent table
    blankspottable = bstm.get_existing_blankspot_tables(params)[0]

    print "using table", blankspottable.getTableName()

    # Without passing any options, this looks for a raster with the default name, `dummy_rast`. 
    # That fails now, since I'm now using multiple rasters per place.
    # This needs to be initialized with the correct raster name. Looks like this is still wrong...
    # ...it's passing the blankspottable, not the raster name

    raster = MapGardening.Raster(blankspottable.getTableName())
    
    raster.get_raster_stats()

    MapGardening.disconnect_db()
