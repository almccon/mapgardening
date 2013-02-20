#! /usr/bin/env python
#$Id: proximity_check.py,v 1.7 2013/02/20 07:25:49 alan Exp alan $

from __future__ import division
import sys
import os
import time
import logging
import math


lib_dir = "/Users/alan/github/DYCAST/application/libs"

sys.path.append(lib_dir)            # the hard-coded library above
sys.path.append("libs")             # a library relative to current folder

sys.path.append(lib_dir+os.sep+"psycopg2")  # the hard-coded library above
sys.path.append("libs"+os.sep+"psycopg2")   # a library relative to current folder

try:
    import psycopg2
except ImportError:
    print "couldn't import psycopg2 library in path:", sys.path
    sys.exit()

loglevel = logging.DEBUG        # For debugging
#loglevel = logging.INFO         # appropriate for normal use
#loglevel = logging.WARNING      # appropriate for almost silent use

distance = 1000 # what are the units of the current projection, meters, right?

dbname = "osm-history-render-tirana"
user = "alan"
password = "blah"
host = "localhost"

dsn = "dbname='" + dbname + "' user='" + user + "' password='" + password + "' host='" + host + "'"

conn = 0    # will by populated by init_db()
cur = 0     # will by populated by init_db()

nodetablename = "hist_point"
nodetableproj = 3857
rastertablename = "dummy_rast"
rasterid = 3

## for tirana:
rastertableproj = 32634 # WGS 84 / UTM zone 34N

## for amsterdam:
#rastertableproj = 32631 # WGS 84 / UTM zone 31N

## for haiti:
#rastertableproj = 32618 # WGS 84 / UTM zone 18N

## for vancouver:
#rastertableproj = 26910 
#rasterWidth = 64
#rasterHeight = 52 
#rasterUpperLeftX = 478000
#rasterUpperLeftY = 5427000  # I think this is really the LowerLeftY... TODO: why is this?
rasterScale = 250

set_nodes_individually_flag = False

blankspottablename = "blankspots"

def init_logging():
    logging.basicConfig(format='%(asctime)s %(levelname)8s %(message)s',
        filename="/Users/alan/bin/osmproj/logfile.txt", filemode='a')
    logging.getLogger().setLevel(loglevel)

def debug(message):
    logging.debug(message)

def info(message):
    logging.info(message)

def warning(message):
    logging.warning(message)

def error(message):
    logging.error(message)
    
def init_db():
    global cur, conn
    try:
        conn = psycopg2.connect(dsn)
    except Exception, inst:
        logging.error("Unable to connect to database")
        logging.error(inst)
        sys.exit()
    cur = conn.cursor()

class BlankSpotTable:
    """
    The database table storing whether a node was create in a blank spot or not
    TODO: Still under construction
    """
    tablename = None
    
    def __init__(self, tablename=blankspottablename):
        """Create the table if it doesn't exist already"""
        querystring = "CREATE TABLE " + tablename + " " # ...continue here
        try:
            cur.execute(querystring)
        except Exception, inst:
            logging.error("Unable to create blankspot table")
            logging.error(inst)
            conn.rollback()

class Cell:
    """a raster cell"""
    tablename = None
    record_id = None
    x = None
    y = None
    
    def __init__(self, raster, rec, x, y):
        self.tablename = raster
        self.record_id = rec
        self.x = x
        self.y = y
        
    def analyze_nodes(self):
        """Select all OSM nodes that intersect this cell and set their blank/not-blank values"""
        
        temptablename = "temp_node_table" 
       
        querystring = "CREATE TEMP TABLE " + temptablename + " AS SELECT b.id, b.version, b.uid, b.username, b.valid_from FROM " + self.tablename + " a, " + nodetablename + " b WHERE a.rid = " + str(self.record_id) + " AND ST_Within(b.geom, ST_Transform(ST_PixelAsPolygon(a.rast, %s, %s), " + str(nodetableproj) + ")) AND b.version = 1 ORDER BY b.valid_from"
