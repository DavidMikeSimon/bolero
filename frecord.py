#!/usr/bin/python

import sys, os, time, pickle

class ProcState:
	def __init__(self, pid):
		cmdf = open("/proc/%s/cmdline" % pid)
		self.cmdline = cmdf.readline().rstrip()
		cmdf.close()
		
		self.fds = set()
		tgtpath = "/proc/%s/fd/" % pid
		fns = os.listdir(tgtpath)
		for fn in fns:
			# If the fd proc entry goes away while we tried to read it, just continue on
			# Maybe the file was closed, maybe the process went away. Doesn't matter, just take the data we can get.
			try:
				rpath = os.readlink(tgtpath + fn)
				# Ignore non-absolute sybmolic links (these are how pipes, sockets, etc, are represented)
				# Also, ignore devices
				if rpath[0] == "/" and rpath[0:4] != "/dev":
					self.fds.add(rpath)
			except IOError:
				pass

def msectime():
	return int(time.time()*1000)

def rec():
	if len(sys.argv) != 2:
		print "Please supply the output filename"
		sys.exit()

	outf = None
	try:
		outf = open(sys.argv[1], "w")
	except:
		print "Couldn't open output file %s" % sys.argv[1]
		sys.exit()
	
	mypid = str(os.getpid())
	
	rec = {} # Key is millisecond timestamp, value is a dict of interesting pids to ProcStates
	initialpids = set() # Pids which were running when observation started. We only care about pids not in this list

	tstart = msectime()
	samples = 0
	firstloop = True
	while True:
		try:
			tstamp = msectime()
			states = {}
			
			for fn in os.listdir("/proc"):
				if fn[0] >= '0' and fn[0] <= '9' and fn != mypid:
					if firstloop:
						initialpids.add(fn)
					# We are only interested in processes that started after the recording process started
					elif fn not in initialpids:
						# Handle the case of a process's cmdline file going away before we get a chance to read it
						# If it goes away during the reading of fds, we are still interested in the ones that we got a chance to look at
						try:
							states[int(fn)] = ProcState(fn)
						except IOError:
							pass
			
			if firstloop:
				firstloop = False
			elif len(states) > 0:
				rec[tstamp] = states
			
			samples += 1
			time.sleep(0.003)
		except KeyboardInterrupt:
			break
	
	tdiff = (msectime() - tstart)
	print "Samples: %u" % samples
	print "Time Elapsed: %.3f seconds" % (float(tdiff)/1000)
	print "Sample Rate: %.3f per second" % ((float(samples)/tdiff)*1000)

	pickle.dump(rec, outf)
	outf.close()

if __name__ == "__main__":
	rec()
