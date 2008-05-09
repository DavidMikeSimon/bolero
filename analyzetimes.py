#!/usr/bin/python

import sys, numpy

for name in sys.argv[1:]:
	fh = open(name)
	vals = []
	for line in fh:
		vals.append(int(line.strip()))
	print "%s (%u lines):  Mean=%.2f  StdDev=%.2f" % (name, len(vals), numpy.mean(vals), numpy.std(vals))
