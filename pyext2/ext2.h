#include <ext2fs/ext2_fs.h>
#include <ext2fs/ext2fs.h>
#include <string>
#include <vector>

class Ext2Error;
class DirEntry;
class Inode;
class Fs;

//Exception class representing when something has gone terribly wrong
class Ext2Error {
		std::string m_msg;
		int m_code;
	public:
		const std::string& msg() const { return m_msg; }
		const int code() const { return m_code; }
		std::string str();
		Ext2Error(const std::string& in_msg, errcode_t in_code) { m_msg = in_msg; m_code = in_code; }
};

class DirEntry {
	private:
		std::string m_name;
		unsigned long m_inode;
	public:
		DirEntry() {}
		DirEntry(const std::string& in_name, unsigned long in_inode) { m_name = in_name; m_inode = in_inode; }
		const std::string& name() { return m_name; }
		unsigned long inode() { return m_inode; }
};

// Represents some DirEntry in some Inode
struct DirRef {
	unsigned long inode;
	unsigned long entry;
	DirRef() { inode = 0; entry = 0; }
	DirRef(unsigned long in_inode, unsigned long in_entry) { inode = in_inode; entry = in_entry; }
};

class Inode {
	private:
		struct ext2_inode m_e2inode;
		std::vector<unsigned long> m_blocks;
		std::vector<DirEntry> m_dirEntries;
		std::vector<DirRef> m_links; //Which directory inodes link to this inode
		
		static int block_iteration(ext2_filsys e2fs, blk_t* blocknr, int blockcnt, void* prv);
		static int dir_iteration(ext2_dir_entry* dirent, int offset, int blocksize, char* buf, void* prv);
		void set_inode(Fs& fs, ext2_ino_t inum, ext2_inode& inode);
	public:
		Inode() {}
		const std::vector<unsigned long>& blocks() { return m_blocks; }
		const std::vector<DirEntry>& dirEntries() { return m_dirEntries; }
		const std::vector<DirRef>& links() { return m_links; }
		std::string data();
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
		std::vector<Inode> m_inodes;
		std::vector<bool> m_usedBlocks;
		
		Fs(const Fs& other) throw(Ext2Error) { throw Ext2Error("Cannot copy Fs object", 0); }
	public:
		Fs(const std::string& path) throw(Ext2Error);
		bool scanning() throw(Ext2Error); // Scans some of the filesystem. Returns true if more scanning needed, false when finished.
		const std::vector<Inode>& inodes() { return m_inodes; } // Allows you to scan through the inode table
		const std::vector<bool>& usedBlocks() { return m_usedBlocks; } //Allows you to check the free blocks table
		~Fs();
		
		friend class Inode;
};
