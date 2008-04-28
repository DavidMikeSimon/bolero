#!/usr/bin/python

import MySQLdb, sys, os, subprocess, datetime, time, signal

if not os.access("/proc/sys/vm/drop_caches", os.W_OK):
	print "Insufficient privileges. You must be superuser."
	sys.exit()

if "drop" in sys.argv:
	print "Dropping cache"
	os.system("/bin/sync")
	fh = file("/proc/sys/vm/drop_caches", "w")
	fh.write("3\n")
	fh.close()
else:
	print "Not dropping cache"

frecordp = None
if "rec" in sys.argv:
	print "Starting file usage recording process"
	fn = "mysql-frecord-%s" % datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
	frecordp = subprocess.Popen(("../frecord.py", fn))
	print "File usage recording begins"

mtstart = int(time.time()*1000)

dbh = MySQLdb.connect("localhost", "testuser", "testpass", "testing")
cursor = dbh.cursor()

cursor.execute("""select * from table1, table2 where f12 < "2008-01-10" and f12 > "2008-01-08" and f11 like 'V%' and id2 = f13 order by f22 desc limit 10""")
for row in cursor.fetchall():
	print "ROW",
print

mdiff = int(time.time()*1000) - mtstart
print "Elapsed: %u ms" % mdiff

if frecordp != None:
	os.kill(frecordp.pid, signal.SIGINT)
	frecordp.wait()
