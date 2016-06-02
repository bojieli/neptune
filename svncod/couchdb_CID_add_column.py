import os
import sys
import time
import traceback
from read_cif import export_json_from_file
sys.path.insert(0, './couchdb-python/')
import couchdb

server = couchdb.Server(url='http://localhost:5984/')
db = server['moldb']

def couchdb_pager(db, view_name='_all_docs',
                  startkey=None, startkey_docid=None,
                  endkey=None, endkey_docid=None, bulk=1000):
    # Request one extra row to resume the listing there later.
    options = {'limit': bulk + 1}
    if startkey:
        options['startkey'] = startkey
        if startkey_docid:
            options['startkey_docid'] = startkey_docid
    if endkey:
        options['endkey'] = endkey
        if endkey_docid:
            options['endkey_docid'] = endkey_docid
    done = False
    while not done:
        view = db.view(view_name, **options)
        rows = []
        # If we got a short result (< limit + 1), we know we are done.
        if len(view) <= bulk:
            done = True
            rows = view.rows
        else:
            # Otherwise, continue at the new start position.
            rows = view.rows[:-1]
            last = view.rows[-1]
            options['startkey'] = last.key
            options['startkey_docid'] = last.id

        for row in rows:
            yield row.id


update_batch = 1000
updated_docs = []

start_time = time.time()
update_count = 0

def batch_update(doc):
	global db
	global updated_docs
	global start_time
	global update_count
	if doc:
		updated_docs.append(doc)
		update_count += 1
	if not doc or len(updated_docs) >= update_batch:
		elapsed_time = time.time() - start_time
		print(str(update_count) + ' files, ' + ('%.2f' % (update_count / elapsed_time)) + ' files/sec')

		db.update(updated_docs)
		updated_docs = []

for key in couchdb_pager(db):
	if key.startswith('COD'):
		doc = db[key]
		if 'structures' in doc:
			for row in doc['structures']:
				row['format'] = 'CIF'
			batch_update(doc)
			print(key)
	elif key.startswith('CID'):
		doc = db[key]
		doc["$type"] = "Molecule"
		doc["$source"] = "CID"
		batch_update(doc)
		print(key)

print("performing final sync...")
batch_update(None)
