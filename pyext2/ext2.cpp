// Based partially upon code from "resize" in the e2fsprogs package

#include <unistd.h>
#include <stdlib.h>
#include <sstream>
#include <algorithm>

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
	
	// If referencer is an indirect block, we get roffset in bytes, but we want it in address length units
	if (rblk != 0) { roffset /= sizeof(blk_t); }
	// Mark this block with a link back to referencing block or inode
	env->fs->m_blkRefs[*blocknr] = BlkRef(env->inum, env->inode->m_blocks.size()-1, rblk, roffset);
	// Mark referencing block (if any) with a link to this block
	if (rblk != 0) { env->fs->m_indirectBlkEntries[rblk].push_back(*blocknr); }
	
	return 0;
}

int Inode::dirIteration(ext2_dir_entry* dirent, int offset, int blocksize, char* buf, void* prv) {
	iteration_env* env = reinterpret_cast<iteration_env*>(prv);
	
	// FIXME: This appears to be buggy. That's why the dirEntry scanning part of scan.py is commented out.
	
	env->inode->m_dirEntries.push_back(DirEntry(std::string(dirent->name, dirent->name_len), dirent->inode)); 
	env->fs->m_inodes[dirent->inode].m_links.push_back(DirRef(env->inum, env->inode->m_dirEntries.size()-1)); // Add backlink to target inode
	
	return 0;
}

