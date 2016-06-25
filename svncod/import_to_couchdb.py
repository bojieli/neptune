import os
import sys
import traceback
from read_cif import export_json_from_file
import time
sys.path.insert(0, './couchdb-python/')
import couchdb

walk_dir = sys.argv[1]
dbname = sys.argv[2]

server = couchdb.Server(url='http://localhost:5984/')
db = server[dbname]

start_time = time.time()
file_count = 0
failed_count = 0

for root, subdirs, files in os.walk(walk_dir):
    for filename in files:
	if not filename.endswith('.cif'):
		continue
        inpath = os.path.join(root, filename)
	print(inpath)
	try:
		jsons = export_json_from_file(inpath)
		for json in jsons:
			db[json['id']] = json
	except:
		traceback.print_exc()
		failed_count += 1
		
	file_count += 1
	elapsed_time = time.time() - start_time
	print(str(file_count) + ' files (failed ' + str(failed_count) + '), ' + ('%.2f' % (file_count / elapsed_time)) + ' files/sec')
