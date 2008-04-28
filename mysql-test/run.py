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

print " -- Starting timing"
mtstart = int(time.time()*1000)

initp = subprocess.Popen(("/etc/init.d/mysql", "start"))
initp.wait()

dbh = None
while True:
	try:
		dbh = MySQLdb.connect("localhost", "testuser", "testpass", "testing")
	except:
		if (int(time.time()*1000) - mtstart) > 20000:
			os.kill(frecord.pid, signal.SIGINT)
			frecordp.wait()
			raise Exception("Couldn't ever connect to MySQL server!")
		else:
			time.sleep(0.0005)
	else:
		break

cursor = dbh.cursor()
cursor.execute("""select * from table1, table2 where f12 < "2008-01-10" and f12 > "2008-01-08" and f11 like 'V%' and id2 = f13 order by f22 desc limit 10""")
rows = 0
for row in cursor.fetchall():
	rows += 1

mdiff = int(time.time()*1000) - mtstart
print " -- Finished timing"

time.sleep(2)

deinitp = subprocess.Popen(("/etc/init.d/mysql", "stop"))
deinitp.wait()

if frecordp != None:
	os.kill(frecordp.pid, signal.SIGINT)
	frecordp.wait()

if rows != 10:
	raise Exception("Wrong number of rows returned: %u instead of expected 10" % rows)
print "     -----     Elapsed Time: %u ms" % mdiff