void Inode::scanInode(Fs& fs, ext2_ino_t inum, ext2_inode& inode) {
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

void Fs::assertSwappableBlock(unsigned long blk) {
	// isSwappableBlock calls assertValidBlock in turn
	if (!isSwappableBlock(blk)) { throw Ext2Error("Invalid data block index", blk); }
}

void Fs::assertValidBlock(unsigned long blk) {
	if (blk == 0 || blk >= blocksCount()) { throw Ext2Error("Invalid block index", blk); }
}

void Fs::assertValidInode(unsigned long ino) {
	if (ino == 0 || ino > inodesCount()) { throw Ext2Error("Invalid inode index", ino); }
}

void Fs::assertScanned() {
	if (!m_scanned) { throw Ext2Error("Operation requires that filesystem was scanned, but it hasn't been", 0); }
}

void Fs::assertConsistency() {
	std::vector<unsigned long> seenBlocks = std::vector<unsigned long>(blocksCount(), 0);
	for (unsigned long i = 0; i < m_inodes.size(); ++i) {
		for (unsigned long b = 0; b < m_inodes[i].m_blocks.size(); ++b) {
			if (seenBlocks[m_inodes[i].m_blocks[b]] > 0) {
				printf("Inconsistency: Block %u is referenced from both inodes %u and %u!\n",
					m_inodes[i].m_blocks[b], seenBlocks[m_inodes[i].m_blocks[b]], i);
				throw Ext2Error("Inconsistency detected", 0);
			} else {
				seenBlocks[m_inodes[i].m_blocks[b]] = i;
			}
			
			if (m_blkRefs[m_inodes[i].m_blocks[b]].inode != i) {
				printf("Inconsistency: Block %u is supposed to be owned by inode %u, but BlkRef disagrees!\n", m_inodes[i].m_blocks[b], i);
				throw Ext2Error("Inconsistency detected", 1);
			}
		}
	}
	
	for (unsigned long i = 0; i < m_blkRefs.size(); ++i) {
		if (m_blkRefs[i].inode != 0) {
			if (m_inodes[m_blkRefs[i].inode].m_blocks[m_blkRefs[i].index] != i) {
				printf("Inconsistency: Block %u was supposed to be at inode %u index %u, but wasn't!\n", i, m_blkRefs[i].inode, m_blkRefs[i].index);
				throw Ext2Error("Inconsistency detected", 2);
			}
			
			if (m_blkRefs[i].rblk != 0) {
				if (m_indirectBlkEntries[m_blkRefs[i].rblk][m_blkRefs[i].offset] != i) {
					printf("Inconsistency: Block %u was supposed to be at indirectBlkEntries[%u][%u], but wasn't!\n", i, m_blkRefs[i].rblk, m_blkRefs[i].offset);
					throw Ext2Error("Inconsistency detected", 3);
				}
			}
		} else {
			if (m_blkRefs[i].index != 0 || m_blkRefs[i].rblk != 0 || m_blkRefs[i].offset != 0) {
				printf("Inconsistency: Block %u has a BlkRef with an inode of 0 but other non-zero information!\n", i);
				throw Ext2Error("Inconsistency detected", 4);
			}
		}
	}
	
	for (unsigned long i = 0; i < m_indirectBlkEntries.size(); ++i) {
		for (unsigned long b = 0; b < m_indirectBlkEntries[i].size(); ++b) {
			if (m_blkRefs[m_indirectBlkEntries[i][b]].rblk != i) {
				printf("Inconsistency: Block %u was supposed to have rblk of %u, but instead it was %u!\n",
					m_indirectBlkEntries[i][b], i, m_blkRefs[m_indirectBlkEntries[i][b]].rblk);
				throw Ext2Error("Inconsistency detected", 5);
			}
		}
	}
}

// Lets us write/read addresses from indirect reference blocks being accessed as arrays of unsigned char
union UBlkAddr {
	blk_t addr;
	unsigned char bytes[sizeof(blk_t)];
};

// Changes the indicated block reference to point to blk
// Doesn't change the contents of any pyext2 structures, just the real ext2 structures they represent
void Fs::alterBlockRef(const BlkRef& blkRef, unsigned long blk) {
	errcode_t e;
	if (blkRef.rblk == 0) {
		m_inodes[blkRef.inode].m_e2inode.i_block[blkRef.offset] = blk;
		e = ext2fs_write_inode(m_e2fs, blkRef.inode, &m_inodes[blkRef.inode].m_e2inode);
		if (e) { throw Ext2Error("Unable to write inode table entry. FS is probably inconsistent now!", blkRef.inode); }
	} else {
		// This is a silly and somewhat wasteful way of doing this, but it's simple
		unsigned char buf[m_e2fs->blocksize];
		e = io_channel_read_blk(m_e2fs->io, blkRef.rblk, 1, buf);
		if (e) { throw Ext2Error("Couldn't read indirect reference block", e); }
		UBlkAddr u;
		u.addr = blk;
		// FIXME: This kind of thing probably causes an endianness bug
		for (int i = 0; i < sizeof(blk_t); ++i) {
			buf[blkRef.offset*sizeof(blk_t) + i] = u.bytes[i];
		}
		e = io_channel_write_blk(m_e2fs->io, blkRef.rblk, 1, buf);
		if (e) { throw Ext2Error("Failed writing to indirect reference block. FS is probably inconsistent now!", e); }
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
		throw Ext2Error("Filesystem's state is dirty. Perhaps it's mounted or needs to be fscked", 0);
	}
	
	m_inodes = std::vector<Inode>(m_e2fs->super->s_inodes_count+1); // There is no inode 0, so the first real inode is at index 1.
	m_blkRefs = std::vector<BlkRef>(m_e2fs->super->s_blocks_count); // FIXME: Vector might be the wrong data structure for this
	m_indirectBlkEntries = std::vector< std::vector<unsigned int> >(m_e2fs->super->s_blocks_count); // FIXME: Vector is the wrong data structure for this
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
			m_inodes[inum].scanInode(*this, inum, inode);
		}
		++n;
	}
	return true;
}

void Fs::swapInodes(unsigned long a, unsigned long b) throw(Ext2Error) {
	assertValidInode(a);
	assertValidInode(b);
	assertScanned();

	// TODO: Implement
}

