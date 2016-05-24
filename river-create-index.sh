#!/bin/bash
if [ -z "$1" ] || [ -z "$2" ]; then
	echo "Usage: $0 <database-name> <index-name>"
	exit 1
fi

DBNAME=$1
INDEXNAME=$2
curl -X PUT "http://127.0.0.1:9200/_river/$INDEXNAME/_meta?pretty=true" \
	-d "{ \"type\" : \"couchdb\", \"couchdb\" : { \"host\" : \"couchdb\", \"port\" : 5984, \"db\" : \"$DBNAME\", \"filter\" : null }, \"index\" : { \"index\" : \"$INDEXNAME\", \"type\" : \"$INDEXNAME\", \"bulk_size\" : \"100\", \"bulk_timeout\" : \"10ms\" } }"
