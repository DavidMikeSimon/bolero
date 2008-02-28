#include <unistd.h>
#include <stdlib.h>
#include <sstream>

#include "ext2.h"

//
// Ext2Error
//

std::string Ext2Error::str() {
	std::ostringstream oss;
	oss << m_code;
	return m_msg + std::string(" -- Error ") + oss.str();
}

//
// Inode
//

int Inode::block_iteration(ext2_filsys e2fs, blk_t* blocknr, int blockcnt, void* prv) {
	reinterpret_cast<Inode*>(prv)->m_blocks.push_back(*blocknr);
	return 0;
}

int Inode::dir_iteration(ext2_dir_entry* dirent, int offset, int blocksize, char* buf, void* prv) {
	reinterpret_cast<Inode*>(prv)->m_dirEntries.push_back(DirEntry(std::string(dirent->name, dirent->name_len), dirent->inode));
	return 0;
}

void Inode::set_inode(Fs& fs, ext2_ino_t inum, ext2_inode& inode) {
	m_e2inode = inode;
	ext2fs_block_iterate(fs.m_e2fs, inum, 0, NULL, &block_iteration, this);
	for (unsigned long i = 0; i < m_blocks.size(); ++i) {
		fs.m_usedBlocks[m_blocks[i]] = 1;
	}
	if (is_dir()) {
		ext2fs_dir_iterate(fs.m_e2fs, inum, 0, NULL, &dir_iteration, this);
		for (unsigned long i = 0; i < m_dirEntries.size(); ++i) {
			fs.m_inodes[m_dirEntries[i].inode()].m_links.push_back(DirRef(inum, i));
		}
	}
}

std::string Inode::data() {
	
}

bool Inode::is_sock() {
	return LINUX_S_ISSOCK(m_e2inode.i_mode);
}

bool Inode::is_lnk() {
	return LINUX_S_ISLNK(m_e2inode.i_mode);
}

bool Inode::is_reg() {
	return LINUX_S_ISREG(m_e2inode.i_mode);
}

bool Inode::is_blk() {
	return LINUX_S_ISBLK(m_e2inode.i_mode);
}

bool Inode::is_dir() {
	return LINUX_S_ISDIR(m_e2inode.i_mode);
}

bool Inode::is_chr() {
	return LINUX_S_ISCHR(m_e2inode.i_mode);
}

bool Inode::is_fifo() {
	return LINUX_S_ISFIFO(m_e2inode.i_mode);
}

Inode::~Inode() {
}

//
// Fs
//

Fs::Fs(const std::string& path) throw(Ext2Error) {
	//FIXME: Check here if the filesystem is mounted before trying to open (see how ext2resize does it)
	
	errcode_t e = ext2fs_open(
		path.c_str(),
		EXT2_FLAG_RW | EXT2_FLAG_EXCLUSIVE,
		0,
		0,
		unix_io_manager,
		&m_e2fs);
	
	if (e) { throw Ext2Error("Error while opening filesystem", e); }
	
	// There is no inode 0, so the first real inode is at index 1.
	m_inodes = std::vector<Inode>(m_e2fs->super->s_inodes_count+1);

	// FIXME: This needs to figure out which blocks are occupied by metadata and other stuff
	// However, i'm not sure whether the "blocks" referred to in inodes are physical blocks or just include potential data blocks
	// Either figure out the pattern for that, or figure out how to read the blocks bitmap from the filesystem
	m_usedBlocks = std::vector<bool>(m_e2fs->super->s_blocks_count);
	
	e = ext2fs_open_inode_scan(m_e2fs, 0, &m_e2scan);
	if (e) { 
		ext2fs_close(m_e2fs);
		throw Ext2Error("Error while creating inode scanner", e);
	}
}

bool Fs::scanning() throw(Ext2Error) {
	unsigned int n = 0;
	while (n <= 100) {
		ext2_ino_t inum;
		ext2_inode inode;
		errcode_t e = ext2fs_get_next_inode(m_e2scan, &inum, &inode);
		if (e) {
			ext2fs_close(m_e2fs);
			throw Ext2Error("Error while scanning inodes", e);
		}
		if (inum == 0) {
			// ext2fs_get_next_inode has reached the end of the table
			return false;
		}
		m_inodes[inum].set_inode(*this, inum, inode);
		++n;
	}
	return true;
}

Fs::~Fs() {
	ext2fs_close_inode_scan(m_e2scan);
	ext2fs_close(m_e2fs);
}
