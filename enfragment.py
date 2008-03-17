#!/usr/bin/python

import sys, random
from pyext2 import ext2

try:
	fs = ext2.Fs(sys.argv[1])
	while (fs.scanning()):
		pass

	dblocks = []
	for i in range(1, fs.blocksCount()):
		if fs.isSwappableBlock(i):
			dblocks.append(i)
	
	for i in dblocks:
		t = random.choice(dblocks)
		print "%04u<->%04u " % (i, t)
		fs.swapBlocks(i, t)
except ext2.Ext2Error, e:
	print e.str()
except IndexError:
	print "Please supply the filename of an unmounted ext2 partition"
