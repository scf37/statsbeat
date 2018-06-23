#!/bin/bash

mkdir -p /data/conf
cp -n /opt/statsbeat.yml /data/conf/statsbeat.yml
mv -n /opt/checks /data/conf/
mv -n /opt/plugins /data/conf/
exec /opt/statsbeat.py