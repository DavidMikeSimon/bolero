#!/usr/bin/python

import sys
from pyext2 import ext2

# Although it is possible and safe to run this script on a mounted filesystem, if that filesystem changes during the scan, output is not to be trusted
# The worst that can happen, though, is that scan will crash; the filesystem is opened read-only by this script, so no worries

try:
	listfh = open(sys.argv[2])
	
	sys.stdout.write("Initializing...")
	fs = ext2.Fs(sys.argv[1], True)
	sys.stdout.write("\n")
	sys.stdout.write("Scanning...")
	while (fs.scanning()):
		sys.stdout.write(".")
		sys.stdout.flush()
	sys.stdout.write("\n")
	
	inodes = fs.inodes()
	for line in listfh:
		path = line.strip()
		inum = fs.pathToInum(path)
		if inum != 0:
			i = inodes[int(n)]
			print "%s:" % path
			print "#%u: Group:%u Links:%04u Blocks:%u File:%u Dir:%u" % (fs.groupOfInode(inum), int(n), len(i.links()), len(i.blocks()), i.is_reg(), i.is_dir())
			if len(i.blocks()) > 0:
				groups = set()
				for v in i.blocks():
					groups.add(fs.groupOfBlock(v))
				print "   ^ Blocks In Groups: " + ",".join(("%04u" % g) for g in sorted(groups))
		else:
			print "ERROR: Couldn't resolve path %s" % path
except ext2.Ext2Error, e:
	print e.str()
except IndexError:
	print "Please supply the filename of an unmounted ext2 partition as the first argument, and a file containing a list of paths as the second"
except IOError:
	print "Please supply a file containing a list of paths as the second argument"
