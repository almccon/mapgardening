Map Gardening
=========

A collection of scripts by [Alan McConchie](https://github.com/almccon) for the analysis of "map gardening" in OpenStreetMap

Installation
----

Requires a database of the format produced by the importer component of the [osm-history-renderer](https://github.com/MaZderMind/osm-history-renderer). Most of the following steps are just to get the osm-history-renderer running.

Get an osm history dump by downloading `history-YYYY-MM_DD.osm.pbf` from here: http://planet.openstreetmap.org/planet/experimental/

```
curl http://planet.openstreetmap.org/pbf/full-history/history-latest.osm.pbf -o history-2015-01-26.osm.pbf
```

Alias this from .osm.pbf to .osh.pbf


```
sudo apt-get install git
git clone https://github.com/almccon/osmium
git clone https://github.com/almccon/osm-history-splitter
git clone https://github.com/almccon/osm-history-renderer
sudo apt-get update
sudo apt-get install libboost-dev zlib1g-dev libshp-dev libgd2-xpm-dev libgdal1-dev libexpat1-dev libgeos++-dev libsparsehash-dev libv8-dev libicu-dev libprotobuf-dev protobuf-compiler doxygen libboost-test-dev libosmpbf-dev clang make
cd osmium
sudo make install
cd ..
cd osm-history-splitter
sudo make install
```

Now, do the splitting. This seems to require a machine with a lot of memory. The extracted files will end up in the current directory. On EC2 copy them to a mounted disc so they can be accessed by a smaller instance.

```
./osm-history-splitter --hardcut /mnt/ebs/history-2014-12-22.osh.pbf osm-history-splitter.config
```

```
cd osm-history-renderer
sudo apt-get install libproj-dev postgresql postgresql-client postgresql-9.3-postgis-2.1 pgadmin3 postgresql-contrib
cd importer # inside the osm-history-renderer directory
make
```

Now we create our database and import the extract. Generally, instead of `osm-history-render` I use `osm-history-render-place` as the database name, and keep each extract in a separate database. Then make sure this database name is saved in `MapGardening/__init__.py` so the scripts know which place corresponds to which database.

```
sudo -u postgres createuser $USER --superuser -P # when prompted, use the same password stored in __init__.py

createdb osm-history-render
psql -d osm-history-render -c "create extension postgis;"
psql -d osm-history-render -c "create extension hstore;"

cd importer # inside the osm-history-renderer/importer/ directory
./osm-history-importer --dsn "dbname='osm-history-render'" /mnt/ebs/losangeles.osh.pbf
```

(currently this fails for me after closing the polygon table)

Message:

```
ERROR:  data type timestamp without time zone has no default operator class for access method "gist"
HINT:  You must specify an operator class for the index or define a default operator class for the data type.
terminate called after throwing an instance of 'std::runtime_error'
  what():  command failed
Aborted (core dumped)
```

Despite the core dump, this process seems to result in a usable database.

Or to initialize several at the same time: (test this for escapes, and for crashing at the importer step)

```
cd importer # inside the osm-history-renderer directory
for place in amsterdam auckland bayarea berlin boston buenosaires cairo crimea cyprus douala haiti istanbul jakarta jerusalem london losangeles manchester mexicocity minsk montevideo montreal moscow mumbai nairobi newyork quebec paris rio santiago seattle seoul tirana tokyo toronto vancouver yaounde
do
  createdb osm-history-render-$place
  psql -d osm-history-render-$place -c "create extension postgis;"
  psql -d osm-history-render-$place -c "create extension hstore;"
  ./osm-history-importer --dsn "dbname='osm-history-render-$place'" /mnt/ebs/$place.osh.pbf || true
  psql -d osm-history-render-$place -c "create index hist_point_idx on hist_point using gist(geom);"
  psql -d osm-history-render-$place -c "VACUUM ANALYZE hist_point;"
done
```

Doing the analyses
----

```
./initialize_nodetable.py -p place
```


When the databases have been loaded, run the mapgardening analysis scripts. 

 * ./proximity_check.py -p bayarea
 * raster_stats.py
 * user_analysis.py

(modify `MapGardening/__init__.py` for configuration)

TODO: transfer changes from small ec2 to large (or commit to github)

Add a password to the ubuntu account on postgres. Log into psql: `\password ubuntu`



For Tilemill mapping and debugging
----

```
git clone https://github.com/mapbox/tilemill
cd tilemill
sudo add-apt-repository ppa:developmentseed/mapbox
sudo apt-get install npm
sudo apt-get update
sudo apt-get install tilemill libmapnik nodejs
npm install
```

Read some of this:
https://www.mapbox.com/tilemill/docs/linux-install/

Then:

```
nodejs /usr/share/tilemill/index.js export every-line-ever output.png

```


What is map gardening? 
----

For now, let me explain by offering the abstract from my presentation at the 2013 Association of American Geographers conference:

> While the volume of Volunteered Geographic Information (VGI) continues its rapid growth, many collaborative mapping projects such as OpenStreetMap (OSM) are entering a mature phase, where the primary activity shifts away from the initial creation of data to its ongoing maintenance. As OSM approaches "completeness" in some geographic areas, there remain the less glamourous--but no less important--tasks of adding attribute data and periodically updating the map to reflect changes on the ground.

> Most research to date does not differentiate between various types of interaction with VGI datasets, thereby leaving many questions unanswered. For example: are the users who initially contribute data the same users who maintain it later? Do the types of tasks undertaken by users change over the duration of their engagement with a project? Are initial contributors more or less likely to have local knowledge of a place than those who maintain that data later?

> In this presentation we propose a typology of modes of interaction with VGI datasets, specifically distinguishing between the acts of adding new data and editing existing data. We adapt the term "wiki gardening" from research on Wikipedia, and propose the term "map gardening" to describe volunteer-led maintenance of VGI data. We apply this concept to the OpenStreetMap dataset, presenting a quantitative analysis of the extent and frequency of map gardening, and making comparisons across different spatial and temporal scales and between individual users. We argue that this typology offers a new insight for understanding the evolution and social dynamics of crowdsourced geospatial datasets.

This github repository includes some of the scripts I am using to perform this quantitative analysis. At this point they may not be complete or functional, but in time I hope to post all my code here.

For more information, see this [blog post](http://mappingmashups.net/2013/05/25/introducing-map-gardening/), or watch [this video](http://vimeopro.com/openstreetmapus/state-of-the-map-us-2013/video/68097490) from the [2013 State of the Map US Conference](http://stateofthemap.us/)
