
%module ext2
%{
#include "ext2.h"
%}

%include "std_string.i"
%include "std_vector.i"
%include "std_map.i"

namespace std {
   %template(inodemap) map<unsigned long, Inode>;
   %template(dirrefvector) vector<DirRef>;
   %template(blkrefvector) map<unsigned long, BlkRef>;
   %template(direntryvector) map<std::string, unsigned long>;
   %template(uint32vector) vector<unsigned long>;
};

%include "ext2.h"
