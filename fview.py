#!/usr/bin/python

import pickle, sys
from frecord import Observations, FileHistory

if len(sys.argv) != 2:
	print "Please supply the input filename"
	sys.exit()

fh = None
try:
	fh = open(sys.argv[1])
except:
	print "Couldn't open %s" % sys.argv[1]
	sys.exit()

obs = pickle.load(fh)

print "------ Observed processes:"
pids = obs.cmdlines.keys()
pids.sort()
for pid in pids:
	print "PID:%6u - %s" % (pid, obs.cmdlines[pid])

print
print

print "------ File usage:"
fns = obs.files.keys()
fns.sort()
for fn in fns:
	print "%s" % fn
	pids = obs.files[fn].usages.keys()
	pids.sort()
	for pid in pids:
		print "    PID:%6u (%8u samples) - %s" % (pid, len(obs.files[fn].usages[pid]), obs.cmdlines[pid])
