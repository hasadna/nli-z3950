#!/usr/bin/env bash
dpp $@
RES=$?
chown -R 1000:1000 /data >/dev/null 2>&1
exit $RES
