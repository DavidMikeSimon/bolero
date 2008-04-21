#!/usr/bin/python

import sys
from pyext2 import ext2

# Although it is possible and safe to run this script on a mounted filesystem, if that filesystem changes during the scan, output is not to be trusted
# The worst that can happen, though, is that scan will crash; the filesystem is opened read-only by this script, so no worries

# Reports information about each group, particularly the degree to which the group's inodes own blocks within that same group

try:
	sys.stdout.write("Initializing...")
	fs = ext2.Fs(sys.argv[1], True)
	sys.stdout.write("\n")
	sys.stdout.write("Scanning...")
	while (fs.scanning()):
		sys.stdout.write(".")
		sys.stdout.flush()
	sys.stdout.write("\n")
	
	print "BLOCKCOUNT: %u" % fs.blocksCount()
	
	groups = {}
	for e, i in fs.inodes().iteritems():
		print "E: %u" % e
		gnum = fs.groupOfInode(e)
		if gnum not in groups:
			groups[gnum] = { 'inodes':0, 'unmatchBlocks':0, 'matchBlocks':0 }
		groups[gnum]['inodes'] += 1
		for b in i.blocks():
			print "  B: %u" % b
			if fs.groupOfBlock(b) == gnum:
				groups[gnum]['matchBlocks'] += 1
			else:
				groups[gnum]['unmatchBlocks'] += 1
	
	tMatch = 0
	tUnmatch = 0
	for gnum, g in groups.iteritems():
		print "GROUP %04u: %06u inodes with %8u/%8u in-group/out-group blocks" % (gnum, g['inodes'], g['matchBlocks'], g['unmatchBlocks']);
		tMatch += g['matchBlocks']
		tUnmatch += g['unmatchBlocks']
	
	print
	print "TOTAL GROUP-MATCHED BLOCKS:   %12u" % tMatch
	print "TOTAL GROUP-UNMATCHED BLOCKS: %12u" % tUnmatch
	print "GROUP-MATCHED BLOCKS: %.2f%%" % ((float(tMatch)/float(tMatch+tUnmatch))*100)
	print "TOTAL BLOCKS: %u" % fs.blocksCount()
	print "TOTAL INODES: %u" % fs.inodesCount()
except ext2.Ext2Error, e:
	print e.str()
except IndexError:
	print "Please supply the filename of an unmounted ext2 partition"
