#!/usr/env/python3

# Shows count of used file descriptors
#


def fd_used():
    with open("/proc/sys/fs/file-nr") as f:
        items = [int(v) for v in f.readline().strip().split()]

    return items[0] # number of allocated file handles


def stats(args):
    return {
        'done': lambda: True,
        'value': lambda: fd_used(),
        'status': lambda: 0,
        'kill': lambda: None,
        'msg': lambda: "OK"
    }
