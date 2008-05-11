#!/usr/bin/python

import MySQLdb, sys, os, datetime, time, signal, subprocess

def iprint(msg):
	print "TIMING: %s" % msg

if not os.access("/proc/sys/vm/drop_caches", os.W_OK):
	iprint("Insufficient privileges. You must be superuser.")
	sys.exit()

runs = 0
try:
	runs = int(sys.argv[1])
	if runs < 1:
		iprint("First argument must be a postive number.")
		sys.exit()
except:
	iprint("First argument must be the number of runs to perform.")
	sys.exit()

tgtdev = ""
try:
	tgtdev = sys.argv[2]
	if not (tgtdev[0:5] == "/dev/" and os.access(tgtdev, os.R_OK)):
		raise Exception()
except:
	iprint("Second argument must be the device file for the relevant drive")
	sys.exit()

nowstr = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
outf = file("mysql-times-%s" % nowstr, "w")

for n in range(1, runs+1):
	iprint("   ---   Run %u of %u" % (n, runs))

	iprint("Dropping cache...")
	os.system("/bin/sync")
	fh = file("/proc/sys/vm/drop_caches", "w")
	fh.write("3\n")
	fh.close()
	time.sleep(5)
	iprint("Cache dropped, deceiving drive cache...")
	os.system("dd if=%s of=/dev/null bs=1024 count=32000" % tgtdev)
	iprint("Drive cache deceived")
	
	frecordp = None
	if "-rec" in sys.argv:
		iprint("Starting file usage recording process...")
		fn = "mysql-frecord-%s---%u" % (nowstr, n)
		frecordp = subprocess.Popen(("../frecord.py", fn), stdout = subprocess.PIPE)
		time.sleep(2)
	
	iprint(" -- Starting timing")
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
				iprint("Couldn't ever connect to MySQL server!")
				sys.exit()
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
	iprint(" -- Finished timing")
	
	if frecordp != None:
		iprint("Finishing file usage recording process")
		os.kill(frecordp.pid, signal.SIGINT)
		frecordp.wait()
	
	time.sleep(2)
	
	deinitp = subprocess.Popen(("/etc/init.d/mysql", "stop"))
	deinitp.wait()
	
	if rows != 10:
		iprint("Wrong number of rows returned: %u instead of expected 10" % rows)
		sys.exit()
	iprint("     -----     Elapsed Time: %u ms" % mdiff)
	outf.write("%u\n" % mdiff)
	time.sleep(3)

outf.close()
