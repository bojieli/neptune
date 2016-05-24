#!/bin/bash
# start couchdb backup (should be on hard disk)
docker run -d --link couchdb:couchdb_master -p 127.0.0.1:59840:5984 -v /usr/local/couchdb_backup:/usr/local/var/lib/couchdb --name couchdb_backup klaemo/couchdb
# start couchdb (should be on SSD)
docker run -d --link couchdb_backup:couchdb_backup -p 127.0.0.1:5984:5984 -v /var/lib/couchdb:/usr/local/var/lib/couchdb --name couchdb klaemo/couchdb
# start elasticsearch
docker run -d -p 127.0.0.1:9200:9200 -p 127.0.0.1:9300:9300 -v /var/lib/elastic_config:/usr/share/elasticsearch/config -v /var/lib/elastic_data:/usr/share/elasticsearch/data --name elastic elasticsearch
# start logstash
docker run -d --link couchdb:couchdb --link elastic:elastic -v /var/lib/logstash_config:/config-dir --name logstash logstash logstash -f /config-dir/logstash.conf
