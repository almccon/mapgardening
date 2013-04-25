"""
Functions to calculate stats for each OSM contributor
"""
import MapGardening
import logging
from datetime import datetime, timedelta
import numpy

userstatstable = "usercounts"

class UserStats(object):
    
    conn = None
    cur = None
    utc_offset = 0
    nodetableobj = None
    blankspottableobj = None
    
    def __init__(self, connection, cursor, nodetableobj, blankspottableobj):
        """
        Initialize
        """
        self.conn = connection
        self.cur = cursor
        self.nodetableobj = nodetableobj
        self.blankspottableobj = blankspottableobj
        
    def drop_userstats_table(self):
        """
        Drop the userstats table.
        """
        
        querystring = "DROP TABLE IF EXISTS " + userstatstable 
        try:
            self.cur.execute(querystring)
        except Exception, inst:
            if str(inst).find("does not exist") != -1:
                # if exception is because table does not exist, do nothing
                pass
            else:
                logging.error("can't drop userstats table")
                logging.error(inst)
        self.conn.commit()
        
    def create_userstats_table(self):
        """
        Create a table called userstats in the currently connected database
        TODO: check whether table exists
        
        Populates table with uid, username, and count of number of times username
        was mentioned in the node table. (This is the number of edits the user is
        responsible for)
        """
        
        querystring = "CREATE TABLE " + userstatstable + " AS SELECT uid, username, count(username) from " +\
            self.nodetableobj.getTableName() + " GROUP BY uid, username ORDER BY count DESC"
        try:
            self.cur.execute(querystring)
        except Exception, inst:
            logging.error("can't select username and count")
            logging.error(inst)
        self.conn.commit()
       
    def add_userstats_countedits(self, queryparam = "", newcolumn = "newcount"): 
        """
        Count number of edits per user, then add as new column to userstats table.
 
        By default, counts all the edits in the database (using an empty query parameter).
        To count v1 edits, use queryparam = "WHERE version=1".
        This function can also be called by a number of convenience functions that
        specify which type of edits to count (all, only v1, etc).
        """
        
        temptablename = userstatstable + "_temp" + newcolumn
        
        querystring = "CREATE TEMP TABLE " + temptablename + \
            " AS " + \
            "SELECT a.uid, a.username, count(a.uid) AS " + newcolumn + " " + \
            "FROM " + self.nodetableobj.getTableName() + " a " + \
            "LEFT JOIN " + self.blankspottableobj.getTableName() + " b " + \
            "ON a.id = b.node_id " + queryparam + " " + \
            "GROUP BY a.uid, a.username ORDER BY " + newcolumn + " DESC"  
        try:
            self.cur.execute(querystring)
        except Exception, inst:
            self.conn.rollback()
            if str(inst).find("already exists") != -1:
                self.cur.execute("DROP TABLE " + temptablename) # drop the old table
                self.conn.commit()
                self.cur.execute(querystring) # and create a new one
                self.conn.commit()
            else:
                logging.error("can't create temp table")
                logging.error(inst)
        self.conn.commit()
        
        querystring = "ALTER TABLE " + userstatstable + " ADD " + newcolumn + " integer"
        try:
            self.cur.execute(querystring)
        except Exception, inst:
            self.conn.rollback()
            logging.warning("can't add new column")
            logging.warning(inst)
        self.conn.commit()
        
        querystring = "UPDATE " + userstatstable + " " + \
            "SET " + newcolumn + " = (" + \
            "SELECT " + newcolumn + " FROM " + \
            temptablename + " WHERE " + \
            temptablename + ".uid = " + userstatstable + ".uid)"  
        try:
            self.cur.execute(querystring)
        except Exception, inst:
            logging.error("can't update new column")
            logging.error(inst)
        self.conn.commit()
    
    def add_userstats_v1edits(self):
        """
        Count number of v1 edits (creation of nodes) by each user
        """ 
        return self.add_userstats_countedits("WHERE a.version=1", "v1count")
    
    def add_userstats_blankedits(self):
        """
        Count number of "blank spot" edits by each user
        """
        return self.add_userstats_countedits("WHERE a.version=1 AND b.blank=true", "blankcount")
    
    def add_userstats_firstedit(self, queryparam = "", newcolumn = "firstedit"):
        """
        Add date of each user's first edit (of any version)
        If their first edit was not v1
        """
        
        # Note: select "distinct on" is postgresql-specific.
        
        temptablename = userstatstable + "_temp" + newcolumn
        
        querystring = "CREATE TEMP TABLE " + temptablename + \
            " AS " + \
            "SELECT DISTINCT ON (a.username) a.username, a.valid_from AS " + newcolumn + " " + \
            "FROM " + self.nodetableobj.getTableName() + " a " + \
            "LEFT JOIN " + self.blankspottableobj.getTableName() + " b " + \
            "ON a.id = b.node_id " + queryparam + " " + \
            "ORDER BY a.username, a.valid_from ASC"
        try:
            self.cur.execute(querystring)
        except Exception, inst:
            self.conn.rollback()
            if str(inst).find("already exists") != -1:
                self.cur.execute("DROP TABLE " + temptablename) # drop the old table
                self.conn.commit()
                self.cur.execute(querystring) # and create a new one
                self.conn.commit()
            else:
                logging.error("can't create temp table")
                logging.error(inst)
        self.conn.commit()
        
        querystring = "ALTER TABLE " + userstatstable + " ADD " + newcolumn + " date"
        try:
            self.cur.execute(querystring)
        except Exception, inst:
            self.conn.rollback()
            logging.warning("can't add new column")
            logging.warning(inst)
        self.conn.commit()
       
        querystring = "UPDATE " + userstatstable + " " \
            "SET " + newcolumn + " = (" + \
            "SELECT " + newcolumn + " from " + \
            temptablename + " WHERE " + \
            temptablename + ".username = " + userstatstable + ".username)"
        try:
            self.cur.execute(querystring)
        except Exception, inst:
            logging.error("can't update new column")
            logging.error(inst)
        self.conn.commit()
       
    def add_userstats_firstedit_v1(self):
        """
        Add date of each user's first v1 edit... these are edits that
        create new features, not modify existing features.
        """
        
        return self.add_userstats_firstedit("WHERE a.version=1", "firsteditv1")
    
    def add_userstats_firstedit_blank(self):
        """
        Add date of each user's first blankspot edit... these are edits that
        create new features, in areas where no features previously existed
        """
        
        return self.add_userstats_firstedit("WHERE b.blank=true", "firsteditblank")

    def _days_since_epoch_obj(self, input_date_obj):
        """
        Given a date object, return number of days since epoch.
        This makes it easier to calculate the mean date of activity.
        """
        epoch = datetime.utcfromtimestamp(0)
        delta = input_date_obj - epoch
        return delta.days 
    
    def _days_since_epoch(self, input_date_str):
        """
        Given a date string of format YYYY-MM-DD return number od days since epoch.
        """
        date_obj = datetime.strptime(input_date_str, "%Y-%m-%d")
        return self._days_since_epoch_obj(date_obj)
    
    def _date_from_days_since_epoch(self, days_since_epoch_int):
        """
        Reverse the calculation from _days_since_epoch(). Given an integer
        representing the number of days since Jan 1, 1970, return a date object
        for that date.
        """
        epoch = datetime.utcfromtimestamp(0)
        delta = timedelta(days=days_since_epoch_int)
        date_obj = epoch + delta
        return date_obj
            
    def get_dates_and_edit_counts(self):
       
        print "gathering dates and edit counts" 
        user_date_dict = {}
        
        querystring = "SELECT username, valid_from, version, blank " + \
            "FROM " + self.nodetableobj.getTableName() 
        try:
            self.cur.execute(querystring)
        except Exception, inst:
            logging.error("can't select from nodes table")
            logging.error(inst)

        rows = self.cur.fetchall()
        
        if rows == None:
            return "" 
        
        for row in rows:
            (username, valid_from, version, blank) = row
            if not username in user_date_dict:
                user_date_dict[username] = {}

            # Shift utc datetimes to local time
            td = timedelta(hours=self.utc_offset)
            edit_dt = valid_from + td
            
            # Return a date object (drop time info) from the datetime object
            edit_date_str = str(edit_dt.date())
            
            if not edit_date_str in user_date_dict[username]:
                user_date_dict[username][edit_date_str] = {'all': 0, 'v1': 0, 'blank': 0}
                
            user_date_dict[username][edit_date_str]['all'] += 1
            if version == 1: 
                user_date_dict[username][edit_date_str]['v1'] += 1
            if blank == True: 
                user_date_dict[username][edit_date_str]['blank'] += 1
        return user_date_dict
        
    def add_userstats_mean_date(self, weighted=False, user_date_dict=None):
        """
        Of all the days the mapper is active, find the average (mean) date of activity
        """
        if user_date_dict == None:
            user_date_dict = self.get_dates_and_edit_counts()
        
        status = "calculating mean edit dates"
        
        newcolumn = "mean_date"
        if weighted == True:
            newcolumn = newcolumn + "_weighted"
            status += " (weighted)"
            
        print status
        
        querystring = "ALTER TABLE " + userstatstable + " ADD " + newcolumn + " date"
        try:
            self.cur.execute(querystring)
        except Exception, inst:
            self.conn.rollback()
            logging.warning("can't add new column")
            logging.warning(inst)
        self.conn.commit() 
        
        # Get keys for each user dict (list of dates)
        # convert keys to integers, find mean, convert back to date.    
        for username in user_date_dict:
            date_keys = user_date_dict[username].keys()
            if weighted:
                weights = []
                for dk in date_keys:
                    weights.append(user_date_dict[username][dk]['all'])
            else:
                weights = None
            list_of_dates = map(self._days_since_epoch, date_keys)
            mean_date = round(numpy.average(list_of_dates, None, weights))
            mean_date_dt = self._date_from_days_since_epoch(mean_date)
            querystring = "UPDATE " + userstatstable + " " + \
                "SET " + newcolumn + " = %s " + \
                "WHERE username = %s"
            try:
                self.cur.execute(querystring, (mean_date_dt, username))
            except Exception, inst:
                logging.error("can't update mean_date column")
                logging.error(inst)
        self.conn.commit()
    
    def add_userstats_days_active(self, user_date_dict=None):
        """
        Count the number of days (calendar days in each region's timezone) the mapper edited the db
        """
        if user_date_dict == None:
            user_date_dict = self.get_dates_and_edit_counts()
            
        print "counting days active"
            
        newcolumn = "days_active"
        
        querystring = "ALTER TABLE " + userstatstable + " ADD " + newcolumn + " integer"
        try:
            self.cur.execute(querystring)
        except Exception, inst:
            self.conn.rollback()
            logging.warning("can't add new column")
            logging.warning(inst)
        self.conn.commit()    
            
        for username in user_date_dict:
            days_active = len(user_date_dict[username])
            querystring = "UPDATE " + userstatstable + " " + \
                "SET " + newcolumn + " = %s " + \
                "WHERE username = %s"
            try:
                self.cur.execute(querystring, (days_active, username))
            except Exception, inst:
                logging.error("can't update days_active column")
                logging.error(inst)
        self.conn.commit()
      
    def print_userstats(self, filename):
        querystring = "SELECT uid, username, count, blankcount, v1count, firstedit, firsteditv1, firsteditblank, days_active, mean_date, mean_date_weighted FROM " + userstatstable
        try:
            self.cur.execute(querystring)
        except Exception, inst:
            logging.error("can't select count and blankcount")
            logging.error(inst)
       
        localfile = open(filename, "w")
         
        print >> localfile, "uid\tusername\tcount\tblankcount\tv1count\tfirstedit\tfirsteditv1\tfirsteditblank\tdays_active\tmean_date\tmean_date_weighted"
        
        rows = self.cur.fetchall()
        
        nullvalue = "NULL"
        
        for row in rows:
            # assign nullvalue instead of None
            uid = row[0] or nullvalue
            username = row[1] or nullvalue
            count = row[2] or 0
            blankcount = row[3] or 0
            v1count = row[4] or 0
            firstedit = row[5] or nullvalue
            firsteditv1 = row[6] or nullvalue
            firsteditblank = row[7] or nullvalue
            days_active = row[8] or 0
            mean_date = row[9] or nullvalue
            mean_date_weighted = row[10] or nullvalue
            print >> localfile, "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % (uid, username, count, blankcount, v1count, firstedit, firsteditv1, firsteditblank, days_active, mean_date, mean_date_weighted)
            
        localfile.close() 