// Based partially upon code from "resize" in the e2fsprogs package

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

// This is passed to blockIteration and dirIteration so that they can get access to all the higher-level structures they need
struct iteration_env {
	Fs* fs;
	Inode* inode;
	ext2_ino_t inum;
};

int Inode::blockIteration(ext2_filsys e2fs, blk_t* blocknr, e2_blkcnt_t blockcnt, blk_t rblk, int roffset, void* prv) {
	iteration_env* env = reinterpret_cast<iteration_env*>(prv);
	
	env->inode->m_blocks.push_back(*blocknr);
	if (rblk != 0) { roffset /= sizeof(blk_t); } // If referencer is an indirect block, we get roffset in bytes, but we want it in address length units
	env->fs->m_blkRefs[*blocknr] = BlkRef(env->inum, env->inode->m_blocks.size()-1, rblk, roffset); // Mark target block with a link back to this inode
	
	return 0;
}

int Inode::dirIteration(ext2_dir_entry* dirent, int offset, int blocksize, char* buf, void* prv) {
	iteration_env* env = reinterpret_cast<iteration_env*>(prv);
	
	env->inode->m_dirEntries.push_back(DirEntry(std::string(dirent->name, dirent->name_len), dirent->inode)); 
	env->fs->m_inodes[dirent->inode].m_links.push_back(DirRef(env->inum, env->inode->m_dirEntries.size()-1)); // Add backlink to target inode
	
	return 0;
}

Inode::Inode(Fs& fs, ext2_ino_t inum, ext2_inode& inode) {
	m_e2inode = inode;
	
	iteration_env ienv;
	ienv.fs = &fs;
	ienv.inode = this;
	ienv.inum = inum;
	
	ext2fs_block_iterate2(fs.m_e2fs, inum, 0, NULL, &blockIteration, &ienv);
	if (is_dir()) { ext2fs_dir_iterate(fs.m_e2fs, inum, 0, NULL, &dirIteration, &ienv); }
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

void Fs::assertValidBlock(unsigned long blk) {
	if (blk == 0 || blk >= blocksCount()) { throw Ext2Error("Invalid block index", blk); }
}

void Fs::assertValidInode(unsigned long ino) {
	if (ino == 0 || ino > inodesCount()) { throw Ext2Error("Invalid inode index", ino); }
}

void Fs::assertScanned() {
	if (!m_scanned) { throw Ext2Error("Operation requires that filesystem was scanned, but it hasn't been", 0); }
}

// Changes the indicated block reference to point to blk
// Doesn't change the contents of the BlkRef structure itself
void Fs::alterBlockRef(const BlkRef& blkRef, unsigned long blk) {
	errcode_t e;
	if (blkRef.rblk == 0) {
		m_inodes[blkRef.inode].m_e2inode.i_block[blkRef.offset] = blk;
		e = ext2fs_write_inode(m_e2fs, blkRef.inode, &m_inodes[blkRef.inode].m_e2inode);
		if (e) { throw Ext2Error("Unable to write inode table entry. FS is probably inconsistent now!", blkRef.inode); }
	} else {
	}
}

Fs::Fs(const std::string& path) throw(Ext2Error) {
	errcode_t e = ext2fs_open(
		path.c_str(),
		EXT2_FLAG_RW | EXT2_FLAG_EXCLUSIVE,
		0,
		0,
		unix_io_manager,
		&m_e2fs);
	if (e) { throw Ext2Error("Error while opening filesystem (perhaps it's mounted or needs to be fscked)", e); }

	if (m_e2fs->super->s_state != EXT2_VALID_FS) {
		ext2fs_close(m_e2fs);
		throw Ext2Error("Filesystem's state is dirty. Perhaps it's mounted or needs to be fscked", m_e2fs->super->s_state);
	}
	
	m_inodes = std::vector<Inode>(m_e2fs->super->s_inodes_count+1); // There is no inode 0, so the first real inode is at index 1.
	m_blkRefs = std::vector<BlkRef>(m_e2fs->super->s_blocks_count);
	m_scanned = false;
	
	e = ext2fs_read_bitmaps(m_e2fs);
	if (e) {
		ext2fs_close(m_e2fs);
		throw Ext2Error("Error while reading inode/block bitmaps", e);
	}
	
	e = ext2fs_open_inode_scan(m_e2fs, 0, &m_e2scan);
	if (e) { 
		ext2fs_close(m_e2fs);
		throw Ext2Error("Error while creating inode scanner", e);
	}
}

bool Fs::scanning() throw(Ext2Error) {
	unsigned long n = 0;
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
			m_scanned = true;
			return false;
		}
		if (isInodeUsed(inum)) {
			m_inodes[inum] = Inode(*this, inum, inode);
		}
		++n;
	}
	return true;
}

