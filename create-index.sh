#!/bin/bash
if [ -z "$1" ]; then
	echo "Usage: $0 <index-name>"
	exit 1
fi

INDEXNAME=$1
curl -X PUT "http://127.0.0.1:9200/$INDEXNAME?pretty=true" --data @index-httppost.conf
