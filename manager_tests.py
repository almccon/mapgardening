#! /usr/bin/env python

import MapGardening
import optparse

usage = "usage: %prog [options]"
p = optparse.OptionParser(usage)
p.add_option('--place', '-p',
             default="all"
             )
p.add_option('--type', '-t',
             default="raster",
             help="type of analysis, 'raster' or 'proximity' (or 'all' for all types)"
             )
p.add_option('--resolution', '-r',
             default="all",
             help="analysis resolution in metres (or 'all' for all resolutions)"
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
                        #'250',
                        #'500',
                        '1000',
                        ]

if options.resolution == "all":
    resolutions = possible_resolutions
else:
    resolutions = [options.resolution] 


MapGardening.init_logging()

for placename in places.keys():
    #print "testing BlankSpotTableManager for", placename
    print placename
    
    MapGardening.init_db(places[placename]['dbname'])

    bstm = MapGardening.BlankSpotTableManager()

    #print "creating manager table"
    #bstm.create_manager_table()
    
    for runtype in runtypes:
        
        for resolution in resolutions:
            
            params = {
                      'runtype': runtype,
                      'resolution': resolution
                      }

            #print "creating blankspot table"
            #bst_obj = bstm.create_new_blankspot_table({'runtype': "raster", 'resolution': 250})
            #print bst_obj.getTableName()
        
            #print "fetching existing blankspot table", params['resolution'], params['runtype']
            bst_objs = bstm.get_existing_blankspot_tables(params)
            if len(bst_objs) > 0:
                for bst_obj in bst_objs:
                    tablename = bst_obj.getTableName().strip()
                    blankcount = bst_obj.getBlankCount()
                    print '\t'.join((tablename, str(blankcount)))
                    if blankcount <= 0:
                        print "deleting", tablename
                        bstm.remove_blankspot_table(bst_obj)
            else:
                print "existing table not found for", params['resolution'], params['runtype']
            
        
        # end for resolutions
        
    # end for runtypes
        
    MapGardening.disconnect_db()
