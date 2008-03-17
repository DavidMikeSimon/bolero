#!/usr/bin/python

# FIXME: This needs to do the following:
# - Actually work on fullish partitions (this is just a quickie algorithm, I need to make a real one, probably something like selection sort)
# - Notice when mid-disk blocks cannot be moved, and attempt to avoid letting them split a file into pieces
# - Try to move blocks so that they're near to the center of the disk, rather than right at the beginning

import sys
from pyext2 import ext2

try:
	fs = ext2.Fs(sys.argv[1])
	while (fs.scanning()):
		pass
	
	dblocks = []
	for b in range(1, fs.blocksCount()):
		if fs.isSwappableBlock(b):
			dblocks.append(b)
	
	inodes = []
	for i in fs.inodes():
		iblocks = []
		for b in i.blocks():
			if fs.isSwappableBlock(b):
				iblocks.append(b)
		if len(iblocks) > 0:
			inodes.append(iblocks)
	
	for i in inodes:
		for b in i:
			d = dblocks[0]
			print "%u<->%u" % (b, d)
			fs.swapBlocks(b, d)
			dblocks.pop(0)

except ext2.Ext2Error, e:
	print e.str()
except IndexError:
	print "Please supply the filename of an unmounted ext2 partition"
