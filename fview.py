#!/usr/bin/python

import pickle, sys
from frecord import ProcState

if len(sys.argv) != 2:
	print "Please supply the input filename"
	sys.exit()

fh = None
try:
	fh = open(sys.argv[1])
except:
	print "Couldn't open %s" % sys.argv[1]
	sys.exit()

rec = pickle.load(fh)

for (ts, states) in rec.iteritems():
	print "-" * 50
	print "TS: %u" % ts
	for (pid, state) in states.iteritems():
		print " Process: %6u %s" % (pid, state.cmdline)
		for f in state.fds:
			print "  %s" % f
