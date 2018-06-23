#!/usr/env/python3

# Collects CPU utilization in percents (0-100) for most loaded core and total
#

last_idle = {}
last_total = {}


def cpu_used():
    def load_average(line):
        global last_idle, last_total

        name = line[0]
        times = list(map(float, line[1:]))

        idle, total = times[3], sum(times)
        idle_delta, total_delta = idle - last_idle.get(name, 0), total - last_total.get(name, 0)

        last_idle[name], last_total[name] = idle, total

        if total_delta != 0:
            return round (100.0 * (1.0 - idle_delta / total_delta), 2)
        else:
            return 0

    with open("/proc/stat") as f:
        lines = [l.split() for l in filter(lambda l: l.startswith('cpu'), map(lambda l: l.strip(), f.readlines()))]

    cpu_used_total = load_average(lines[0])
    cpu_used_single_core = max(map(load_average, lines[1:]))

    return {
        'cpu_used_percent': cpu_used_total,
        'cpu_used_single_core_percent': cpu_used_single_core
    }


def stats(args):
    return {
        'done': lambda: True,
        'value': lambda: cpu_used(),
        'status': lambda: 0,
        'kill': lambda: None,
        'msg': lambda: "OK"
    }
