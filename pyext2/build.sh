#!/bin/sh

swig -python -c++ ext2.i
g++ -shared -fpic ext2.cpp ext2_wrap.cxx -I/usr/include/python2.5/ -lext2fs -o _ext2.so
