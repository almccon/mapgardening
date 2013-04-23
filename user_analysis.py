#! /usr/bin/env python

import MapGardening
from MapGardening import UserStats
import time
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
    
    st = time.time()
    lt = st
    
    print "starting", placename 
       
    (conn, cur) = MapGardening.init_db(places[placename]['dbname'])
    nt = MapGardening.NodeTable() # Using defaults
    us = UserStats.UserStats(conn, cur, nt)
    
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

    us.print_userstats("outputv3_" + placename + "_1000m.tsv")
            

             
    now = time.time()
    print "finished. time elapsed: {:.0f} sec, {:.0f} sec total".format(now - lt, now - st)
    lt = now
    
    
