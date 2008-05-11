#!/usr/bin/python

import sys, os, datetime, time, signal, subprocess

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

try:
	exec ("from %s import Timing" % sys.argv[2])
except ImportError:
	iprint("Second argument must be the name of a timing target module (i.e. one of the directories in this directory).")
	sys.exit()

tgtdev = ""
try:
	tgtdev = sys.argv[3]
	if not (tgtdev[0:5] == "/dev/" and os.access(tgtdev, os.R_OK)):
		raise Exception()
except:
	iprint("Third argument must be the device file for the relevant drive")
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
	
	t = Timing()
	
	frecordp = None
	if "-rec" in sys.argv:
		iprint("Starting file usage recording process...")
		fn = "mysql-frecord-%s---%u" % (nowstr, n)
		frecordp = subprocess.Popen(("../frecord.py", fn), stdout = subprocess.PIPE)
		time.sleep(2)
	
	iprint(" -- Starting timing")
	mtstart = int(time.time()*1000)
	
	try:
		t.timing()
	except Exception, e:
		iprint(str(e))
		sys.exit()
	
	mdiff = int(time.time()*1000) - mtstart
	iprint(" -- Finished timing")
	
	if frecordp != None:
		iprint("Finishing file usage recording process")
		os.kill(frecordp.pid, signal.SIGINT)
		frecordp.wait()
	
	time.sleep(2)

	try:
		t.posttiming()
	except Exception, e:
		iprint(str(e))
		sys.exit()
	
	iprint("     -----     Elapsed Time: %u ms" % mdiff)
	outf.write("%u\n" % mdiff)
	time.sleep(3)

outf.close()
