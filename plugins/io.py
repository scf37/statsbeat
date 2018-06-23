#!/usr/env/python3
import time

# Collects CPU utilization in percents (0-100) for most loaded core and total
#

diskstats_fields = ['major', 'minor', 'device',
                   'reads_completed', 'reads_merged',
                   'sectors_read', 'time_spent_reading_ms',
                   'writes_completed', 'writes_merged',
                   'sectors_written', 'time_spent_writing_ms',
                   'inflight_ios', 'io_time_ms',
                   'weighted_time_spent_io']

device_stats_prev = {}
last_ts = {}


def load_diskstats():
    def parse_line(l):
        ll = l.strip().split()
        r = {}
        for i in range(0, len(diskstats_fields)):
            r[diskstats_fields[i]] = ll[i]
        return r

    with open("/proc/diskstats") as f:
        return [parse_line(l) for l in map(lambda l: l.strip(), f.readlines())]


def io_stats(device):
    global device_stats_prev, last_ts

    device_stats = list(filter(lambda s: s['device'] == device, load_diskstats()))
    if len(device_stats) == 0:
        raise Exception("Device not found: " + device)
    device_stats = device_stats[0]

    if device_stats_prev.get(device) is None:
        device_stats_prev[device] = device_stats
        last_ts[device] = time.monotonic()
        return {
            'iops_read': None,
            'iops_write': None,
            'utilization_percent': None
        }

    ts = time.monotonic()
    delta_ms = (ts - last_ts[device]) * 1000

    io_time_ms = int(device_stats['io_time_ms'])
    io_time_ms_prev = int(device_stats_prev[device]['io_time_ms'])
    utilization_percent = round(100 * (io_time_ms - io_time_ms_prev) / delta_ms, 2)

    reads = int(device_stats['reads_completed'])
    reads_prev = int(device_stats_prev[device]['reads_completed'])
    writes = int(device_stats['writes_completed'])
    writes_prev = int(device_stats_prev[device]['writes_completed'])

    iops_read = round(1000 * (reads - reads_prev) / delta_ms)
    iops_write = round(1000 * (writes - writes_prev) / delta_ms)

    device_stats_prev[device] = device_stats
    last_ts[device] = ts

    return {
        'iops_read': iops_read,
        'iops_write': iops_write,
        'utilization_percent': utilization_percent
    }


def stats(args):
    return {
        'done': lambda: True,
        'value': lambda: io_stats(args[0]),
        'status': lambda: 0,
        'kill': lambda: None,
        'msg': lambda: "OK"
    }
