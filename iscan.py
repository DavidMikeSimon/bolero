#!/usr/bin/python

import sys,re
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
	pat = re.compile(r"\d+")
	inodes = fs.inodes()
	for n in sys.argv[2:]:
		match = pat.match(n)
		if match:
			i = inodes[int(n)]
			print "#%03u: Links:%u Blocks:%u File:%u Dir:%u" % (int(n), len(i.links()), len(i.blocks()), i.is_reg(), i.is_dir())
			if len(i.blocks()) > 0:
				print "   ^ Blocks:" + ",".join(str(v) for v in i.blocks())
			if i.is_dir():
				print "   ^ DEntrs:" + ",".join(v for v in i.dirEntries())
			if len(i.links()) > 0:
				print "   ^  Links:" + ",".join(v.entry for v in i.links())
	print
	print "TOTAL BLOCKS: %u" % fs.blocksCount()
	print "TOTAL INODES: %u" % fs.inodesCount()
except ext2.Ext2Error, e:
	print e.str()
except IndexError:
	print "Please supply the filename of an unmounted ext2 partition as the first argument, and block numbers as subsequent arguments"
