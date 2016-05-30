import os
import sys
import traceback
from read_cif import export_json_from_file
import time

walk_dir = sys.argv[1]

start_time = time.time()
file_count = 0
failed_count = 0

for root, subdirs, files in os.walk(walk_dir):
    for filename in files:
	if not filename.endswith('.cif'):
		continue
        inpath = os.path.join(root, filename)
	outpath = os.path.join('json', inpath)
	try:
		os.makedirs(os.path.dirname(outpath))
	except:
		pass

	print(inpath)
	try:
		outf = open(outpath, 'w')
		jsons = export_json_from_file(inpath)
		for json in jsons:
			outf.write(json)
		outf.close()
	except:
		traceback.print_exc()
		failed_count += 1
		
	file_count += 1
	elapsed_time = time.time() - start_time
	print(str(file_count) + ' files (failed ' + str(failed_count) + '), ' + ('%.2f' % (file_count / elapsed_time)) + ' files/sec')
