#!/usr/bin/env bash

if [ "${1}" == "bash" ]; then
    bash
elif [ "${1}" == "results_download" ]; then
    [ -e data/search_results/unique_records.csv ] || (
        mkdir -p data/search_results
        curl -L https://github.com/hasadna/nli-z3950/releases/download/v0.0.4/unique_records.csv > data/search_results/unique_records.csv
    )
elif [ "${1}" == "gdrive_download" ]; then
    [ -z "${SERVICE_ACCOUNT_FILE}" ] && echo missing SERVICE_ACCOUNT_FILE environment variable && exit 1
    ! [ -e "${SERVICE_ACCOUNT_FILE}" ] && echo missing SERVICE_ACCOUNT_FILE file && exit 1
    python3.6 ./search_import_gdrive_download.py
elif [ "${1}" == "serve_search_app" ]; then
    export FLASK_APP=search_app.py
    export FLASK_DEBUG=1
    flask run -h 0.0.0.0
else
    dpp $@
    RES=$?
    chown -R 1000:1000 /data >/dev/null 2>&1
    exit $RES
fi
