#!/usr/bin/python

import sys, numpy, pylab, matplotlib, re

pat = re.compile(r"[^-]+-[^-]+-(\S+)")

# First pass: Figure out the minimum and maximum values
vmin, vmax = -1, -1
for name in sys.argv[1:]:
	match = pat.match(name)
	if match:
		fh = open(name)
		vals = []
		for line in fh:
			vals.append(int(line.strip())/1000.0)
		
		if vmin == -1:
			vmin = numpy.min(vals)
		else:
			vmin = min(numpy.min(vals), vmin)
		
		if vmax == -1:
			vmax = numpy.max(vals)
		else:
			vmax = max(numpy.max(vals), vmax)
		
		fh.close()
binwidth = (vmax-vmin)/200.0

# Second pass: Generate the plots
fig = pylab.figure(facecolor = "white")
a1rect = (0.09, 0.08, 0.67, 0.85)
a2rect = (0.82, 0.08, 0.16, 0.85)
lines = []
ptitles = []
n = 0
for name in sys.argv[1:]:
	match = pat.match(name)
	if match:
		fh = open(name)
		vals = []
		for line in fh:
			vals.append(int(line.strip())/1000.0)
		
		# Time graph
		chr = ('x', 'o', 's')[n]
		n += 1
		a = fig.add_axes(a1rect)
		lines.append(a.plot(vals, chr))
		
		# Histogram
		flabels = []
		fvals = []
		x = vmin
		while x < vmax:
			flabels.append(x + binwidth/2)
			fvals.append(len([v for v in vals if v >= x and v < (x+binwidth)]))
			x += binwidth
		a = fig.add_axes(a2rect)
		a.plot(fvals, flabels, '-')
		
		ptitles.append(match.group(1))
		fh.close()

# Time graph
a = fig.add_axes(a1rect)
a.set_xlabel('Test #')
a.set_ylabel('Elapsed (sec)')

# Frequency graph
a = fig.add_axes(a2rect)
a.set_title("Distribution")
a.set_xticks([])

fig.legend(lines, ptitles, 'upper center', prop = matplotlib.font_manager.FontProperties(size='smaller'))
pylab.show()
