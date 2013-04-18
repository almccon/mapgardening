"""
Functions to calculate stats for each OSM contributor
"""
import MapGardening
import logging
from datetime import datetime, timedelta

userstatstable = "usercounts"

class UserStats(object):
    
    conn = None
    cur = None
    utc_offset = 0
    
    def __init__(self, connection, cursor):
        """
        Initialize
        """
        self.conn = connection
        self.cur = cursor
        
    def create_userstats_table(self):
        """
        Create a table called userstats in the currently connected database
        TODO: check whether table exists
        
        Populates table with uid, username, and count of number of times username
        was mentioned in the node table. (This is the number of edits the user is
        responsible for)
        """
        
        querystring = "CREATE TABLE " + userstatstable + " AS SELECT uid, username, count(username) from " +\
            MapGardening.global_nodetablename + " GROUP BY uid, username ORDER BY count DESC"
        try:
            self.cur.execute(querystring)
        except Exception, inst:
            logging.error("can't select username and count")
            logging.error(inst)
        self.conn.commit()
       
    def add_userstats_countedits(self, queryparam = "WHERE blank=true", newcolumn = "newcount"): 
        """
        Count number of edits per user, then add as new column to userstats table.
 
        By default, counts all the edits in the database (using an empty query parameter)
        This function can also be called by a number of convenience functions that
        specify which type of edits to count (all, only v1, only blanks, etc).
        """
        
        temptablename = userstatstable + "_temp" + newcolumn
        
        querystring = "CREATE TEMP TABLE " + temptablename + \
            " AS " + \
            "SELECT uid, username, count(uid) AS " + newcolumn + " FROM " + \
            MapGardening.global_nodetablename + " " + queryparam + " " + \
            "GROUP BY uid, username ORDER BY " + newcolumn + " DESC"  
        try:
            self.cur.execute(querystring)
        except Exception, inst:
            logging.error("can't create temp table")
            logging.error(inst)
        self.conn.commit()
        
        querystring = "ALTER TABLE " + userstatstable + " ADD " + newcolumn + " integer"
        try:
            self.cur.execute(querystring)
        except Exception, inst:
            logging.error("can't add new column")
            logging.error(inst)
        self.conn.commit()
        
        querystring = "UPDATE " + userstatstable + " " + \
            "SET " + newcolumn + " = (" + \
            "SELECT " + newcolumn + " from " + \
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
        return self.add_userstats_countedits("WHERE version=1", "v1count")
    
    def add_userstats_blankedits(self):
        """
        Count number of "blank spot" edits by each user
        """
        return self.add_userstats_countedits("WHERE blank=true", "blankcount")
    
    def add_userstats_firstedit(self, queryparam = "", newcolumn = "firstedit"):
        """
        Add date of each user's first edit (of any version)
        If their first edit was not v1
        """
        
        # Note: select "distinct on" is postgresql-specific.
        
        temptablename = userstatstable + "_temp" + newcolumn
        
        querystring = "CREATE TEMP TABLE " + temptablename + \
            " AS " + \
            "SELECT DISTINCT ON (username) username, valid_from " + \
            "FROM " + MapGardening.global_nodetablename + " " + queryparam + " " + \
            "ORDER BY username, valid_from ASC"
        try:
            self.cur.execute(querystring)
        except Exception, inst:
            logging.error("can't create temp table")
            logging.error(inst)
        self.conn.commit()
        
        querystring = "ALTER TABLE " + userstatstable + " ADD " + newcolumn + " date"
        try:
            self.cur.execute(querystring)
        except Exception, inst:
            logging.error("can't add new column")
            logging.error(inst)
        self.conn.commit()
        
        querystring = "UPDATE " + userstatstable + " " \
            "SET " + newcolumn + " = (" + \
            "SELECT " + newcolumn + " from " + \
            temptablename + " WHERE " + \
            temptablename + ".uid = " + userstatstable + ".uid)"  
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
        
        return self.add_userstats_firstedit("WHERE version=1", "firsteditv1")
    
    def add_userstats_firstedit_blank(self):
        """
        Add date of each user's first blankspot edit... these are edits that
        create new features, in areas where no features previously existed
        """
        
        return self.add_userstats_firstedit("WHERE blank=true", "firsteditblank")

    def _days_since_epoch(self, input_date_obj):
        """
        Given a date object, return number of days since epoch.
        This makes it easier to calculate the mean date of activity.
        """
        epoch = datetime.datetime.utcfromtimestamp(0)
        delta = input_date_obj - epoch
        return delta.days 
    
    def _date_from_days_since_epoch(self, days_since_epoch_int):
        """
        Reverse the calculation from _days_since_epoch(). Given an integer
        representing the number of days since Jan 1, 1970, return a date object
        for that date.
        """
        epoch = datetime.datetime.utcfromtimestamp(0)
        delta = timedelta(days=days_since_epoch_int)
        date_obj = epoch + delta
        return date_obj
            
    def get_dates_and_edit_counts(self):
       
        print "gathering dates and edit counts" 
        user_date_dict = {}
        
        querystring = "SELECT username, valid_from, version, blank " + \
            "FROM " + MapGardening.global_nodetablename 
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
        
    def add_userstats_mean_date(self, user_date_dict=None):
        """
        Of all the days the mapper is active, find the average (mean) date of activity
        """
        if user_date_dict == None:
            user_date_dict = self.get_dates_and_edit_counts()
        # Get keys for each user dict (list of dates)
        # convert keys to integers (timedelta?), find mean, convert back to date.    
        for username in user_date_dict:
            print username, numpy.mean(user_date_dict[]) 
    
    def add_userstats_weighted_mean_date(self, user_date_dict=None):
        """
        Find the mean date of activity, weighted by number of edited nodes on each day
        """
        if user_date_dict == None:
            user_date_dict = self.get_dates_and_edit_counts()
        # Get keys for each user dict (list of dates)
        # convert keys to integers (timedelta?), find weighted mean, convert back to date.    
        
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
            logging.error("can't add new column")
            logging.error(inst)
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
        querystring = "SELECT uid, username, count, blankcount, v1count, firstedit, firsteditv1, firsteditblank, days_active FROM " + userstatstable
        try:
            self.cur.execute(querystring)
        except Exception, inst:
            logging.error("can't select count and blankcount")
            logging.error(inst)
       
        localfile = open(filename, "w")
         
        print >> localfile, "uid\tusername\tcount\tblankcount\tv1count\tfirstedit\tfirsteditv1\tfirsteditblank\tdays_active"
        
        rows = self.cur.fetchall()
        
        for row in rows:
            # assign 0 instead of None
            uid = row[0] or 0
            username = row[1] or 0
            count = row[2] or 0
            blankcount = row[3] or 0
            v1count = row[4] or 0
            firstedit = row[5] or 0
            firsteditv1 = row[6] or 0
            firsteditblank = row[7] or 0
            days_active = row[8] or 0
            print >> localfile, "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % (uid, username, count, blankcount, v1count, firstedit, firsteditv1, firsteditblank, days_active)
            
        localfile.close() 