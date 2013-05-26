#! /usr/bin/env python
"""
Calculate statistics for each user, and print results to a tsv.

Primarily uses functions from the UserStats class in the MapGardening module.
"""
import MapGardening
from MapGardening import UserStats
import time
import optparse


usage = "usage: %prog [options]"
p = optparse.OptionParser(usage)
p.add_option('--type', '-t',
             default="raster",
             help="type of analysis, 'raster' or 'proximity' (or 'all' for all types)"
             )
p.add_option('--resolution', '-r',
             default="all",
             help="analysis resolution in metres (or 'all' for all resolutions)"
             )
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

# TODO: query the BlankSpotTableManager to see which types are present 
possible_types = [
                  'raster',
                  'proximity',
                  ]

if options.type == "all":
    runtypes = possible_types
else:
    runtypes = [options.type]
    
# TODO: query the BlankSpotTableManager to see which resolutions are present 
possible_resolutions = [
                        '250',
                        '500',
                        '1000',
                        ]

if options.resolution == "all":
    resolutions = possible_resolutions
else:
    resolutions = [options.resolution]
    

MapGardening.init_logging()

for placename in places.keys():

    # Each place exists in a different database, so we connect/disconnect inside the places loop    
    (conn, cur) = MapGardening.init_db(places[placename]['dbname'])
    
    bstm = MapGardening.BlankSpotTableManager()

    nt = MapGardening.NodeTable() # Using defaults for table name and projection
    
    for runtype in runtypes:
        
        for resolution in resolutions:
    
            st = time.time()
            lt = st
            
            print "starting", placename, resolution, runtype

            params = {
                      'runtype': runtype,
                      'resolution': resolution
                      }
            
            # Only use the most recent table
            blankspottable = bstm.get_existing_blankspot_tables(params)[0]
            
            print "using table", blankspottable.getTableName()
            
            us = UserStats.UserStats(conn, cur, nt, blankspottable)
            
            us.utc_offset = places[placename]['utc_offset']
               
            us.drop_userstats_table()
            us.create_userstats_table()
               
            us.add_userstats_v1edits() 
            us.add_userstats_blankedits() 
        
            us.add_userstats_firstedit()
            us.add_userstats_firstedit_v1()
            us.add_userstats_firstedit_blank()
            
            userdates = us.get_dates_and_edit_counts() 
            us.add_userstats_days_active(userdates) 
            us.add_userstats_mean_date(weighted=False, user_date_dict=userdates)
            us.add_userstats_mean_date(weighted=True, user_date_dict=userdates)
        
            us.print_userstats("outputv4_" + placename + "_" + params['runtype'] + "_" + params['resolution'] + "m.tsv")
                    
            us.print_placestats("output_totals_" + placename + "_" + params['runtype'] + "_" + params['resolution'] + "m.tsv")
                     
            now = time.time()
            print "finished. time elapsed: {:.0f} sec, {:.0f} sec total".format(now - lt, now - st)
            lt = now
        
        # end for resolutions
        
    # end for runtypes
    
    MapGardening.disconnect_db() # Disconnect from this place, ready to connect to next place
    
