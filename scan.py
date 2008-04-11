#!/usr/bin/python

import sys
from pyext2 import ext2

# Although it is possible and safe to run this script on a mounted filesystem, if that filesystem changes during the scan, output is not to be trusted
# The worst that can happen, though, is that scan will crash; the filesystem is opened read-only by this script, so no worries

try:
	sys.stdout.write("Initializing...")
	fs = ext2.Fs(sys.argv[1], True)
	sys.stdout.write("\n")
	sys.stdout.write("Scanning...")
	while (fs.scanning()):
		sys.stdout.write(".")
		sys.stdout.flush()
	sys.stdout.write("\n")
	for e, i in fs.inodes().iteritems():
		print "#%03u: Links:%u Blocks:%u File:%u Dir:%u" % (e, len(i.links()), len(i.blocks()), i.is_reg(), i.is_dir())
		if len(i.blocks()) > 0:
			print "   ^ Blocks:" + ",".join(str(v) for v in i.blocks())
		if i.is_dir():
			print "   ^ DEntrs:" + ",".join(v.name() for v in i.dirEntries())
	print
	print "REFERENCED BLOCKS: " + ",".join(str(i) for i in fs.blockRefs())
	print "USED BLOCKS: " + ",".join(str(i) for i in range(1, fs.blocksCount()) if fs.isBlockUsed(i))
	print "TOTAL BLOCKS: %u" % fs.blocksCount()
	print "TOTAL INODES: %u" % fs.inodesCount()
except ext2.Ext2Error, e:
	print e.str()
except IndexError:
	print "Please supply the filename of an unmounted ext2 partition"