#        querystring = "CREATE TEMP TABLE " + temptablename + " " 
#        "AS SELECT b.id, b.version, b.uid, b.username "
#        "FROM" + self.rastertablename + " a, " + nodetablename + " b "
#        "WHERE ST_DWithin(ST_PixelAsPolygon(a, %s, %s), b.geom, %s)"
        try:
            cur.execute(querystring, (self.x, self.y))
        except Exception, inst:
            conn.rollback()
            if str(inst).find("already exists") != -1:
                cur.execute("DROP TABLE " + temptablename) # drop the old table
                conn.commit()
                cur.execute(querystring, (self.x, self.y)) # and create a new one
                conn.commit()
            else:
                logging.error("can't create table of intersecting nodes for cell %s, %s", self.x, self.y)
                logging.error(inst)
                sys.exit() 
        conn.commit()
            
        querystring = "SELECT * FROM " + temptablename + " ORDER BY valid_from"
        try:
            cur.execute(querystring)
        except Exception, inst:
            logging.error("can't select intersecting nodes for cell %s, %s", self.x, self.y)
            logging.error(inst)
            sys.exit() 
            
        rows = cur.fetchall()
        length = len(rows)
            
        print "Cell %s, %s got %s nodes" % (self.x, self.y, length)

        if length > 0:
                    
            earliest_id = rows[0][0]
             
            # If we have not wiped the True/Falseness of the blank tag before starting, 
            # then we have to individually set everything here.  
            
            if set_nodes_individually_flag == True: 
                list_of_nodes = [] # a list 
                for row in rows:
                    (id, version, uid, username, valid_from) = row
                    list_of_nodes.append(id)
                    #print "id: %s, valid_from: %s" % (id, valid_from)
               
                # this needs to be stored as a tuple for the query to execute
                list_of_nodes_tuple = tuple(set(list_of_nodes)) 
                
                # For all nodes set blank = FALSE 
                querystring = "UPDATE " + nodetablename + " SET blank = FALSE where id IN %s" 
                try:
                    cur.execute(querystring, (list_of_nodes_tuple,))
                except Exception, inst:
                    conn.rollback()
                    logging.error("can't set blank = FALSE")
                    logging.error(inst)
                    sys.exit()  
                conn.commit()
                
            # endif set_nodes_individually_flag == True
              
            print "updating node %s" % earliest_id
            
            # For the first node (and only the first node) set blank = TRUE 
            querystring = "UPDATE " + nodetablename + " SET blank = TRUE where id = %s AND version = 1" 
            try:
                cur.execute(querystring, (earliest_id,))
            except Exception, inst:
                conn.rollback()
                logging.error("can't set blank = TRUE")
                logging.error(inst)
                sys.exit()  
            conn.commit()
            
        # endif length > 0
            
        # Now just update the raster for visualization purposes
               
        querystring = "UPDATE " + self.tablename + " SET rast = ST_SetValue(" + self.tablename + ".rast, 1, %s, %s, %s) WHERE rid = " + str(self.record_id)
        try:
            cur.execute(querystring, (self.x, self.y, length))
        except Exception, inst:
            conn.rollback()
            logging.error("can't update raster cell %s, %s", self.x, self.y)
            logging.error(inst)
            sys.exit()  
        conn.commit()
    
# end class Cell

class Raster:
    """
    a raster used as an analysis grid. Assumes raster exists in database.
    
    Skew is always 0
    """
    tablename = None
    record_id = None
    width = None
    height = None
    upperLeftX = None
    upperLeftY = None
    scale = None    # scaleX and scaleY always the same
    proj = None
    nodetableobj = None
    
    def __init__(self, raster = rastertablename, rec = rasterid, proj = rastertableproj):
        self.tablename = raster
        self.record_id = rec
    
    def add_node_table(self, nodetableobj):
        self.nodetableobj = nodetableobj
        
    def create_db_raster(self, w, h, ulx, uly, s, p = rastertableproj):
        self.width = w
        self.height = h
        self.upperLeftX = ulx
        self.upperLeftY = uly
        self.scale = s
        self.proj = p
        
        #drop table
        #create table
        
        querystring = "DROP TABLE " + self.tablename # drop the old table
        try:
            cur.execute(querystring)
        except Exception, inst:
            conn.rollback()
            logging.error("can't drop raster table")
            logging.error(inst)
        conn.commit()
        
        querystring = "CREATE TABLE " + self.tablename + " (rid integer, rast raster)"
        try:
            cur.execute(querystring)
        except Exception, inst:
            conn.rollback()
            logging.error("can't create raster table")
            logging.error(inst)
            sys.exit() 
        conn.commit() 
    
        querystring = "INSERT INTO " + self.tablename + " (rid, rast) values (" + str(self.record_id) + ", ST_MakeEmptyRaster(%s,%s,%s,%s,%s,%s,0,0,%s))"
        try:
            cur.execute(querystring, (self.width, self.height, self.upperLeftX, self.upperLeftY, self.scale, self.scale, self.proj))
        except Exception, inst:
            conn.rollback()
            logging.error("can't insert raster record")
            logging.error(inst)
            sys.exit() 
        conn.commit()
        
        querystring = "update " + self.tablename + " SET rast = ST_AddBand(rast,'32BUI'::text,200) where rid = " + str(self.record_id)
        try:
            cur.execute(querystring)
        except Exception, inst:
            conn.rollback()
            logging.error("can't add raster band")
            logging.error(inst)
            sys.exit() 
        conn.commit()
            
    def get_width(self):
        if not self.width:
            querystring = "SELECT ST_Width(rast) FROM " + self.tablename + " WHERE rid = " + str(self.record_id)
            try:
                cur.execute(querystring)
            except Exception, inst:
                logging.error("can't select raster width")
                logging.error(inst)
                sys.exit()
            self.width = cur.fetchone()[0]
        return self.width
        
    def get_height(self):
        if not self.height:
            querystring = "SELECT ST_Height(rast) FROM " + self.tablename  + " WHERE rid = " + str(self.record_id)
            try:
                cur.execute(querystring)
            except Exception, inst:
                logging.error("can't select raster height")
                logging.error(inst)
                sys.exit()
            self.height = cur.fetchone()[0]
        return self.height
    
    def get_cell(self, x, y):
        return Cell(self.tablename, self.record_id, x, y)
      
    def get_proj(self):
        return self.proj
     
        
    