void Fs::swapBlocks(unsigned long a, unsigned long b) throw(Ext2Error) {
	assertSwappableBlock(a);
	assertSwappableBlock(b);
	assertScanned();

	if (a == b) {
		// Well, looks like my work here is done. No, no need for thanks, good citizen. Just doing my job.
		return;
	}
	
	// Read in the data from the blocks
	errcode_t e;
	unsigned char buf_a[m_e2fs->blocksize], buf_b[m_e2fs->blocksize];
	e = io_channel_read_blk(m_e2fs->io, a, 1, buf_a);
	if (e) { throw Ext2Error("Couldn't read block a", e); }
	e = io_channel_read_blk(m_e2fs->io, b, 1, buf_b);
	if (e) { throw Ext2Error("Couldn't read block b", e); }
	
	// Update the block usage bitmap with the newly swapped values, if necessary
	bool a_used = isBlockUsed(a);
	bool b_used = isBlockUsed(b);
	if (a_used && !b_used) {
		ext2fs_unmark_block_bitmap(m_e2fs->block_map, a);
		ext2fs_mark_block_bitmap(m_e2fs->block_map, b);
		ext2fs_mark_bb_dirty(m_e2fs);
	} else if (!a_used && b_used) {
		ext2fs_mark_block_bitmap(m_e2fs->block_map, a);
		ext2fs_unmark_block_bitmap(m_e2fs->block_map, b);
		ext2fs_mark_bb_dirty(m_e2fs);
	}
	
	// Write the data back out to new blocks
	e = io_channel_write_blk(m_e2fs->io, a, 1, buf_b);
	if (e) { throw Ext2Error("Failed writing to block a. FS is probably inconsistent now!", e); }
	e = io_channel_write_blk(m_e2fs->io, b, 1, buf_a);
	if (e) { throw Ext2Error("Failed writing to block b. FS is probably inconsistent now!", e); }
	
	// Update references among inodes (and possibly indirect reference blocks) that own these blocks
	if (m_blkRefs[a].inode != 0) {
		m_inodes[m_blkRefs[a].inode].m_blocks[m_blkRefs[a].index] = b;
		if (m_blkRefs[a].rblk != 0) {
			m_indirectBlkEntries[m_blkRefs[a].rblk][m_blkRefs[a].offset] = b;
		}
	}
	if (m_blkRefs[b].inode != 0) {
		m_inodes[m_blkRefs[b].inode].m_blocks[m_blkRefs[b].index] = a;
		if (m_blkRefs[b].rblk != 0) {
			m_indirectBlkEntries[m_blkRefs[b].rblk][m_blkRefs[b].offset] = a;
		}
	}
	
	// Swap m_blkRef entries
	BlkRef a_ref = m_blkRefs[a];
	BlkRef b_ref = m_blkRefs[b];
	m_blkRefs[a] = b_ref;
	m_blkRefs[b] = a_ref;
	
	// Also need to alter any m_blkRefs that mention being referenced by these blocks, if these blocks are themselves indirect reference blocks
	for (std::vector<unsigned int>::iterator i = m_indirectBlkEntries[a].begin(); i != m_indirectBlkEntries[a].end(); ++i) {
		m_blkRefs[*i].rblk = b;
	}
	for (std::vector<unsigned int>::iterator i = m_indirectBlkEntries[b].begin(); i != m_indirectBlkEntries[b].end(); ++i) {
		m_blkRefs[*i].rblk = a;
	}
	m_indirectBlkEntries[a].swap(m_indirectBlkEntries[b]);
	
	// Finally, update the actual filesystem to match the new pyext2 state
	if (m_blkRefs[a].inode != 0) { alterBlockRef(m_blkRefs[a], a); }
	if (m_blkRefs[b].inode != 0) { alterBlockRef(m_blkRefs[b], b); }
	
	//assertConsistency();
}

bool Fs::isSwappableBlock(unsigned long blk) throw(Ext2Error) {
	assertValidBlock(blk);
	// It's a swappable block if it's unused, or if it is referenced by any inode, except for inode 7.
	// Inode 7 is the "reserved group descriptors" inode, which I'm unclear on the purpose of...
	// However, attempting to alter it often results in inconsistencies in the filesystem (undocumented libext2fs activity, maybe?)
	return (!ext2fs_test_block_bitmap(m_e2fs->block_map, blk)) || (m_blkRefs[blk].inode != 0 && m_blkRefs[blk].inode != 7);
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
	ext2fs_close_inode_scan(m_e2scan);
	io_channel_flush(m_e2fs->io);
	ext2fs_close(m_e2fs);
}
