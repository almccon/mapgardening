#! /usr/bin/env python

import MapGardening
import optparse
import time
import datetime
import sys

usage = "usage: %prog [options]"
p = optparse.OptionParser(usage)
p.add_option('--type', '-t',
             default="raster",
             help="type of analysis, 'raster' or 'proximity'"
             )
p.add_option('--place', '-p',
             default="tirana"
             )
p.add_option('--resolution', '-r',
             default=1000,
             help="analysis resolution in metres"
             )
p.add_option('--startx', '-x',
             default=1,
             help="starting raster x coord"
             )
p.add_option('--starty', '-y',
             default=1,
             help="starting raster y coord"
             )

options, arguments = p.parse_args()

resolution = options.resolution
runtype = options.type

if runtype not in ['raster', 'proximity']:
    print "type", runtype, "not recognized"
    sys.exit()

startx = int(options.startx)
starty = int(options.starty)    

place = MapGardening.get_place(options.place)

if place is not None:
                                                    
    print "starting with", options.place
        
    MapGardening.init_logging()

    MapGardening.init_db(place['dbname'])
    
    # analyze to nodes table, ignore others for now. 
    
    nodetable = MapGardening.NodeTable()
    
    # TODO: test for spatial indexes before proceeding
    
    bstm = MapGardening.BlankSpotTableManager() 
   
    # We assume the manager table exists. If not, create it. 
    #if not bstm.table_exists():
    #    bstm.create_manager_table()

    params = {
                'runtype': runtype,
                'resolution': resolution
              }
    blankspottable = bstm.create_new_blankspot_table(params)

    
    if params['runtype'] == "raster":
        print "doing raster analysis" 
        
        # Create semi-unique raster name to allow concurrent processing in same database
        raster = MapGardening.Raster("raster_" + str(int(time.time()))) 
        
        rasterScale = float(params['resolution'])
        
        # To make the raster edges line up with round-number units in the UTM
        # projection, divide by the rasterScale before applying floor and ceil
        # 
        # So, if xmin is 478094.849660545 and rasterScale is 1000, the resulting 
        # value for rasterUpperLeftX should be 478000.
        
        (xmin, ymin, xmax, ymax) = nodetable.calculate_extent(place['rastertableproj'])
        #print (xmin, ymin, xmax, ymax) 
        
        (rasterUpperLeftX, rasterUpperLeftY, rasterWidth, rasterHeight) = raster.find_expanded_bounds(xmin, ymin, xmax, ymax, rasterScale)
       
        #print (rasterUpperLeftX, rasterUpperLeftY, rasterWidth, rasterHeight) 
        raster.create_db_raster(rasterWidth, rasterHeight, rasterUpperLeftX, rasterUpperLeftY, rasterScale, place['rastertableproj'])
        
        raster.add_node_table(nodetable)
        raster.add_blankspot_table(blankspottable)
        
        st = time.time()
        lt = st
        inc = 0
        skipped = 0
        width = raster.get_width() 
        height = raster.get_height()
        count = width * height
        count_todo = count - (starty-1) * width - (startx-1)
        active = False
        print "got %s cells (width: %s, height: %s), %s to do" % (count, width, height, count_todo)
        try:
            for row in xrange(1, height+1):
                for column in xrange(1, width+1):
                    if not active:
                        if row == starty and column == startx:
                            active = True
                        else:
                            continue
                    cell = raster.get_cell(column, row)
                    cell.analyze_nodes()
                    # counter:
                
                    inc += 1      
                    if not inc % 10:
                        now = time.time()
                        print "done {}/{} ({:.2f}%), skipped {} ({:.2f}%) time elapsed: {:.0f} sec, {:.0f} sec total {}".format(inc, count_todo, 100*inc/count_todo, skipped, 100*skipped/count_todo, now - lt, now - st, time.ctime(int(now)))
                        lt = now
        
                # end loop
            # end loop
            
        except KeyboardInterrupt:
            print "KeyboardInterrupt caught"
            
        bstm.update_run_finish_time(blankspottable)
            
    elif params['runtype'] == "proximity":
        # Else, we do the node-to-node proximity test   
        
        # TODO: update this for the new separate-blankspot-table style
        print "WARNING: the proximity mode has not been updated for the new blankspot db style"
        
        # select where blankspot = null (meaning we haven't checked it yet)
        # results in list of nodes to test. (order by... what?)
        nodelist = nodetable.get_null_blankspots()  # how should this be ordered?
        
        if not nodelist:
            print "no nodes returned"
            sys.exit()
        
        st = time.time()
        lt = st
        inc = 0
        skipped = 0
        length = len(nodelist)
        
        print "entering loop"
        try:
            for testnode in nodelist:
        
                # First, test if node is (still) null, since I am updating as I go
                if testnode.is_null_blankspot():
            
                    nearbylistpast = testnode.get_nearby_features_past(distance)
            
                    nearbycount = len(nearbylistpast)
            
                    if nearbycount > 0:
                        #print "node %s found %s nearby" % (testnode.nodeid, nearbycount)
                        #for nearnode in nearbylistpast:
                            #print nearnode.nodeid
                        testnode.setblank(False)    
                        
                    else:
                        #print "node %s found no nearby (earlier) nodes" % (testnode.nodeid)
                        testnode.setblank(True)    
                
                
                    nearbylistfuture = testnode.get_nearby_nodeids_future(distance)
                
                    nearbycountfuture = len(nearbylistfuture)
                
                    if nearbycountfuture > 0:
                        #print "node %s found %s future nodes nearby" % (testnode.nodeid, nearbycountfuture)
                        nodetable.set_multiple_nodes_notblank(nearbylistfuture)
                
                    else:
                        #print "node %s found no future nodes nearby" % (testnode.nodeid)
                        pass
        
                    print "node {} {:<16} found {:>4} past and {:>4} future nodes nearby".format(testnode.nodeid, testnode.username, nearbycount, nearbycountfuture)
                
                
                    # optional:
                        # store date and time we last populated blankspot (Will this be useful? In case I want to change my algorithm and re-run parts?) Maybe this can wait 
            
                else: # Node is not null
                    skipped += 1
                
                # counter:
            
                inc += 1      
                if not inc % 10:
                    now = time.time()
                    print "done {}/{} ({:.2f}%), skipped {} ({:.2f}%) time elapsed: {:.0f} sec, {:.0f} sec total".format(inc, length, 100*inc/length, skipped, 100*skipped/length, now - lt, now - st)
                    lt = now
        
        except KeyboardInterrupt:
            print "KeyboardInterrupt caught"
    
    else:
        print "type", runtype, "not recognized"

else:
    print "place not found"
