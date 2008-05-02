#!/usr/bin/python

# Examines several files of the sort produced by frecord, and creates a single list of paths sorted by access time
# Includes every file mentioned in at least one frecord, and follows majority rule when deciding order

import pickle, sys
from frecord import Observations, FileHistory

if len(sys.argv) < 2:
	print "Please supply at least one input filename"
	sys.exit()

flists = []
all = set()

for f in sys.argv[1:]:
	fh = None
	try:
		fh = open(f)
	except:
		print "Couldn't open %s" % sys.argv[1]
		sys.exit()
	obs = pickle.load(fh)
	flist = obs.files_ordered()
	for f in flist:
		all.add(f)
	flists.append(flist)


def summcmp(a, b):
	# A goes before B to the degree that A was recorded as being loaded before B
	r = 0
	for flist in flists:
		try:
			idxa = flist.index(a)
			idxb = flist.index(b)
			r += (idxa - idxb)
		except ValueError:
			pass
	return r

summlist = sorted(all, summcmp)
for f in summlist:
	print f
