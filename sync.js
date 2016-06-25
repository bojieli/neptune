var request = require('request')
  , JSONStream = require('JSONStream')
  , es = require('event-stream')
  , elasticsearch = require('elasticsearch')
  , fs = require('fs')

var db = 'http://localhost:5984/moldb2'
var es_client = new elasticsearch.Client({host: 'localhost:9200'})
var index_name = "molecule3"
var max_in_flight_reqs = 100
var curr_in_flight_reqs = 0
var is_bulk_in_flight = false
var bulk_buffer = []

var since_number = 0
try {
	since_number = fs.readFileSync('.couchdb_seq')
} catch(e) {
	console.log(e)
}
console.log("Starting syncing from " + db + " since sequence number " + since_number)

request({url: db + '/_changes?feed=continuous&since=' + since_number })
  //.pipe(JSONStream.parse('results.*'))
  .pipe(es.split()) // by line
  .pipe(es.mapSync((line) => JSON.parse(line)))
  .pipe(es.through(function write(record) {
    var seq = record.seq
    var id = record.id
    curr_in_flight_reqs += 1
    if (curr_in_flight_reqs >= max_in_flight_reqs)
      this.pause()
    request(db + '/' + id, (err, res, body) => {
      curr_in_flight_reqs -= 1

      if (!err && res.statusCode == 200) {
        var doc = JSON.parse(body)

        bulk_buffer.push(doc)
        if (!is_bulk_in_flight) {
          // flush bulk buffer
          var bulk_body = []
          bulk_buffer.forEach((doc) => {
             this.emit('data', doc.id + "\n")
             bulk_body.push({"index":{"_id": doc.id, "_index":index_name, "_type": doc["$type"], "_routing":null}}),
             bulk_body.push({"doc": doc })
          })
          bulk_buffer = []

          is_bulk_in_flight = true
          es_client.bulk({ body: bulk_body }, (err, resp) => { 
             if (err)
               console.log(err)
             fs.writeFile(".couchdb_seq", seq)
             is_bulk_in_flight = false
             if (this.paused)
               this.resume()
          })
        }
      }
      else {
        console.log(err)
        console.log(res)
      }
    })
  }))
  .pipe(process.stdout);
