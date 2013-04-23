"""
A collection of functions and classes for the MapGardening analysis

Includes some global variables to manage the database connection
and containing some defaults.


"""
from __future__ import division
import sys
import os
import time
import datetime
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

distance = 100 # what are the units of the current projection, meters, right?

dbname = "osm-history-render-tirana"
user = "alan"
password = "blah"
host = "localhost"


conn = 0    # will be populated by init_db()
cur = 0     # will be populated by init_db()

# TODO: remove these globals, move them to a config file
# Note, they are also used in the UserStats module
global_nodetablename = "hist_point"
global_nodetableproj = 3857

default_rastertablename = "dummy_rast"
default_rasterid = 3

# A dict to store information about each case study area 
# Note: the utc_offset is for calculating the local time based on the 
# UTC timestamps in the database. This is a naive implementation of
# time zones that does not take into account DST. So, for much of the year
# these times will be off by one. However, this is good enough for the
# purposes of this analysis. Later, use the pytz module for more accuracy.
places = {
            'tirana': {
                        'dbname': "osm-history-render-tirana",
                        'rastertableproj': 32634, # WGS 84 / UTM zone 34N
                        'utc_offset': 1,
                       },
            'bayarea': {
                        'dbname': "osm-history-render-bayarea",
                        'rastertableproj': 26910,
                        'utc_offset': -8,
                       },
            'seattle': {
                        'dbname': "osm-history-render-seattle",
                        'rastertableproj': 26910,
                        'utc_offset': -8,
                       },
            'vancouver': {
                        'dbname': "osm-history-render-vancouver",
                        'rastertableproj': 26910,
                        'utc_offset': -8,
                       },
            'haiti': {
                        'dbname': "osm-history-render-haiti",
                        'rastertableproj': 32618, # WGS 84 / UTM zone 18N
                        'utc_offset': -5,
                       },
            'manchester': {
                        'dbname': "osm-history-render-manchester",
                        'rastertableproj': 32630, # WGS 84 / UTM zone 30N
                        'utc_offset': 0,
                       },
            'london': {
                        'dbname': "osm-history-render-london",
                        'rastertableproj': 32630, # WGS 84 / UTM zone 30N
                        'utc_offset': 0,
                       },
            'amsterdam': {
                        'dbname': "osm-history-render-amsterdam",
                        'rastertableproj': 32631, # WGS 84 / UTM zone 31N
                        'utc_offset': 1,
                       },
            'cairo': {
                        'dbname': "osm-history-render-cairo",
                        'rastertableproj': 32636, # WGS 84 / UTM zone 36N
                        'utc_offset': 2,
                       },
          }


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
    
def init_db(dbname_to_connect = dbname):
    global cur, conn
    
    dsn = "dbname='" + dbname_to_connect + "' user='" + user + "' password='" + password + "' host='" + host + "'"
    
    try:
        conn = psycopg2.connect(dsn)
    except Exception, inst:
        logging.error("Unable to connect to database")
        logging.error(inst)
        sys.exit()
    cur = conn.cursor()
    return (conn, cur)
    
def disconnect_db():
    global cur, conn
    
    cur.close()
    conn.close()
    
def get_place(placename):
    return places[placename]

def get_all_places():
    return places

class BlankSpotTable:
    """
    The database table storing whether a node was created in a blank spot or not
    
    Each BlankSpotTable object is unaware of any other tables or 
    BlankSpotTable objects. It is up to the BlankSpotTableManager 
    to keep track of these.
    
    Each BlankSpotTable object is also not necessarily aware of 
    which parameters it is associated with. Again, it is up to the 
    BlankSpotTableManager to keep track of the parameters. The
    BlankSpotTable object only needs to know the parameters when 
    creating a new table (to pick a reasonable table name)
    """
    
    _tablename = "blankspots"
    _params = {}
    
    def __init__(self, in_params):
        """Create an object that is not yet associated with a database table"""
        # TODO: sanity checks on incoming params
        self._params = in_params
        
        
    def create_new_table(self):
        """Create the table if it doesn't exist already"""
        self._tablename = self._tablename + "_" + self._params['runtype'] + "_" + str(int(self._params['resolution'])) + "_" + str(int(time.time())) 
       
        # TODO: handle exception if table exists 
        querystring = "CREATE TABLE \"" + self._tablename + "\" " + \
            "(node_id integer PRIMARY KEY, blank boolean)"
        try:
            cur.execute(querystring)
        except Exception, inst:
            logging.error("Unable to create blankspot table")
            logging.error(inst)
            conn.rollback()
            
    def connect_to_existing_table(self, tablename):
        """
        Connect to the given database table. Caller is responsible for 
        checking that this table was created for this object's parameters
        """
        self._tablename = tablename
        
        # TODO: confirm that the table exists. Raise exception otherwise.
            
    def get_tablename(self):
        return self._tablename
            
