#! /usr/bin/env python
"""
Create a list of all usernames and which study areas they're found in.

Based on combine_stats.py

There are three files to combine for each study area:

userstats_{placename}.csv
    a modified output of mvexel's userstats scripts, with monthly totals for users
    ...and overall totals by month for the whole study area

output_userstatsbydate_{placename}_raster_1000m.tsv
    my blankspot counts by date and user, not summed for months. Does not include totals.

NOTE: this assumes 1000m rasters. Would need to be extended for other scales.
"""

folder = "userstats/"

# The prefixes and postfixes for the input files
userstats_filename_template = [folder + "userstats_", ".csv"]
blankspots_filename_template = [folder + "output_userstatsbydate_", "_raster_1000m.tsv"]
output_filename = folder + "usercount_raster_1000m.tsv"

#import MapGardening
import optparse
import csv
import datetime

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

#MapGardening.init_logging()

usercounts = {}

for placename in places:
#for placename in places.keys():
    #print "combining output stats for", placename

    userstats_filename = userstats_filename_template[0] + placename + userstats_filename_template[1]
    blankspots_filename = blankspots_filename_template[0] + placename + blankspots_filename_template[1]

    #print userstats_filename
    #print blankspots_filename

    data = {}

    # First, parse the mvexel-style output.
    # We are ignoring many other fields in that table
    # ...for example anything about ways and relations

    fields_of_interest = ["nodes", "nodes_created", "cur nodes"]
    head = None
    doc = csv.reader(open(userstats_filename), dialect='excel', delimiter='\t')
    for row in doc:
      if not head:
        head = row
      else:
        username = row[head.index('username')]
        # My files print anonymous users differently
        if (username == ""):
          username = "NULL"
        date = row[head.index('year')]
        if not username in data:
          data[username] = {}
        data[username]['uid'] = row[head.index('uid')]
        if not 'edits' in data[username]:
          data[username]['edits'] = {}
        if not date in data[username]['edits']:
          data[username]['edits'][date] = {}
        for field in fields_of_interest:
          data[username]['edits'][date][field] = row[head.index(field)]

    # Now parse the blankspot data
    # This is all borrowed from the combine_stats.py script

    username = "total"
    if not username in data:
      data[username] = {}
    if not 'uid' in data[username]:
      data[username]['uid'] = ""     # if we loaded the user from mvexel style, this will be set already
    if not 'edits' in data[username]:
      data[username]['edits'] = {}

    fields_of_interest = ["count", "v1count", "blankcount"]
    head = None
    doc = csv.reader(open(blankspots_filename), dialect='excel', delimiter='\t')
    for row in doc:
      if not head:
        head = row
      else:
        username = row[head.index('user_name')]

        date = datetime.datetime.strptime(row[head.index('date')], "%Y-%m-%d").date()
        date = date.replace(day=1) # Round to first day of month
        date = date.strftime("%Y-%m-%d")
        if not username in data:
          data[username] = {}
        if not 'uid' in data[username]:
          data[username]['uid'] = ""     # if we loaded the user from mvexel style, this will be set already
        if not 'edits' in data[username]:
          data[username]['edits'] = {}
        if not date in data[username]['edits']:
          data[username]['edits'][date] = {}
        if not date in data['total']['edits']:
          data['total']['edits'][date] = {}
        for field in fields_of_interest:
          if not field in data[username]['edits'][date]:
            data[username]['edits'][date][field] = 0
          if not field in data['total']['edits'][date]:
            data['total']['edits'][date][field] = 0
          data[username]['edits'][date][field] += int(row[head.index(field)])
          data['total']['edits'][date][field] += int(row[head.index(field)])

    # For each user in this place, add to the usercounts list
    # Note that we're not actually counting anything...
    # ...just listing the places where this user can be found
    for username in sorted(data.keys()):
      if not username in usercounts:
        usercounts[username] = {}
        usercounts[username]['uid'] = data[username]['uid']
        usercounts[username]['places'] = [placename]
      else:
        usercounts[username]['places'].append(placename);

# Finally print the usercounts into a new file, stepping through a sorted list
# of usernames. Print the number of places for each user, as well as a comma-separated list of placenames (note that this is a TSV file, so they will all be in the same column.

with open(output_filename, 'wb') as outfile:
  doc = csv.writer(outfile, dialect='excel', delimiter='\t')

  doc.writerow(['username','uid','count','places'])
  for username in sorted(usercounts.keys()):
    doc.writerow([username, usercounts[username]['uid'], len(usercounts[username]['places']), ','.join(usercounts[username]['places'])])
