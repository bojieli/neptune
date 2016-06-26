#!/bin/bash
docker network create couchdb-net
# start couchdb backup (should be on hard disk)
docker run -d --net=couchdb-net --net-alias=couchdb_backup -p 127.0.0.1:59840:5984 -v /usr/local/couchdb_backup:/usr/local/var/lib/couchdb --name couchdb_backup klaemo/couchdb
# start couchdb (should be on SSD)
docker run -d --net=couchdb-net --net-alias=couchdb_master -p 127.0.0.1:5984:5984 -v /var/lib/couchdb:/usr/local/var/lib/couchdb --name couchdb klaemo/couchdb
# start elasticsearch
docker run -d --net=couchdb-net --net-alias=elastic -p 127.0.0.1:9200:9200 -p 127.0.0.1:9300:9300 -v /var/lib/elastic_config:/usr/share/elasticsearch/config -v /var/lib/elastic_data:/usr/share/elasticsearch/data --name elastic elasticsearch
# start logstash
docker run -d --net=couchdb-net --net-alias=logstash -v /var/lib/logstash_config:/config-dir --name logstash logstash-large logstash -f /config-dir/logstash.conf

docker run -d --net=couchdb-net --net-alias=webserver -p 127.0.0.1:3000:3000 -v /var/mat-gene:/var/mat-gene --name webserver mat-gene
