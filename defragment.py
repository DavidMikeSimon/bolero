#!/usr/bin/python

# TODO: This needs to do the following:
# - Notice when mid-disk blocks cannot be moved, and attempt to avoid letting them split a file into pieces
# - Try to move blocks so that they're near to the center of the disk, rather than right at the beginning
# - Move inode table entries as well (though, this first needs to be implemented in pyext2)

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
	
	iblocks = []
	for i in fs.inodes():
		for b in i.blocks():
			if fs.isSwappableBlock(b):
				iblocks.append(b)
	
	for d in dblocks:
		if len(iblocks) == 0:
			break
		b = iblocks.pop(0)
		print "%u<->%u" % (b, d)
		fs.swapBlocks(b, d)
		for idx in range(len(iblocks)):
			if iblocks[idx] == d:
				iblocks[idx] = b
				break

except ext2.Ext2Error, e:
	print e.str()
except IndexError:
	print "Please supply the filename of an unmounted ext2 partition"