void Fs::swapInodes(unsigned long a, unsigned long b) throw(Ext2Error) {
	assertValidInode(a);
	assertValidInode(b);
	assertScanned();
}

void Fs::swapBlocks(unsigned long a, unsigned long b) throw(Ext2Error) {
	assertValidBlock(a);
	assertValidBlock(b);
	assertScanned();
	
	// Read in the data from the blocks
	errcode_t e;
	unsigned char buf_a[m_e2fs->blocksize], buf_b[m_e2fs->blocksize];
	e = io_channel_read_blk(m_e2fs->io, a, 1, buf_a);
	if (e) { throw Ext2Error("Couldn't read inode a", e); }
	e = io_channel_read_blk(m_e2fs->io, b, 1, buf_b);
	if (e) { throw Ext2Error("Couldn't read inode b", e); }
	
	// Update the block usage bitmap with the newly swapped values, if necessary
	bool a_used = isBlockUsed(a);
	bool b_used = isBlockUsed(b);
	if (a_used && !b_used) {
		ext2fs_unmark_block_bitmap(m_e2fs->block_map, a);
		ext2fs_mark_block_bitmap(m_e2fs->block_map, b);
	} else if (!a_used && b_used) {
		ext2fs_mark_block_bitmap(m_e2fs->block_map, a);
		ext2fs_unmark_block_bitmap(m_e2fs->block_map, b);
	}
	
	// Update any references to these blocks in the inode table
	BlkRef a_ref = m_blkRefs[a];
	BlkRef b_ref = m_blkRefs[b];
	if (a_ref.inode != 0) { alterBlockRef(a_ref, b); }
	if (b_ref.inode != 0) { alterBlockRef(b_ref, a); }
	m_blkRefs[a] = b_ref;
	m_blkRefs[b] = a_ref;
	
	// Write the data back out to new blocks
	e = io_channel_write_blk(m_e2fs->io, a, 1, buf_b);
	if (e) { throw Ext2Error("Failed writing to inode a. FS is probably inconsistent now!", e); }
	e = io_channel_write_blk(m_e2fs->io, b, 1, buf_a);
	if (e) { throw Ext2Error("Failed writing to inode b. FS is probably inconsistent now!", e); }
}

bool Fs::isBlockUsed(unsigned long blk) throw(Ext2Error) {
	assertValidBlock(blk);
	return ext2fs_test_block_bitmap(m_e2fs->block_map, blk);
}

bool Fs::isInodeUsed(unsigned long ino) throw(Ext2Error) {
	assertValidInode(ino);
	return ext2fs_test_inode_bitmap(m_e2fs->inode_map, ino);
}

unsigned long Fs::blocksCount() {
	return m_e2fs->super->s_blocks_count;
}

unsigned long Fs::inodesCount() {
	return m_e2fs->super->s_inodes_count;
}

Fs::~Fs() {	
	io_channel_flush(m_e2fs->io);
	ext2fs_close_inode_scan(m_e2scan);
	ext2fs_close(m_e2fs);
}