class BlankSpotTableManager:
    """
    Keep track of all the blankspot tables in the database
    """
    
    _manager_tablename = "blankspot_manager" 
    
    def __init__(self):
        """check if the manager table already exists. Else, throw error"""
        pass
    
    def create_manager_table(self, tablename=None): 
        """create the manager table already exists. Else, throw error"""
        if tablename:
            self._manager_tablename = tablename
        querystring = "CREATE TABLE \"" + self._manager_tablename + "\" " + \
            "(id SERIAL PRIMARY KEY, runtype char(16), resolution float, run_start timestamp, run_finish timestamp, tablename char(80))"
        try:
            cur.execute(querystring)
        except Exception, inst:
            logging.error("Unable to create blankspot manager table")
            logging.error(inst)
            conn.rollback()
    
    def create_new_blankspot_table(self, params):
        """create a new blankspot table for the given params"""
        blankspot_table_obj = BlankSpotTable(params)
        blankspot_table_obj.create_new_table()
        
        querystring = "INSERT INTO \"" + self._manager_tablename + "\" " + \
            "(runtype, resolution, run_start, tablename) " + \
            "VALUES (" + \
            "%s" + ", " + \
            "%s" + ", " + \
            "%s, " + \
            "'" + blankspot_table_obj.get_tablename() + "')"
        try:
            cur.execute(querystring, (params['runtype'], params['resolution'], datetime.datetime.now(),))
        except Exception, inst:
            conn.rollback()
            logging.error("can't insert blankspot record in manager table")
            logging.error(inst)
        conn.commit()
        
        return blankspot_table_obj
    
    def get_existing_blankspot_table(self, params):
        """
        return latest blankspot table for the given params.
        TODO: allow caller to specify a particular table, not just the latest one
        """
        querystring = "SELECT tablename FROM \"" + self._manager_tablename + "\" " + \
            "WHERE runtype = %s " + \
            "AND resolution = %s " + \
            "ORDER BY id DESC"
        try:
            cur.execute(querystring, (params['runtype'], params['resolution']))
        except Exception, inst:
            logging.error("can't select existing blankspot table from manager")
            logging.error(inst)
        
        rows = cur.fetchall()
        
        if len(rows) < 1:   
            return None
        tablename = rows[0][0]
        
        blankspot_table_obj = BlankSpotTable(params)
        try:
            blankspot_table_obj.connect_to_existing_table(tablename)
        except Exception, inst:
            logging.warning("blankspot table doesn't exist, returning None")
            logging.warning(inst)
            return None # or should I raise another exception?
        
        return blankspot_table_obj 
    
    def remove_blankspot_table(self, params):
        """Drop specified table(s)"""
        # TODO: add this!
        # Drop blankspot table
        # Remove entry from manager table
        pass
    
    def update_run_finish_time(self, tablename):
        """After finishing a blankspot run, update the time in the manager table"""
        querystring = "UPDATE \"" + self._manager_tablename + "\" SET run_finish = %s"
        try:
            cur.execute(querystring, (time.time(),))
        except Exception, inst:
            conn.rollback()
            logging.error("can't update run_finish in manager table")
            logging.error(inst)
        conn.commit()
        
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
        
    def analyze_nodes(self, set_nodes_individually_flag=False):
        """Select all OSM nodes that intersect this cell and set their blank/not-blank values"""
        
        temptablename = "temp_node_table" 
       
        querystring = "CREATE TEMP TABLE " + temptablename + " " + \
            "AS SELECT b.id, b.version, b.uid, b.username, b.valid_from " + \
            "FROM " + self.tablename + " a, " + global_nodetablename + " b " + \
            "WHERE a.rid = " + str(self.record_id) + " " + \
            "AND ST_Within(b.geom, ST_Transform(ST_PixelAsPolygon(a.rast, %s, %s), " + str(global_nodetableproj) + ")) " + \
            "AND b.version = 1 ORDER BY b.valid_from"
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
                    node_id = row[0]
                    list_of_nodes.append(node_id)
                    #print "node_id: %s, valid_from: %s" % (node_id, valid_from)
               
                # this needs to be stored as a tuple for the query to execute
                list_of_nodes_tuple = tuple(set(list_of_nodes)) 
                
                # For all nodes set blank = FALSE 
                querystring = "UPDATE " + global_nodetablename + " SET blank = FALSE WHERE id IN %s" 
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
            querystring = "UPDATE " + global_nodetablename + " SET blank = TRUE WHERE id = %s AND version = 1" 
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
    
    # end def analyze_nodes
        
    def analyze_nodes_and_preset_blanks(self):
        return self.analyze_nodes(True)
        
    
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
    
    def __init__(self, raster = default_rastertablename, rec = default_rasterid):
        self.tablename = raster
        self.record_id = rec
    
    def add_node_table(self, nodetableobj):
        self.nodetableobj = nodetableobj
        
    def create_db_raster(self, w, h, ulx, uly, s, p):
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
    
        querystring = "INSERT INTO " + self.tablename + " (rid, rast) " + \
            "VALUES (" + str(self.record_id) + ", ST_MakeEmptyRaster(%s,%s,%s,%s,%s,%s,0,0,%s))"
        try:
            cur.execute(querystring, (self.width, self.height, self.upperLeftX, self.upperLeftY, self.scale, self.scale, self.proj))
        except Exception, inst:
            conn.rollback()
            logging.error("can't insert raster record")
            logging.error(inst)
            sys.exit() 
        conn.commit()
        
        querystring = "UPDATE " + self.tablename + " SET rast = ST_AddBand(rast,'32BUI'::text,200) WHERE rid = " + str(self.record_id)
        try:
            cur.execute(querystring)
        except Exception, inst:
            conn.rollback()
            logging.error("can't add raster band")
            logging.error(inst)
            sys.exit() 
        conn.commit()
            
    def get_width(self, get_from_db=False):
        if not self.width or get_from_db:
            querystring = "SELECT ST_Width(rast) FROM " + self.tablename + " " + \
                "WHERE rid = " + str(self.record_id)
            try:
                cur.execute(querystring)
            except Exception, inst:
                logging.error("can't select raster width")
                logging.error(inst)
                sys.exit()
            self.width = cur.fetchone()[0]
        return self.width

    def get_width_from_db(self):
        return self.get_width(True)
    
    def get_height(self, get_from_db=False):
        if not self.height or get_from_db:
            querystring = "SELECT ST_Height(rast) FROM " + self.tablename  + " " + \
                "WHERE rid = " + str(self.record_id)
            try:
                cur.execute(querystring)
            except Exception, inst:
                logging.error("can't select raster height")
                logging.error(inst)
                sys.exit()
            self.height = cur.fetchone()[0]
        return self.height
    
    def get_height_from_db(self):
        return self.get_height(True)
    
    def get_raster_stats(self): 
        querystring = "SELECT rid, (foo.md).* FROM " + \
            "(SELECT rid, ST_MetaData(rast) AS md FROM dummy_rast) " + \
            "AS foo"
        try:
            cur.execute(querystring)
        except Exception, inst:
            logging.error("can't select raster metadata")
            logging.error(inst)
        rows = cur.fetchall()
        if len(rows) == 0:
            logging.error("found no rasters")
        else:
            print "found %s raster(s)" % len(rows)
            for row in rows:
                (rid, upperleftx, upperlefty, width, height, scalex, scaley, skewx, skewy, srid, numbands) = row
                print "rid: %s, upperleftx: %s, upperlefty: %s, width: %s, height: %s, scalex: %s, scaley: %s, skewx: %s, skewy: %s, srid: %s, numbands: %s" % (rid, upperleftx, upperlefty, width, height, scalex, scaley, skewx, skewy, srid, numbands) 
            
        #CONTINUE
        
    
    def get_cell(self, x, y):
        return Cell(self.tablename, self.record_id, x, y)
      
    def get_proj(self):
        # TODO: should query db if object doesn't know it
        return self.proj
    
    def find_expanded_bounds(self, xmin, ymin, xmax, ymax, rasterScale):
        """Expand bounds beyond input dimensions to result in rounded UTM coords"""
        self.scale = rasterScale
        self.upperLeftX = int(math.floor(xmin / rasterScale) * rasterScale)
        self.upperLeftY = int(math.floor(ymin / rasterScale) * rasterScale)
        self.width = int(((math.ceil(xmax / rasterScale) * rasterScale) - self.upperLeftX) / rasterScale)
        self.height = int(((math.ceil(ymax / rasterScale) * rasterScale) - self.upperLeftY) / rasterScale)
        return (self.upperLeftX, self.upperLeftY, self.width, self.height)
    
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
        querystring = "SELECT version from \"" + global_nodetablename + "\" WHERE id = %s ORDER BY version LIMIT 1"
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
            "FROM " + global_nodetablename + " a, " + global_nodetablename + " b "
            "WHERE a.id = %s "
            "AND b.valid_from < a.valid_from "
            "AND b.valid_to > a.valid_from "
            "AND ST_DWithin(a.geom, b.geom, %s) "
            "AND a.uid != b.uid"
        else:
            querystring = "SELECT b.id, b.version, b.uid, b.username "
            "FROM " + global_nodetablename + " a, " + global_nodetablename + " b "
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
        querystring = "UPDATE b SET blank = FALSE FROM \"" + global_nodetablename + "\" a, \"" + global_nodetablename + "\" b WHERE a.id = %s AND a.valid_from < b.valid_from AND a.valid_to > b.valid_from AND ST_DWithin(a.geom, b.geom, %s) AND a.uid != b.uid"
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
            querystring = "UPDATE \"" + global_nodetablename + "\" SET blank = TRUE WHERE version = 1 AND id = %s"
        else:
            querystring = "UPDATE \"" + global_nodetablename + "\" SET blank = FALSE WHERE version = 1 AND id = %s"
        try:
            cur.execute(querystring, (self.nodeid,))
        except Exception, inst:
            conn.rollback()
            logging.error("can't set blank for id %s", self.nodeid)
            logging.error(inst)
            sys.exit()
        conn.commit()

    def is_null_blankspot(self):
        querystring = "SELECT * FROM \"" + global_nodetablename + "\" WHERE version = 1 AND id = %s and blank IS NULL"
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
    
    def __init__(self, tablename=global_nodetablename, tableproj=3857):
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
        #querystring = "UPDATE \"" + self.nodetablename + "\" SET blank = " + arg
        querystring = "ALTER TABLE \"" + self.nodetablename + "\" DROP COLUMN blank"
        try:
            cur.execute(querystring)
        except Exception, inst:
            conn.rollback()
            logging.error("can't set all blank fields")
            logging.error(inst)
            sys.exit()
        conn.commit()
        print "done dropping old blank column. Creating new one..." 
        return self.create_blankspot_column()
    
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
    
    def get_blankspot_stats(self):
        """
        Count the number of blankspots and other nodes in this table.
        Print nothing but do not error if table does not exist.
        """
        querystring = "SELECT count(*) FROM " + self.nodetablename + " " + \
            "WHERE blank = 't'"
        try:
            cur.execute(querystring)
        except Exception, inst:
            logging.error("can't select count from node table")
            logging.error(inst)
            conn.rollback()
            return 1
        
        blankcount = cur.fetchone()[0]
        
        querystring = "SELECT count(*) FROM " + self.nodetablename + " " + \
            "WHERE version = 1"
        try:
            cur.execute(querystring)
        except Exception, inst:
            logging.error("can't select count from node table")
            logging.error(inst)
            conn.rollback()
            return 1
        
        v1count = cur.fetchone()[0]
        
        querystring = "SELECT count(*) FROM " + self.nodetablename 
        try:
            cur.execute(querystring)
        except Exception, inst:
            logging.error("can't select count from node table")
            logging.error(inst)
            conn.rollback()
            return 1
        
        editcount = cur.fetchone()[0]

        print "%s\t%s\t%s\t%s" % (self.nodetablename, blankcount, v1count, editcount)
        
    
# end class NodeTable
