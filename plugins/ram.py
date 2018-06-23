#!/usr/env/python3

# Shows RAM utilization
# result:
#    ram_free_mb:
#    ram_free_percent:
#    swap_free_mb:
#    swap_free_percent:


def mem():
    with open("/proc/meminfo") as f:
        values = dict([(l.split()[0], int(l.split()[1])) for l in f.readlines()])
    total = values['MemTotal:']
    free = values['MemAvailable:']
    swap_total = values['SwapTotal:']
    swap_free = values['SwapFree:']

    return {
        'ram_free_mb:': round(free / 1024),
        'ram_free_percent': round(100 * free / total, 2),
        'swap_free_mb': round(swap_free / 1024),
        'swap_free_percent': 100 if swap_total == 0 else round(100 * swap_free / swap_total, 2)
    }


def stats(args):
    return {
        'done': lambda: True,
        'value': lambda: mem(),
        'status': lambda: 0,
        'kill': lambda: None,
        'msg': lambda: "OK"
    }
