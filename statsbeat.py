#!/usr/bin/env python3

import datetime
import importlib
import json
import os
import requests
import subprocess
import sys
import time
import traceback
import yaml



# statsbeat - simple way to push metrics and nagios-compatible plugins to ES
#
# status:
# 0 - OK
# 1 - WARN
# 2 - CRITICAL
# 3 - UNKNOWN

# configuration

# config file name
statsbeat_yml = "/data/conf/statsbeat.yml"
plugins_root = "/data/conf"
checks_root = "/data/conf/checks"

sys.path.insert(0, plugins_root)
os.chdir(plugins_root)

imported_modules = {}


def log_info(s):
    pass


def log_error(s):
    pass


def load_yaml(fname):
    f = open(fname, 'r')
    result = yaml.load(f)
    f.close()
    return result


# replace values in tree-like cfg with environment variables
# nested values are separated by dots, lists represended by indexes in brackets
def override_with_env(cfg, env, path = ''):
    def append_key(path, key):
        if path == '':
            return key
        else:
            return path + "." + key

    if isinstance(cfg, list):
        r = []
        for i, v in cfg:
            r.append(override_with_env(v, env, path + "[" + i + "]"))
        return r

    if isinstance(cfg, map):
        r = {}
        for k in cfg:
            r[k] = override_with_env(cfg[k], append_key(path, k))
        return r

    key = append_key(path, str(cfg))
    if key in env:
        return env[key]
    else:
        return cfg


# statsbeat.beat_interval
# statsbeat.timestamp_field_name
# statsbeat.timeout
# fields[]
def load_config():
    try:
        cfg = load_yaml(statsbeat_yml)
        cfg = override_with_env(cfg, os.environ)
        return cfg
    except Exception as e:
        raise Exception("Unable to load config file '" + statsbeat_yml + "'. Cause: " + str(e))
    pass


def make_result(value, status, msg):
    return {
        'done': lambda: True,
        'value': lambda: value,
        'status': lambda: status,
        'kill': lambda: None,
        'msg': lambda: str(msg)
    }


def start_check(args):
    try:
        if not isinstance(args, list):
            args = str(args).split(" ")

        if args[0].startswith('./'):
            args[0] = checks_root + "/" + args[0][2:]

        p = subprocess.Popen(args, bufsize=65536, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return {
            'done': lambda: p.poll() is not None,
            'value': lambda: p.poll(),
            'status': lambda: p.poll(),
            'kill': lambda: p.kill(),
            'msg': lambda: str(p.stdout.read().decode('utf-8').strip())
        }
    except Exception as e:
        ex = e
        return make_result(0, 3, ex)


def start_plugin(args):
    try:
        if not isinstance(args, list):
            args = str(args).split(" ")
        name = args[0]

        if name in imported_modules:
            module = imported_modules[name]
        else:
            module = importlib.import_module("plugins." + name)
            imported_modules[name] = module

        return module.stats(args[1:])

    except Exception as e:
        ex = e
        return make_result(None, 3, ex)


def is_check(cfg):
    if isinstance(cfg, list):
        name = cfg[0]
    else:
        name = cfg
    return name.startswith(".") or name.startswith("/")


def collect_stats(fields, timeout):
    result = {}

    def add_result(field, v):
        try:
            value = v['value']()
            if value is not None:
                if isinstance(value, dict):
                    for k in value:
                        result[field + "_" + k] = value[k]
                else:
                    result[field] = value
            result[field + "_status"] = v['status']()
            result[field + "_msg"] = v['msg']()
        except Exception as e:
            result[field + "_status"] = 3
            result[field + "_msg"] = str(e)

    running = {}

    for field in fields:
        try:
            cfg = fields[field]
            if is_check(cfg):
                running[field] = start_check(cfg)
            else:
                running[field] = start_plugin(cfg)
            pass
        except Exception as e:
            ex = e
            running[field] = make_result(0, 3, ex)

    start_time = time.monotonic()

    while len(running) > 0 and time.monotonic() - start_time < timeout:
        for field in dict(running):
            v = running[field]
            if v['done']():
                add_result(field, v)
                del running[field]
        time.sleep(0.2)

    for field in running:
        running[field]['kill']()
        add_result(field, make_result(0, 3, "CRITICAL: Timed out after " + str(timeout) + " seconds"))

    return result


def send(stats, index, url):
    req = ""
    for o in [stats]:
        try:
            req += '{"index":{"_index":"' + index + '","_type":"external", "_id":"' + o['_id'] + '"}}\n'
            o.pop('_id', None)
        except KeyError:
            req += '{"index":{"_index":"' + index + '","_type":"external"}}\n'
        req += json.dumps(o) + "\n"

    r = requests.post(url + index + "/external/_bulk", data=req,
                      headers={'Content-Type': 'application/json'})

    if r.status_code >= 300:
        raise RuntimeError("Request to ES failed: " + str(r.status_code) + " " + r.reason + "\n" + r.text[:300])


def mainloop(config):
    beat_interval = int(config['statsbeat']['beat_interval'])
    index = config['statsbeat']['elastic']['index_name']
    es_url = config['statsbeat']['elastic']['server_url']

    while True:
        try:
            start = time.monotonic()
            ts = datetime.datetime.utcnow().isoformat()
            stats = collect_stats(config['fields'], config['statsbeat']['timeout'])
            stats[config['statsbeat']['timestamp_field_name']] = ts

            send(stats, index, es_url)

            remaining_time_sec = beat_interval - (time.monotonic() - start)
            if remaining_time_sec > 0:
                time.sleep(remaining_time_sec)
        except Exception as e:
            traceback.print_exc()
            time.sleep(beat_interval)


def main():
    config = load_config()
    mainloop(config)


main()

