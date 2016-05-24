if (process.argc < 3) {
    console.log('Usage: nodejs import.js <json-file>');
    process.exit();
}

// use memcached with "memcache" NPM package 
var nodeCouchDB = require("node-couchdb");
var couch = new nodeCouchDB("localhost", 5984);

var json_file = process.argv[2];
console.log('Importing from ' + json_file);
var data = require('./' + json_file);

var counter = 0;
var all_docs = [];
for (var key in data) {
    counter ++;
    var doc = data[key];
    doc._id = key;
    all_docs.push(doc);
}
console.log('insert ' + counter + ' records...');

var seq = 0;
var success = 0;
var exist = 0;
var parallel = 50;
var in_flight = 0;
var requests = 0;

function insert_one_record(doc) {
	requests ++;
	couch.insert("moldb", doc, function (err, resData) {
	    if (err) {
		if (err.indexOf('Problem with HTTP POST request: Unexpected status code {CODE:409}') == 0) {
                    exist ++;
                }
                else {
	            console.error(err);
		    insert_one_record(doc); // retry insertion
                    return;
                }
	    }
	    else {
	        success ++;
            }

	    in_flight --;
	    if (in_flight < parallel)
	        parallel_insert();
	});
}

function parallel_insert() {
	if (seq >= counter) {
	    if (in_flight == 0) // last thread
	        console.log('success ' + success + ' records, exist ' + exist + ' records, failed ' + (counter - success - exist) + ' records, ' + requests + ' HTTP requests');
	    return;
	}
	in_flight ++;
	insert_one_record(all_docs[seq ++]);
}

// create threads
for (var i=0; i<parallel; i++)
	parallel_insert();
