
%module ext2
%{
#include "ext2.h"
%}

%include "std_string.i"
%include "std_vector.i"

namespace std {
   %template(inodevector) vector<Inode>;
   %template(dirrefvector) vector<DirRef>;
   %template(blkrefvector) vector<BlkRef>;
   %template(direntryvector) vector<DirEntry>;
   %template(uint32vector) vector<unsigned long>;
};

%include "ext2.h"
