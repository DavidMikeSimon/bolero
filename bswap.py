#!/usr/bin/python

import sys,re
from pyext2 import ext2

try:
	fs = ext2.Fs(sys.argv[1])
	while (fs.scanning()):
		pass
	pat = re.compile(r"(\d+),(\d+)")
	for i in sys.argv[2:]:
		match = pat.match(i)
		if match:
			a = int(match.group(1))
			b = int(match.group(2))
			print "%u <-> %u" % (a, b)
			fs.swapBlocks(a, b)
except ext2.Ext2Error, e:
	print e.str()
except IndexError:
	print "Please supply the filename of an unmounted ext2 partition, and pairs of valid block indexes to swap"
except ValueError:
	print "Please supply the filename of an unmounted ext2 partition, and pairs of valid block indexes to swap"
