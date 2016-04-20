#! /usr/bin/env python
"""
Calculate localness stats for each place, and print results to stdout.

Depends only on the "outputv5_*" files from add_localness.py

Does not depend on database access.

NOTE: this assumes 1000m rasters. Would need to be extended for other scales.
"""

folder = "userstats/"
infile_template = [folder + "outputv5_", "_raster_1000m.tsv"]

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

print "placename\tlocal users\tnonlocal users\tpercent local\tedits by locals\tedits by nonlocals\tpercent edits by locals"

for placename in places:

    input_filename = infile_template[0] + placename + infile_template[1]

    localusers = 0;
    localedits = 0;
    localv1edits = 0;
    localblankedits = 0;

    nonlocalusers = 0;
    nonlocaledits = 0;
    nonlocalv1edits = 0;
    nonlocalblankedits = 0;

    fields_of_interest = ["count", "blankcount", "v1count", "firstedit", "firsteditv1", "firsteditblank", "days_active", "mean_date", "mean_date_weighted"]
    head = None
    doc = csv.reader(open(input_filename), dialect='excel', delimiter='\t')
    for row in doc:
        if not head:
            head = row

        else:

            if row[head.index('countlocalness')] == 'NULL':
                # don't count it either way
                continue
            if float(row[head.index('countlocalness')]) >= 0.5:
                # call them a local
                localusers += 1
                localedits += int(row[head.index('count')])
                localv1edits += int(row[head.index('v1count')])
                localblankedits += int(row[head.index('blankcount')])
            else:
                # call them a nonlocal
                nonlocalusers += 1
                nonlocaledits += int(row[head.index('count')])
                nonlocalv1edits += int(row[head.index('v1count')])
                nonlocalblankedits += int(row[head.index('blankcount')])

    print '\t'.join([placename,str(localusers),str(nonlocalusers),str(float(localusers/(localusers+nonlocalusers))),str(localedits),str(nonlocaledits),str(float(localedits/(localedits+nonlocaledits)))])
