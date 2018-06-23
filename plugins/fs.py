#!/usr/env/python3
import os

# Shows filesystem statistics by disk mount point
# args: mount point, e.g. / or /mnt/something
# result:
#   .free_inodes: 157704485      # count of free inodes
#   .free_inodes_percent: 99.71  # % of free inodes
#   .free_size_mb: 161089585152     # free space on disk, in megabytes
#   .free_size_percent: 32.21    # % of free space on disk


#  struct statvfs {
#                unsigned long  f_bsize;    /* Filesystem block size */
#                unsigned long  f_frsize;   /* Fragment size */
#                fsblkcnt_t     f_blocks;   /* Size of fs in f_frsize units */
#                fsblkcnt_t     f_bfree;    /* Number of free blocks */
#                fsblkcnt_t     f_bavail;   /* Number of free blocks for
#                                              unprivileged users */
#                fsfilcnt_t     f_files;    /* Number of inodes */
#                fsfilcnt_t     f_ffree;    /* Number of free inodes */
#                fsfilcnt_t     f_favail;   /* Number of free inodes for
#                                              unprivileged users */
#                unsigned long  f_fsid;     /* Filesystem ID */
#                unsigned long  f_flag;     /* Mount flags */
#                unsigned long  f_namemax;  /* Maximum filename length */
#            };
def disk_stat(path):
    stat = os.statvfs(path)

    fragment_size = stat.f_frsize
    total_size = fragment_size * stat.f_blocks
    free_size = fragment_size * stat.f_bavail
    total_inodes = stat.f_files
    free_inodes = stat.f_favail

    return {
        'free_size_mb': round(free_size / 1024 / 1024),
        'free_size_percent': round(100 * free_size / total_size, 2),
        'free_inodes': free_inodes,
        'free_inodes_percent': round(100 * free_inodes / total_inodes, 2)
    }


def stats(args):
    return {
        'done': lambda: True,
        'value': lambda: disk_stat(args[0]),
        'status': lambda: 0,
        'kill': lambda: None,
        'msg': lambda: "OK"
    }
