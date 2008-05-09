#!/usr/bin/python

import sys
from pyext2 import ext2

try:
	listfh = open(sys.argv[2])
	
	sys.stdout.write("Initializing...")
	fs = ext2.Fs(sys.argv[1])
	sys.stdout.write("\n")
	sys.stdout.write("Scanning...")
	while (fs.scanning()):
		sys.stdout.write(".")
		sys.stdout.flush()
	sys.stdout.write("\n")
	
	# Create a list of all the blocks we're about to defragment, in the order they're supposed to be in
	iblocks = []
	for line in listfh:
		path = line.strip()
		inum = fs.pathToInum(path)
		if inum != 0:
			i = fs.inodes()[inum]
			for b in i.blocks():
				if fs.isSwappableBlock(b):
					iblocks.append(b)
				else:
					print "ERROR: Can't move desired source block %u, skipping" % s
		else:
			print "ERROR: Couldn't resolve path %s, skipping" % path
	
	# Find a suitable number of addressable blocks to use as a destination point
	# Start with the first block that any file we're manipulating starts with, and proceed linearly from there
	dblocks = []
	curdblock = (sorted(iblocks))[0]
	for i in range(0, len(iblocks)):
		while not fs.isSwappableBlock(curdblock):
			curdblock += 1
		dblocks.append(curdblock)
		curdblock += 1
	
	print "Beginning defragmentation..."
	
	for d in dblocks:
		if len(iblocks) == 0:
			break
		b = iblocks.pop(0)
		fs.swapBlocks(b, d)
		for idx in range(len(iblocks)):
			if iblocks[idx] == d:
				iblocks[idx] = b
				break

except ext2.Ext2Error, e:
	print e.str()
except IndexError:
	print "Please supply the filename of an unmounted ext2 partition as the first argument, and a file containing a list of paths as the second"
except IOError:
	print "Please supply a file containing a list of paths as the second argument"
