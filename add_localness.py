#! /usr/bin/env python
"""
Calculate statistics for each user, and print results to a tsv.

Combine the "outputv4_*" files from user_analysis.py with "userstats_summed.csv" (includes planet-wide totals.)
Result is overall indicators for each user (not subdivided by time) including "localness".

Does not depend on database access.

NOTE: this assumes 1000m rasters. Would need to be extended for other scales.
"""

folder = "userstats/"
infile_template = [folder + "outputv4_", "_raster_1000m.tsv"]
outfile_template = [folder + "outputv5_", "_raster_1000m.tsv"]
planet_total_file = folder + "userstats_summed.csv"

#import MapGardening
#from MapGardening import UserStats
#import time
import optparse
import csv

usage = "usage: %prog [options]"
p = optparse.OptionParser(usage)
p.add_option('--place', '-p',
             default="all"
             )

options, arguments = p.parse_args()

if options.place == "all":

    #places = MapGardening.get_all_places()
    places = [
        "amsterdam",
        "auckland",
        "barcelona",
        "bayarea",
        "berlin",
        "boston",
        "buenosaires",
        "cairo",
        "chicago",
        "crimea",
        "cyprus",
        "douala",
        "haiti",
        "istanbul",
        "jakarta",
        "jerusalem",
        "kathmandu",
        "lasvegas",
        "london",
        "losangeles",
        "manchester",
        "mexicocity",
        "miami",
        "minsk",
        "montevideo",
        "montreal",
        "moscow",
        "mumbai",
        "nairobi",
        "newyork",
        "quebec",
        "paris",
        "rio",
        "santiago",
        "seattle",
        "seoul",
        "sydney",
        "tirana",
        "tokyo",
        "toronto",
        "vancouver",
        "yaounde"
      ]

else:

    placename = options.place
    #place = MapGardening.get_place(placename)
    #places = {placename: place}
    places = [placename]

# first we load the planet-wide totals:

# this is mvexel-style output.
# We are ignoring many other fields in that table
# ...for example anything about ways and relations

print "loading planet-wide totals"

data = {}
fields_of_interest = ["nodes","nodes_created", "cur nodes"]
head = None
doc = csv.reader(open(planet_total_file), dialect='excel', delimiter='\t') # filename is .csv but it's actually tsv
for row in doc:
    if not head:
        head = row
    else:
        username = row[head.index('username')]
        uid = row[head.index('uid')]

        # My files print anonymous users differently
        if (username == ""):
            username = "NULL"
        #if not username in data:
        #    data[username] = {}
        if not uid in data:
            data[uid] = {}
        data[uid]['username'] = row[head.index('username')]
        #data[username]['uid'] = row[head.index('uid')]
        for field in fields_of_interest:
            data[uid][field] = row[head.index(field)]
            #data[username][field] = row[head.index(field)]

for placename in places:

    print "adding localness for", placename

    input_filename = infile_template[0] + placename + infile_template[1]

    output_filename = outfile_template[0] + placename + outfile_template[1]

    with open(output_filename, 'wb') as outfile:

        outdoc = csv.writer(outfile, dialect='excel', delimiter='\t')

        fields_of_interest = ["count", "blankcount", "v1count", "firstedit", "firsteditv1", "firsteditblank", "days_active", "mean_date", "mean_date_weighted"]
        head = None
        doc = csv.reader(open(input_filename), dialect='excel', delimiter='\t')
        for row in doc:
            if not head:
                head = row

                outdoc.writerow(["user_id","user_name", "count", "blankcount", "v1count", "firstedit", "firsteditv1", "firsteditblank", "days_active", "mean_date", "mean_date_weighted", "countlocalness", "v1countlocalness"])

            else:
                username = row[head.index('user_name')]
                uid = row[head.index('user_id')]

                countlocalness = 'NULL'
                v1countlocalness = 'NULL'

                # look up planet totals
                if not uid in data:
                    if uid == 'NULL' or username == 'NULL':
                        # don't worry about looking up anonymous accounts
                        countlocalness = 'NULL'
                        v1countlocalness = 'NULL'
                    else:
                        raise LookupError("Error: couldn't find", uid, username, "in planet file")
                else:
                    try:
                        #countlocalness = float(row[head.index("count")]) / float(data[uid]["nodes"])
                        countlocalness = round( float(row[head.index("count")]) / float(data[uid]["nodes"]) ,4)

                        # these are supposed to be percents. Round them back to 1 if they're over for any reason.
                        if countlocalness >= 1:
                            countlocalness = 1.0

                        # should never happen
                        if countlocalness < 0:
                            countlocalness = 0.0

                    except ZeroDivisionError as error:
                        countlocalness = 'NULL'

                    try:
                        #v1countlocalness = float(row[head.index("v1count")]) / float(data[uid]["nodes_created"])
                        v1countlocalness = round( float(row[head.index("v1count")]) / float(data[uid]["nodes_created"]) ,4)
                        if v1countlocalness >= 1:
                            v1countlocalness = 1.0
                        if v1countlocalness < 0:
                            v1countlocalness = 0.0

                    except ZeroDivisionError as error:
                        v1countlocalness = 'NULL'

                # Finally print the data into a new filename, with each new row matching the row we just read...
                # ...with the added two columns, of course.
                outdoc.writerow([row[head.index("user_id")],row[head.index("user_name")],row[head.index("count")],row[head.index("blankcount")],row[head.index("v1count")],row[head.index("firstedit")],row[head.index("firsteditv1")],row[head.index("firsteditblank")],row[head.index("days_active")],row[head.index("mean_date")],row[head.index("mean_date_weighted")],countlocalness,v1countlocalness])



