#!/bin/bash
if [ -z "$1" ]; then
	echo "Usage: $0 <database-name>"
	exit 1
fi

DBNAME=$1

function check_and_create_db() {
	PORT=$1
	DBNAME=$2
	if curl http://127.0.0.1:$PORT/_all_dbs 2>/dev/null | grep "\"$DBNAME\""; then
		echo "DB $DBNAME exists on port $PORT"
	else
		echo "try to create DB $DBNAME on port $PORT"
		curl -X PUT http://127.0.0.1:$PORT/$DBNAME
	fi
}
# create master database if not exists
check_and_create_db 5984 $DBNAME
# create backup database
check_and_create_db 59840 $DBNAME
# setup replication
echo "setting up continuous replication..."
curl -H "Content-Type: application/json" -d "{\"source\":\"$DBNAME\",\"target\":\"http://couchdb_backup:5984/$DBNAME\",\"continuous\":true}" http://localhost:5984/_replicate