# end class Raster

class Node:
    """an OSM node in the database"""
    nodeid = None
    version = None
    userid = None
    username = None
    def __init__(self, nodeid=None, version=None, userid=None, username=None):
        self.nodeid = nodeid 
        self.version = version
        self.userid = userid
        self.username = username

    def highest_version(self):
        querystring = "SELECT version from \"" + nodetablename + "\" WHERE id = %s ORDER BY version LIMIT 1"
        try:
            cur.execute(querystring, (self.nodeid,))
        except Exception, inst:
            conn.rollback()
            logging.error("can't select highest version for node %s", self.nodeid)
            logging.error(inst)
            sys.exit()
        return cur.fetchone()

    def get_nearby_features(self, dist, is_past, return_node_obj=True):
        """ Get features around the given node, either in the past or the future, but not both
        # dist = distance for proximity test
        # is_past = True/False, for past/future
        # return_node_obj = True/False to return Node object, or just node id

        # Note, I am excluding any nodes that were created by the same user...
        # That's one way I can avoid catching other nodes that are part of the 
        # same changeset. (Don't seem to have changeset info in the db)
        """

        if is_past is True:
            querystring = "SELECT b.id, b.version, b.uid, b.username "
            "FROM " + nodetablename + " a, " + nodetablename + " b "
            "WHERE a.id = %s "
            "AND b.valid_from < a.valid_from "
            "AND b.valid_to > a.valid_from "
            "AND ST_DWithin(a.geom, b.geom, %s) "
            "AND a.uid != b.uid"
        else:
            querystring = "SELECT b.id, b.version, b.uid, b.username "
            "FROM " + nodetablename + " a, " + nodetablename + " b "
            "WHERE a.id = %s "
            "AND a.valid_from < b.valid_from "
            "AND a.valid_to > b.valid_from "
            "AND ST_DWithin(a.geom, b.geom, %s) "
            "AND a.uid != b.uid"

        try:
            cur.execute(querystring, (self.nodeid, distance))
        except Exception, inst:
            conn.rollback()
            logging.error("can't select nearby features for node %s", self.nodeid)
            logging.error(inst)
            sys.exit()
        closenodes = []
        for row in cur.fetchall():
            nodeid = row[0]
            version = row[1]
            userid = row[2]
            username = row[3]
            #print nodeid, " ", version 
            if return_node_obj:
                newnode = Node(nodeid, version, userid, username)
                closenodes.append(newnode)
            else:
                closenodes.append(nodeid)
        return closenodes

    def get_nearby_features_past(self, dist):
        #print "get_nearby_features_past"
        return self.get_nearby_features(dist, True, True)

    def get_nearby_nodeids_past(self, dist):
        #print "get_nearby_nodeids_past"
        return self.get_nearby_features(dist, True, False)

    def get_nearby_features_future(self, dist):
        #print "get_nearby_features_future"
        return self.get_nearby_features(dist, False, True)

    def get_nearby_nodeids_future(self, dist):
        #print "get_nearby_nodeids_future"
        return self.get_nearby_features(dist, False, False)

    def set_nearby_features_future_notblank(self, dist):
        #print "set_nearby_features_future_notblank"

        # this doesn't seem to work
        querystring = "UPDATE b SET blank = FALSE FROM \"" + nodetablename + "\" a, \"" + nodetablename + "\" b WHERE a.id = %s AND a.valid_from < b.valid_from AND a.valid_to > b.valid_from AND ST_DWithin(a.geom, b.geom, %s) AND a.uid != b.uid"
        try:
            cur.execute(querystring, (self.nodeid, distance))
        except Exception, inst:
            conn.rollback()
            logging.error("can't set blank in future for id %s", self.nodeid)
            logging.error(inst)
            sys.exit()
        conn.commit()

    def setblank(self, flag):
        if flag is True:
            querystring = "UPDATE \"" + nodetablename + "\" SET blank = TRUE WHERE version = 1 AND id = %s"
        else:
            querystring = "UPDATE \"" + nodetablename + "\" SET blank = FALSE WHERE version = 1 AND id = %s"
        try:
            cur.execute(querystring, (self.nodeid,))
        except Exception, inst:
            conn.rollback()
            logging.error("can't set blank for id %s", self.nodeid)
            logging.error(inst)
            sys.exit()
        conn.commit()

    def is_null_blankspot(self):
        querystring = "SELECT * FROM \"" + nodetablename + "\" WHERE version = 1 AND id = %s and blank IS NULL"
        try:
            cur.execute(querystring, (self.nodeid,))
        except Exception, inst:
            logging.error("can't check blank for id %s", self.nodeid)
            logging.error(inst)
            sys.exit()
        rows = cur.fetchall()
        if len(rows) > 0:
            #print "node %s is blank=null" % (self.nodeid)
            return True
        else:
            print "node %s is blank!=null" % (self.nodeid)
            return False
        
