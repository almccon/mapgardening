Instructions for installing and running on AWS
=======

**in progress**

All of the code in the repo was originally written to run locally on OSX. I am now porting most of it to run on Amazon Web Services (AWS). 



Getting the full history dump
------

Log into your AWS console (I'm using the Stamen group). I'm using the us-west-2a zone (Oregon).

Create a 100GB gp2 EBS volume for the history dump. (As for Jan 2016 the history dump is 49G itself)

Create an r3.xlarge ubuntu instance to do the history splitting (and processing?). This is a pretty big instance, so remember to stop it when its done!

Log into the instance:

`ssh -i ~/.ssh/osmhistory.pem ubuntu@xxx.xxx.xxx.xxx`
or
`ssh -i ~/.ssh/osmhistory.pem root@xxx.xxx.xxx.xxx`
(get latest IP address from the EC2 console)

Associate the EBS volume with the instance using the web console. Then mount it:

List the disks:
`sudo fdisk -l`
Make the filesystem:
`sudo mkfs -t ext4 /dev/xvdf`
Make a mountpoint:
`sudo mkdir /mnt/ebs`
Mount the drive:
`sudo mount /dev/xvdf /mnt/ebs`
Confirm that it mounted:
`mount -l`
`df`

Download the history file in pbf format. Find the link to the latest version at the bottom of this page: http://planet.openstreetmap.org/planet/experimental/

`wget http://planet.openstreetmap.org/planet/experimental/history-2014-11-24.osm.pbf`

Then create a symlink to this file using .osh.pbf instead of osm.pbf (necessary for the osm-history-splitter to read it correctly)

ln -s history-2014-11-24.osm.pbf history-2014-11-24.osh.pbf

Then make a snapshot of this volume.

After you run the `osm-history-splitter` you probably want to make another snapshot of this volume.

After you're finished doing the splitting, you can unmount this drive and stop this large instance. Then connect this drive (the one with the extracts) to a smaller EC2 instance to import them into a database (using `osm-history-renderer`) and run the map-gardening analysis.
