from datapackage_pipelines.wrapper import ingest, spew
import logging, re, json
from nli_z3950.load_marc_data import get_export_url, get_export_value, is_valid_export_row, get_export_row


parameters, datapackage, resources, stats = ingest() + ({'num items without url': 0,
                                                         'num items with invalid url': 0,},)


export_keys = parameters['export_keys']


unique_records_resource_num = None


for i, resource in enumerate(datapackage['resources']):
    if resource['name'] == 'unique_records':
        unique_records_resource_num = i


def get_resource(resource):
    for row in resource:
        row = get_export_row(row, export_keys)
        if row:
            yield row


def get_resources():
    for i, resource in enumerate(resources):
        if i == unique_records_resource_num:
            yield get_resource(resource)
        else:
            yield resource


datapackage['resources'][unique_records_resource_num].update(schema={'fields': [{'name': k, 'type': 'string'}
                                                                                for k in export_keys]},
                                                             name='search_export',
                                                             path='search_export.csv')


spew(datapackage, get_resources(), stats)
