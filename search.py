from datapackage_pipelines.wrapper import ingest, spew
from datapackage_pipelines.utilities.resources import PROP_STREAMING
import logging, os, json
from nli_z3950.load_marc_data import load_marc_data, get_marc_records_schema
import datetime


parameters, datapackage, resources, stats = ingest() + ({},)


max_records = parameters.get('max-records', os.environ.get('MAX_RECORDS'))
max_records = int(max_records) if max_records else None
logging.info('max_records={}'.format(max_records))


is_stateful = len(datapackage['resources']) == 3


query_stats = {}
all_records = []


def get_record_key(record):
    return '{}{}{}'.format(record['url'], record['tags'], record['title'])


def get_resource():
    stats["total yielded records"] = 0
    stats["total search results"] = 0
    stats["total searches"] = 0
    if is_stateful:
        for record in next(resources):
            all_records.append(get_record_key(record))
            if 'last_query_datetime' not in record:
                record['last_query_datetime'] = None
            yield record
        for row in next(resources):
            query_stats[row['ccl_query']] = {'num records': row['num_records']}
        logging.info(query_stats)
    for ccl_query_row in next(resources):
        if not max_records or max_records >= stats['total yielded records']:
            ccl_query = ccl_query_row["ccl_query"]
            if ccl_query not in query_stats:
                query_stats[ccl_query] = {}
                logging.info('running query: {}'.format(ccl_query))
                for record in load_marc_data("ULI02", ccl_query, query_stats[ccl_query]):
                    record_key = get_record_key(record)
                    if record_key not in all_records:
                        migdar_id = len(all_records)
                        all_records.append(record_key)
                        yield dict(record,
                                   migdar_id=migdar_id,
                                   first_ccl_query=ccl_query,
                                   last_query_datetime=datetime.datetime.now(),
                                   json=json.loads(record['json']))
                        stats['total yielded records'] += 1
                    stats["total search results"] += 1
                logging.info("'{}': {}, total search results: {}, total yielded records={}".format(ccl_query, query_stats[ccl_query],
                                                                                                   stats['total search results'],
                                                                                                   stats['total yielded records']))
                stats["total searches"] += 1
            else:
                logging.info('skipping query {}'.format(ccl_query))


def get_query_stats_resource():
    for ccl_query, stats_ in query_stats.items():
        yield {'ccl_query': ccl_query,
               'num_records': stats_['num records']}


def get_unique_records_schema():
    schema = get_marc_records_schema()
    schema['fields'] += [{'name': 'migdar_id', 'type': 'integer'},
                         {'name': 'first_ccl_query', 'type': 'string'},
                         {'name': 'last_query_datetime', 'type': 'datetime'}]
    for field in schema['fields']:
        if field['name'] == 'json':
            field['type'] = 'object'
    return schema


datapackage["resources"] = [{PROP_STREAMING: True,
                             "name": "unique_records", "path": "unique_records.csv",
                             "schema": get_unique_records_schema()},
                            {PROP_STREAMING: True,
                             "name": "query_stats", "path": "query_stats.csv",
                             "schema": {"fields": [{"name": "ccl_query", "type": "string"},
                                                   {"name": "num_records", "type": "integer"},]}},
                            ]


spew(datapackage, [get_resource(), get_query_stats_resource()], stats)
