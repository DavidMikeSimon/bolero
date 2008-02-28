#!/usr/bin/python

import sys
from pyext2 import ext2

try:
	fs = ext2.Fs(sys.argv[1])
	while (fs.scanning()):
		pass
	for e, i in enumerate(fs.inodes()):
		if e == 0: continue
		print "#%03u: Links:%u Blocks:%u File:%u Dir:%u" % (e, len(i.links()), len(i.blocks()), i.is_reg(), i.is_dir())
		if len(i.blocks()) > 0:
			print "   " + ",".join(str(v) for v in i.blocks())
	print "USED BLOCKS:" + ",".join(str(i) for i, v in enumerate(fs.usedBlocks()) if v)
	print "TOTAL BLOCKS: %u" % (len(fs.usedBlocks()))
except ext2.Ext2Error, e:
	print e.str()
except IndexError:
	print "Please supply the filename of an unmounted ext2 partition"
