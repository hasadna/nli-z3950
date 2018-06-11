from datapackage_pipelines.wrapper import ingest, spew
from datapackage_pipelines.utilities.resources import PROP_STREAMING
from tabulator import Stream
import logging
from openpyxl import load_workbook
import search_import
from nli_z3950.load_marc_data import get_record_key
import os


def get_all_gdrive_migdar_ids():
    all_migdar_ids = set()
    schema, sheets = search_import.load_sheets()
    for sheet in sheets:
        for row in sheet['iterator']:
            all_migdar_ids.add(str(row['migdar_id']))
    return all_migdar_ids


def get_all_gdrive_record_keys():
    schema, sheets = search_import.load_sheets()
    # old numeric migdar ids, referenced in data/search_results/unique_records.csv
    numeric_migdar_ids = set()
    # new search app migdar ids, referenced in data/search_app under relevant search_id
    search_migdar_ids = {}
    # iterate over sheets from gdrive - extract all the ids
    for sheet in sheets:
        for row in sheet['iterator']:
            migdar_id = str(row['migdar_id'])
            if migdar_id.isnumeric():
                numeric_migdar_ids.add(int(migdar_id))
            else:
                try:
                    search_id, rownum = migdar_id.split('-')
                    search_migdar_ids.setdefault(search_id, set()).add(int(rownum))
                except Exception:
                    logging.exception('invalid migdar_id: {}'.format(migdar_id))
    # get record keys for the old migdar ids
    with Stream('data/search_results/unique_records.csv', headers=1) as stream:
        for row in stream.iter(keyed=True):
            if int(row['migdar_id']) in numeric_migdar_ids:
                yield {'migdar_id': str(row['migdar_id']),
                       'record_key': get_record_key(row)}
    # get record keys for the new search app migdar ids
    for search_id, rownums in search_migdar_ids.items():
        if os.path.exists('data/search_app/{}/records.csv'.format(search_id)):
            with Stream('data/search_app/{}/records.csv'.format(search_id), headers=1) as stream:
                for row in stream.iter(keyed=True):
                    if int(row['migdar_id'].split('-')[1]) in rownums:
                        yield {'migdar_id': row['migdar_id'],
                               'record_key': get_record_key(row)}
        else:
            logging.error('invalid search_id: {}'.format(search_id))


def main():
    parameters, datapackage, resources, stats = ingest() + ({},)
    datapackage["resources"] = [{PROP_STREAMING: True, 'name': 'record_keys', 'path': 'record_keys.csv', 'schema': {
                                'fields': [{'name': 'migdar_id', 'type': 'string'}, {'name': 'record_key', 'type': 'string'}]}}]
    spew(datapackage, [get_all_gdrive_record_keys()], stats)


if __name__ == '__main__':
    main()
