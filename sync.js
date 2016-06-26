var request = require('request')
  , JSONStream = require('JSONStream')
  , es = require('event-stream')
  , elasticsearch = require('elasticsearch')
  , fs = require('fs')

if (process.argv.length != 4) {
    throw "Usage: node sync.js <dbname> <index_name>";
}

var dbhost = 'http://localhost:5984'
var dbname = process.argv[2]
var db = dbhost + '/' + dbname
var es_client = new elasticsearch.Client({host: 'localhost:9200'})
var index_name = process.argv[3]
var max_in_flight_reqs = 100
var curr_in_flight_reqs = 0
var is_bulk_in_flight = false
var bulk_buffer = []

var couchdb_seq_file = '.couchdb_seq_' + dbname
var since_number = 0
try {
	since_number = parseInt(fs.readFileSync(couchdb_seq_file))
	if (isNaN(since_number))
		since_number = 0
} catch(e) {
	console.log(e)
}
var global_max_seq = since_number
console.log("Starting syncing from " + db + " since sequence number " + since_number)

function flush_bulk_buffer() {
  var bulk_body = []
  bulk_buffer.forEach((doc) => {
     bulk_body.push({"index":{"_id": doc._id, "_index":index_name, "_type": doc["$type"], "_routing":null}}),
     bulk_body.push({"doc": doc })
  })
  bulk_buffer = []

  is_bulk_in_flight = true
  es_client.bulk({ body: bulk_body }, (err, resp) => { 
     if (err)
       throw err
     try {
       if (resp.errors) {
         //console.log("elasticsearch bulk update error: " + JSON.stringify(resp))
         resp.items.forEach((item) => {
           if (item.index.status != 200) {
             console.log("Update failed [" + item.index._id + "]: " + JSON.stringify(item.index))
           }
         })
       }
       id_list = resp.items.map((item) => item.index._id)
       this.emit('data', "Update batch size " + id_list.length + " took " + resp.took + "ms, seq " + global_max_seq + ", IDs: " + id_list.join(',') + "\n")
       if (global_max_seq > 0)
         fs.writeFile(couchdb_seq_file, global_max_seq)
     } catch(e) {
       console.log(e)
     }

     is_bulk_in_flight = false
     if (bulk_buffer.length > 0)
       flush_bulk_buffer.call(this)
     if (this.paused)
       this.resume()
  })
}

request({url: db + '/_changes?feed=continuous&since=' + since_number })
  //.pipe(JSONStream.parse('results.*'))
  .pipe(es.split()) // by line
  .pipe(es.mapSync((line) => JSON.parse(line)))
  .pipe(es.through(function write(record) {
    global_max_seq = record.seq
    var id = record.id
    if (dbname == 'moldb3' && global_max_seq <= 7875823 && id.startsWith('COD')) {
      return;
    }
    curr_in_flight_reqs += 1
    if (curr_in_flight_reqs >= max_in_flight_reqs)
      this.pause()
    request(db + '/' + id, (err, res, body) => {
      curr_in_flight_reqs -= 1

      if (!err && res.statusCode == 200) {
        var doc = JSON.parse(body)

        bulk_buffer.push(doc)
        if (!is_bulk_in_flight)
          flush_bulk_buffer.call(this)
      }
      else {
        console.log("CouchDB error: " + JSON.stringify(err))
        console.log("CouchDB error HTTP response: " + JSON.stringify(res))
      }
    })
  }))
  .pipe(process.stdout);
