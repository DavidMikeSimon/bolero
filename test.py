#!/usr/bin/python

import ext2.ext2

try:
	fs = ext2.Fs("../testpart")
	while (fs.scanning()):
		pass
	for e, i in enumerate(fs.inodes()):
		if e == 0: continue
		print "#%03u: Links:%u Blocks:%u File:%u Dir:%u" % (e, len(i.links()), len(i.blocks()), i.is_reg(), i.is_dir())
except ext2.Ext2Error, e:
	print e.str()