# end class Node      

class NodeTable:
    """
    The database table storing the OSM nodes.
    Uses same format as hist_point from osm-history-render
    but with added "blank" field for storing blank spot information
    """
    
    def __init__(self, tablename="hist_point", tableproj=3857):
        self.nodetablename = tablename
        self.nodetableproj = tableproj
        
    def set_multiple_nodes_notblank(self, list_of_nodeids):
    
        # this needs to be stored as a tuple for the query to execute
        list_of_nodes_tuple = tuple(set(list_of_nodeids))
    
        querystring = "UPDATE \"" + self.nodetablename + "\" SET blank = FALSE WHERE version = 1 AND id IN %s"
        try:
            cur.execute(querystring, (list_of_nodes_tuple,))
        except Exception, inst:
            conn.rollback()
            logging.error("problem setting blank for multiple nodes")
            logging.error(inst)
            sys.exit()
        conn.commit()
        
    def create_blankspot_column(self):
        querystring = "ALTER TABLE \"" + self.nodetablename + "\" ADD COLUMN blank boolean"
        try:
            cur.execute(querystring)
        except Exception, inst:
            conn.rollback()
            # If string includes "already exists"...
            if str(inst).find("already exists") != -1:
                print "blank column already exists, continuing..."
            else:
                print "couldn't create blank column, exiting..."
                sys.exit()
        conn.commit()
       
    def set_all_blankspots(self, arg):
        """For some analyses, we want everything set before we begin"""
        querystring = "UPDATE \"" + self.nodetablename + "\" SET blank = " + arg
        try:
            cur.execute(querystring)
        except Exception, inst:
            conn.rollback()
            logging.error("can't set all blank fields")
            logging.error(inst)
            sys.exit()
        conn.commit()
        print "done setting all blank fields..." 
    
    def set_all_blankspots_true(self):
        print "setting all blank fields true..." 
        return self.set_all_blankspots("TRUE")
    
    def set_all_blankspots_false(self):
        print "setting all blank fields false..." 
        return self.set_all_blankspots("FALSE")
    
    def set_all_blankspots_null(self):
        print "setting all blank fields null..." 
        return self.set_all_blankspots("NULL")
    
    def set_v2_blankspots(self):
        """For any node in the database that is v2 or greater, set blank = false"""
        
        print "setting v2 blankspots..." 
        querystring = "UPDATE \"" + self.nodetablename + "\" SET blank = FALSE WHERE version > 1"
        try:
            cur.execute(querystring)
        except Exception, inst:
            conn.rollback()
            logging.error("can't set blank = false for version > 1")
            logging.error(inst)
            sys.exit()
        conn.commit()
        print "done setting v2 blankspots..." 
        
    def set_import_blankspots(self, username):
        """For any node by an import user, set blank = false"""
        
        print "setting import blankspots for %s..." % username
        querystring = "UPDATE \"" + self.nodetablename + "\" SET blank = FALSE WHERE username = '" + username + "'"
        try:
            cur.execute(querystring)
        except Exception, inst:
            conn.rollback()
            logging.error("can't set blank = false for version > 1")
            logging.error(inst)
            sys.exit()
        conn.commit()
        print "done setting import blankspots..." 
            
    def get_null_blankspots(self):
        """By definition, any node of version > 1 is not in a blank spot"""
        
        print "getting null blankspots..."
    
        querystring = "SELECT id, uid, username from \"" + self.nodetablename + "\" WHERE version = 1 AND blank IS NULL"
        try:
            cur.execute(querystring)
        except Exception, inst:
            logging.error("can't select null blankspots")
            logging.error(inst)
            sys.exit()
        rows = cur.fetchall()
    
        nodes = []
    
        for row in rows:
            nodeid = row[0]
            userid = row[1]
            username = row[2]
            nodes.append(Node(nodeid, 1, userid, username))
    
        print "finished getting list of null blankspots..."
        return nodes
    
    def calculate_extent(self, toproj = None):
        """
        Find the extent of all the features in the db table.
        Transform to the given projection.
        """
        
        #print "calculating extent" 
        
        #querystring = "SELECT ST_AsText(ST_Transform(ST_SetSRID(ST_Extent(geom),%s),%s)) FROM " + table
   
        if toproj: 
            querystring = "SELECT \
                ST_XMin(ST_Transform(ST_SetSRID(ST_Extent(geom)," + str(self.nodetableproj) + ")," + str(toproj) + ")), \
                ST_YMin(ST_Transform(ST_SetSRID(ST_Extent(geom)," + str(self.nodetableproj) + ")," + str(toproj) + ")), \
                ST_XMax(ST_Transform(ST_SetSRID(ST_Extent(geom)," + str(self.nodetableproj) + ")," + str(toproj) + ")), \
                ST_YMax(ST_Transform(ST_SetSRID(ST_Extent(geom)," + str(self.nodetableproj) + ")," + str(toproj) + ")) \
                FROM " + self.nodetablename
        else:
            querystring = "SELECT \
                ST_XMin(ST_SetSRID(ST_Extent(geom)," + str(self.nodetableproj) + ")), \
                ST_YMin(ST_SetSRID(ST_Extent(geom)," + str(self.nodetableproj) + ")), \
                ST_XMax(ST_SetSRID(ST_Extent(geom)," + str(self.nodetableproj) + ")), \
                ST_YMax(ST_SetSRID(ST_Extent(geom)," + str(self.nodetableproj) + ")) \
                FROM " + self.nodetablename
            
        try:
            cur.execute(querystring)
        except Exception, inst:
            logging.error("can't select extent")
            logging.error(inst)
            sys.exit()
        
        (xmin, ymin, xmax, ymax) = cur.fetchone()
        return (xmin, ymin, xmax, ymax)
    
