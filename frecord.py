#!/usr/bin/python

import sys, os, time, pickle

def msectime():
	return int(time.time()*1000)


class Observations:
	def __init__(self):
		self.files = {} # Key is file path, value is instance of FileHistory
		self.cmdlines = {} # Key is PID, value is cmdline (assume that a given PID will only be used once during recording)
	
	def update(self, pid):
		if pid not in self.cmdlines:
			try:
				cmdf = open("/proc/%u/cmdline" % pid)
				cmdline = cmdf.readline().rstrip()
				cmdf.close()
				self.cmdlines[pid] = cmdline
			except IOError:
				pass

		rpaths = set()
		
		# Find out which regular files this process has open at the moment
		tgtpath = "/proc/%u/fd/" % pid
		try:
			fns = os.listdir(tgtpath)
			for fn in fns:
				try:
					rpath = os.readlink(tgtpath + fn)
					# Ignore non-absolute sybmolic links (these are how pipes, sockets, etc, are represented)
					# Also, ignore devices
					if rpath[0] == "/" and rpath[0:4] != "/dev":
						rpaths.add(rpath)
				except IOError:
					pass
		except OSError:
			pass
		
		# Find out which files have sections mapped to this process's memory (i.e. libraries)
		try:
			for line in file("/proc/%u/maps" % pid):
				rpath = line[49:].rstrip()
				# Ignore non-file entries in maps (i.e. "[heap]")
				if len(rpath) > 0 and rpath[0] == "/":
					rpaths.add(rpath)
		except IOError:
			pass
		
		for path in rpaths:
			if path not in self.files:
				self.files[path] = FileHistory()
			self.files[path].update(pid)


class FileHistory:
	def __init__(self):
		self.usages = {} # Key is pid, value is list of millitimestamps of samples of usage of file by that PID
	
	def update(self, pid):
		if pid not in self.usages:
			self.usages[pid] = []
		self.usages[pid].append(msectime())


def rec(outf):
	tstart = msectime()
	samples = 0
	obs = Observations()
	initialpids = set() # Pids which were running when observation started. We only care about pids not in this list.
	
	firstloop = True
	while True:
		try:
			tstamp = msectime()
			states = {}
			
			for fn in os.listdir("/proc"):
				try:
					pid = int(fn)
					if firstloop:
						initialpids.add(pid)
					elif pid not in initialpids:
						# Only interested in processes that started after the recording began
						obs.update(pid)
				except ValueError:
					pass
			
			if firstloop:
				firstloop = False
			
			samples += 1
			time.sleep(0.003)
		except KeyboardInterrupt:
			break
	
	tdiff = (msectime() - tstart)
	print "FRECORD: Samples: %u" % samples
	print "FRECORD: Time Elapsed: %.3f seconds" % (float(tdiff)/1000)
	print "FRECORD: Sample Rate: %.3f per second" % ((float(samples)/tdiff)*1000)
	
	pickle.dump(obs, outf)


if __name__ == "__main__":
	if len(sys.argv) != 2:
		print "Please supply the output filename"
		sys.exit()
	outf = None
	try:
		outf = open(sys.argv[1], "w")
	except:
		print "Couldn't open output file %s" % sys.argv[1]
		sys.exit()
	print "FRECORD: Opened file %s" % sys.argv[1]
	rec(outf)
	outf.close()
