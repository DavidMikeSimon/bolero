
%module ext2
%{
#include "ext2.h"
%}

%include "std_string.i"
%include "std_vector.i"

namespace std {
   %template(inodevector) vector<Inode>;
   %template(direntryvector) vector<DirEntry>;
   %template(uintvector) vector<unsigned int>;
};

%include "ext2.h"
