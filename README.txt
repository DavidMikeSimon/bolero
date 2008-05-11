To build the pyext2 library, just go in to its directory and run the "build.sh" script. A better build system will be used later.

Here is a quick overview of the python scripts included here:
- analyzetimes.py : Given one or more files containing one testing time per line, produces a report about those times.
- bswap.py : Swaps individual given blocks in a filesystem.
- defragment.py : Defragments an entire filesystem. This is only a test implementation; it is NOT a good general defragmenter.
- enfragment.py : Randomly shuffles the blocks in a filesystem.
- frecord.py : Once started, notices any new processes that start up and records which files they have open and when.
- fsummarize.py : Given the output of several runs of frecord on the same program, produces a best-guess list for what order the files will be loaded in.
- fview.py : Given the output of a run of frecord, prints out details.
- groupscan.py : Prints out information about inode/block assocation within each group of a given filesystem.
- iscan.py : Prints out information about a particular numbered inode in a given filesystem.
- listdefrag.py : Given a list of files as produced by fsummarize, organizes a filesystem so that those files are sequential and in the given order.
- listscan.py : Given a list of files as produced by fsummarize, prints out information about them within a given filesystem.
- scan.py : Prints out lots of information about a given filesystem.
