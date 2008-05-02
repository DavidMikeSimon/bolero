#!/usr/bin/python

# Examines several files of the sort produced by frecord, and creates a single list of paths sorted by access time
# Includes every file mentioned in at least one frecord, and follows majority rule when deciding order

import pickle, sys
from frecord import Observations, FileHistory

if len(sys.argv) < 2:
	print "Please supply at least one input filename"
	sys.exit()

for fn in sys.argv:
	fh = None
	try:
		fh = open(sys.argv[1])
	except:
		print "Couldn't open %s" % sys.argv[1]
		sys.exit()
	obs = pickle.load(fh)
