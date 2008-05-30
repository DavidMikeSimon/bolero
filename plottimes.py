#!/usr/bin/python

import sys, numpy, pylab, matplotlib, re

pat = re.compile(r"[^-]+-[^-]+-(\S+)")

lines = []
ptitles = []
for name in sys.argv[2:]:
	match = pat.match(name)
	if match:
		fh = open(name)
		vals = []
		for line in fh:
			vals.append(int(line.strip())/1000.0)
		
		# Time graph
		pylab.subplot(121)
		lines.append(pylab.plot(vals)) # Same line colors will show up in same order for frequency graph too
		pylab.plot(vals)
		
		# Frequency graph
		vmin, vmax = numpy.min(vals), numpy.max(vals)
		step = (vmax-vmin)/20.0
		flabels = []
		fvals = []
		x = vmin
		while x < vmax:
			flabels.append(x + step/2)
			fvals.append(len([v for v in vals if v >= x and v < (x+step)]))
			x += step
		pylab.subplot(122)
		pylab.plot(flabels, fvals)
		
		ptitles.append("%s - (Mean:%.3f StdDev:%.3f)" % (match.group(1), numpy.mean(vals), numpy.std(vals)))

# Time graph
pylab.title("In Sequence")
pylab.subplot(121)
pylab.xlabel('Test #')
pylab.ylabel('Elapsed (sec)')

# Frequency graph
pylab.title("By Frequency")
pylab.subplot(122)
pylab.xlabel('Elapsed (sec)')
pylab.ylabel('Frequency')

pylab.figlegend(lines, ptitles, 'upper right', prop = matplotlib.font_manager.FontProperties(size='smaller'))
pylab.show()
