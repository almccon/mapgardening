#! /usr/bin/env python

import MapGardening
import optparse
import time

usage = "usage: %prog [options]"
p = optparse.OptionParser(usage)
p.add_option('--type', '-t',
             default="raster",
             help="type of analysis, 'raster' or 'proximity'"
             )
p.add_option('--place', '-p',
             default="tirana"
             )

options, arguments = p.parse_args()

set_nodes_individually_flag = False
rasterScale = 250

place = MapGardening.get_place(options.place)

if place is not None:
                                                    
    print "starting with", options.place
        
    MapGardening.init_logging()

    MapGardening.init_db(place['dbname'])
    
    # apply to nodes table, ignore others for now. 
    
    nodetable = MapGardening.NodeTable()
    
    # TODO: test for spatial indexes before proceeding
    
    # Create column: blankspot
    # this will be for recording if the node was created in a blank spot on the map
    nodetable.create_blankspot_column()
    
    # By definition, any node of version > 1 is not in a blank spot
    ### Commented out for testing:
    ### nodetable.set_v2_blankspots()
    

    if set_nodes_individually_flag == False:    
        #nodetable.set_all_blankspots_true()
        #nodetable.set_all_blankspots_null()
        nodetable.set_all_blankspots_false()
    
    # If the data is an import, we don't care if it's in a blank spot or not
    # For now, we'll just set these all as not blank, but really I should have
    # another kind of flag there.
    # However, when doing the raster analysis I read the imports like every
    # other node, otherwise I would risk flagging a human's first node as blank
    # even if it occurred in an area that already had imported nodes
    
    #nodetable.set_import_blankspots("mbiker_imports_and_more")
    #nodetable.set_import_blankspots("pnorman_imports")

    do_raster_analysis = True

    if do_raster_analysis:
        print "doing raster analysis" 
        raster = MapGardening.Raster()
        
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
        
        st = time.time()
        lt = st
        inc = 0
        skipped = 0
        width = raster.get_width() 
        height = raster.get_height()
        count = width * height
        print "got %s cells (width: %s, height: %s)" % (count, width, height)
        try:
            for row in range(1, height):
                for column in range(1, width):
                    cell = raster.get_cell(column, row)
                    if set_nodes_individually_flag == False:    
                        cell.analyze_nodes()
                    else:
                        cell.analyze_nodes_and_preset_blanks()
                    # counter:
                
                    inc += 1      
                    if not inc % 10:
                        now = time.time()
                        print "done {}/{} ({:.2f}%), skipped {} ({:.2f}%) time elapsed: {:.0f} sec, {:.0f} sec total".format(inc, count, 100*inc/count, skipped, 100*skipped/count, now - lt, now - st)
                        lt = now
        
                # end loop
            # end loop
            
        except KeyboardInterrupt:
            print "KeyboardInterrupt caught"
            
    else:
        # Else, we do the node-to-node proximity test   

        
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
    print "place not found"
