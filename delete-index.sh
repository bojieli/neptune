#!/bin/bash
if [ -z "$1" ]; then
	echo "Usage: $0 <index-name>"
	exit 1
fi

INDEXNAME=$1
# delete index
curl -X DELETE "localhost:9200/$INDEXNAME?pretty=true"
