Map Gardening
=========

A collection of scripts by [Alan McConchie](https://github.com/almccon) for the analysis of "map gardening" in OpenStreetMap

Installation
----

Requires a database of the format produced by the importer component of the [osm-history-renderer](https://github.com/MaZderMind/osm-history-renderer). Most of the following steps are just to get the osm-history-renderer running.

Get an osm history dump by downloading `history-YYYY-MM_DD.osm.pbf` from here: http://planet.openstreetmap.org/planet/experimental/

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

./osm-history-splitter --hardcut /mnt/ebs/history-2014-12-22.osh.pbf osm-history-splitter.config


cd osm-history-renderer
(not sure which order is necessary here, some of these may be already installed)
sudo apt-get install libproj-dev
sudo apt-get install postgresql
sudo apt-get install postgresql-client
sudo apt-get install postgresql-9.3-postgis-2.1 pgadmin3 postgresql-contrib

sudo -u postgres createuser $USER --superuser
createdb osm-history-render
psql -d osm-history-render -c "create extension postgis;"
psql -d osm-history-render -c "create extension hstore;"

cd importer # inside the osm-history-renderer directory
./osm-history-importer --dsn "dbname='osm-history-render'" /mnt/ebs/losangeles.osh.pbf
(currently this fails for me)

```

Instead of using the renderer, you could do this:

```
sudo apt-get install osm2pgsql
osm2pgsql /mnt/ebs/losangeles.osh.pbf -d osm-history-render
```

For Tilemill mapping and debugging

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
