from datapackage_pipelines.wrapper import ingest, spew
import logging, re, json


parameters, datapackage, resources, stats = ingest() + ({'num items without url': 0,
                                                         'num items with invalid url': 0,},)


export_keys = parameters['export_keys']


unique_records_resource_num = None


for i, resource in enumerate(datapackage['resources']):
    if resource['name'] == 'unique_records':
        unique_records_resource_num = i


def get_url(row):
    if row['url']:
        res = re.match('.*(http([^\s]+)).*', row['url'])
        if res:
            return res.group(1)
        else:
            stats['num items with invalid url'] += 1
            logging.info('item with invalid url: {}'.format(row['url']))
            return None
    else:
        stats['num items without url'] += 1
        logging.info('item without url')
        return None


def get_value(row, k):
    v = row[k]
    if not v:
        return ''
    elif k == 'json':
        return json.dumps(v)
    else:
        return str(v)


def is_valid_row(row):
    if row['url']:
        return True
    else:
        logging.info('invalid row: missing url')
        return False


def get_resource(resource):
    for row in resource:
        row['url'] = get_url(row)
        if is_valid_row(row):
            row = {k: get_value(row, k) for k, v in row.items() if k in export_keys}
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
