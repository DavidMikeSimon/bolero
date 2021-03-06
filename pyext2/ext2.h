// Based partially upon code from "resize" in the e2fsprogs package

#include <ext2fs/ext2_fs.h>
#include <ext2fs/ext2fs.h>
#include <string>
#include <vector>
#include <map>

class Ext2Error;
class Inode;
class Fs;

//Exception class representing when something has gone terribly wrong
class Ext2Error {
		std::string m_msg;
		unsigned long m_code;
	public:
		const std::string& msg() const { return m_msg; }
		unsigned long code() const { return m_code; }
		std::string str();
		Ext2Error(const std::string& in_msg, errcode_t in_code) { m_msg = in_msg; m_code = in_code; }
};

// Represents some dir entry in some directory Inode
struct DirRef {
	unsigned long inode;
	std::string entry;
	DirRef() { inode = 0; entry = std::string(); }
	DirRef(unsigned long in_inode, const std::string& in_entry) { inode = in_inode; entry = in_entry; }
};

// Represents where some data or indirection block is referenced from
struct BlkRef {
	unsigned long inode; // Index in the Fs's m_inodes vector (aka, the inum)
	unsigned long index; // Index in the Inode's m_blocks vector
	unsigned long rblk; // Index of referencing block. If 0, then target block is directly referenced from Inode.
	unsigned long offset; // Offset into whatever is referred to by rblk, in units of address length
	BlkRef() { inode = 0; index = 0; rblk = 0; offset = 0; }
	BlkRef(unsigned long in_inode, unsigned long in_index, unsigned long in_rblk, unsigned long in_offset) {
		inode = in_inode; index = in_index; rblk = in_rblk; offset = in_offset;
	}
};

class Inode {
	private:
		struct ext2_inode m_e2inode;
		std::vector<unsigned long> m_blocks;
		std::map<std::string, unsigned long> m_dirEntries; //Filenames to inode numbers
		std::vector<DirRef> m_links; //Which directory inodes link to this inode
		
		static int blockIteration(ext2_filsys e2fs, blk_t* blocknr, e2_blkcnt_t blockcnt, blk_t rblk, int roffset, void* prv);
		static int dirIteration(ext2_dir_entry* dirent, int offset, int blocksize, char* buf, void* prv);
		void scanInode(Fs& fs, ext2_ino_t inum, ext2_inode& inode); // Used during scanning process when in-use inodes encountered
	public:
		// Please do not use this constructor in client code, it is public so that STL code may work
		Inode() {}
		
		const std::vector<unsigned long>& blocks() { return m_blocks; }
		const std::map<std::string, unsigned long>& dirEntries() { return m_dirEntries; }
		const std::vector<DirRef>& links() { return m_links; }
		bool is_sock(); //Is it a socket?
		bool is_lnk(); //Is it a symlink?
		bool is_reg(); //Is it a regular file?
		bool is_blk(); //Is it a block device?
		bool is_dir(); //Is it a directory?
		bool is_chr(); //Is it a character device?
		bool is_fifo(); //Is it a FIFO?
		~Inode();
		
		friend class Fs;
};

class Fs {
	private:
		ext2_filsys m_e2fs;
		ext2_inode_scan m_e2scan;
		std::map<unsigned long, Inode> m_inodes;
		std::map<unsigned long, BlkRef> m_blkRefs;
		std::map<unsigned long, std::vector<unsigned long> > m_indirectBlkEntries; //Mapping of indirect reference blocks to their entries
		bool m_scanned;
		bool m_readonly;
		
		Fs(const Fs& other) throw(Ext2Error) { throw Ext2Error("Cannot copy Fs object", 0); }
		void assertSwappableBlock(unsigned long blk);
		void assertValidBlock(unsigned long blk);
		void assertValidInode(unsigned long ino);
		void assertScanned();
		void assertConsistency();
		void assertWritable();
		void alterBlockRef(const BlkRef& blkRef, unsigned long blk);
	public:
		Fs(const std::string& path, bool readonly = false) throw(Ext2Error);
		bool scanning() throw(Ext2Error); // Scans some of the filesystem. Returns true if more scanning needed, false when finished.
		void swapInodes(unsigned long a, unsigned long b) throw(Ext2Error); // Swaps two inode entries, updates all references from directory tables
		void swapBlocks(unsigned long a, unsigned long b) throw(Ext2Error); // Swaps two data blocks, updates all references from inodes, bitmaps, etc.
		const std::map<unsigned long, Inode>& inodes() { return m_inodes; } // Allows you to scan through the inode table
		const std::map<unsigned long, BlkRef>& blockRefs() { return m_blkRefs; } // Allows you to scan through the block reference table
		bool isSwappableBlock(unsigned long blk) throw(Ext2Error); // Returns true if the given block can be swapped
		bool isBlockUsed(unsigned long blk) throw(Ext2Error); // Returns true if the given block is in use, false otherwise
		bool isInodeUsed(unsigned long ino) throw(Ext2Error); // Returns true if the given inode is in use, false otherwise
		unsigned long groupOfBlock(unsigned long blk) throw(Ext2Error); // Returns which group contains the given block, starting with group 0
		unsigned long groupOfInode(unsigned long ino) throw(Ext2Error); // Returns which group contains the given inode, starting with group 0
		unsigned long blockOfGroup(unsigned long grp) throw(Ext2Error); // Returns the first block of a given group
		unsigned long blocksCount(); // Returns the total number of blocks, free or used. Valid block indexes are 1 .. blocksCount-1
		unsigned long inodesCount(); // Returns the total number of inodes, free or used. Valid inode indexes are 1 .. inodesCount
		unsigned long pathToInum(const std::string& path); // Resolves an absolute path into an inode number, returns 0 on failed lookup
		~Fs();
		
		friend class Inode;
};
