#!/bin/bash
if [ -z "$1" ] || [ -z "$2" ]; then
	echo "Usage: $0 <database-name> <index-name>"
	exit 1
fi

DBNAME=$1
INDEXNAME=$2
curl -X PUT "http://127.0.0.1:9200/$INDEXNAME?pretty=true" --data @index-httppost.conf
