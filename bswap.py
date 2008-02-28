#!/usr/bin/python

import sys
from pyext2 import ext2

try:
	fs = ext2.Fs(sys.argv[1])
	while (fs.scanning()):
		pass
	a = int(sys.argv[2])
	b = int(sys.argv[3])
	if a < 0 or b < 0 or a == b or a >= len(fs.usedBlocks()) or b >= len(fs.usedBlocks()):
		raise IndexError()
	fs.swapBlocks(a, b)
except ext2.Ext2Error, e:
	print e.str()
except IndexError:
	print "Please supply the filename of an unmounted ext2 partition, and two valid block indexes to swap"
except ValueError:
	print "Please supply the filename of an unmounted ext2 partition, and two valid block indexes to swap"