# end class NodeTable
        
def main():
    
    init_logging()

    init_db()
    
    # apply to nodes table, ignore others for now. 
    
    nodetable = NodeTable()
    
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
        raster = Raster()
        
        # To make the raster edges line up with round-number units in the UTM
        # projection, divide by the rasterScale before applying floor and ceil
        # 
        # So, if xmin is 478094.849660545 and rasterScale is 1000, the resulting 
        # value for rasterUpperLeftX should be 478000.
        
        (xmin, ymin, xmax, ymax) = nodetable.calculate_extent(raster.get_proj())
        #print (xmin, ymin, xmax, ymax) 
        rasterUpperLeftX = int(math.floor(xmin / rasterScale) * rasterScale)
        rasterUpperLeftY = int(math.floor(ymin / rasterScale) * rasterScale)
        rasterWidth = int(((math.ceil(xmax / rasterScale) * rasterScale) - rasterUpperLeftX) / rasterScale)
        rasterHeight = int(((math.ceil(ymax / rasterScale) * rasterScale) - rasterUpperLeftY) / rasterScale)
       
        #print (rasterUpperLeftX, rasterUpperLeftY, rasterWidth, rasterHeight) 
        raster.create_db_raster(rasterWidth, rasterHeight, rasterUpperLeftX, rasterUpperLeftY, rasterScale)
        
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
                    cell.analyze_nodes()
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
            
    # end if/else

if __name__ == "__main__":
    main()
