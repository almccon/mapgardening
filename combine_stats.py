#! /usr/bin/env python
"""
Combines the output statistics for each study area into a single file.

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
output_filename_template = [folder + "combined_", "_raster_1000m.tsv"]

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

for placename in places:
#for placename in places.keys():
    print "combining output stats for", placename

    userstats_filename = userstats_filename_template[0] + placename + userstats_filename_template[1]
    blankspots_filename = blankspots_filename_template[0] + placename + blankspots_filename_template[1]
    output_filename = output_filename_template[0] + placename + output_filename_template[1]

    print userstats_filename
    print blankspots_filename
    print output_filename

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

    # Finally print the data into a new filename, stepping through a sorted list
    # of usernames, and a sorted list of dates (but only the ones that exist).
    # But remember to output every column, or zeros if data isn't available. 

    with open(output_filename, 'wb') as outfile:
      doc = csv.writer(outfile, dialect='excel', delimiter='\t')

      # count and v1count should match 'nodes' and 'nodes_created'. Do I want to sanity check here?
      doc.writerow(['uid','username','year','nodes','nodes_created','cur nodes','blankcount','count','v1count'])
      for username in sorted(data.keys()):
        uid = data[username]['uid']
        for date in sorted(data[username]['edits']):
          values = data[username]['edits'][date]
          all_are_zero = True
          for field in ["nodes", "nodes_created", "cur nodes", "count", "v1count", "blankcount"]:
            if not field in values:
              values[field] = 0;
            else:
              if int(values[field]) != 0:
                all_are_zero = False
          # Sometimes all values are zero. No need to print these.
          if not all_are_zero:
            doc.writerow([uid, username, date, str(values['nodes']), str(values['nodes_created']), str(values['cur nodes']), str(values['blankcount']), str(values['count']), str(values['v1count'])])
