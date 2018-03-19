from datapackage_pipelines.wrapper import ingest, spew
from datapackage_pipelines.utilities.resources import PROP_STREAMING
import logging
from nli_z3950.load_marc_data import load_marc_data, get_marc_records_schema


parameters, datapackage, resources, stats = ingest() + ({},)


query_stats = {}


def get_resource():
    stats["total records"] = 0
    stats["total searches"] = 0
    for resource in resources:
        for row in resource:
            if not parameters.get('max-records') or parameters['max-records'] >= stats['total records']:
                ccl_query = row["ccl_query"]
                if ccl_query not in query_stats:
                    query_stats[ccl_query] = {}
                    logging.info(ccl_query)
                    for record in load_marc_data("ULI02", ccl_query, query_stats[ccl_query]):
                        yield dict(record, ccl_query=ccl_query)
                        stats['total records'] += 1
                    logging.info("'{}': {}, total records={}".format(ccl_query, query_stats[ccl_query], stats['total records']))
                    stats["total searches"] += 1


def get_query_stats_resource():
    for ccl_query, stats_ in query_stats.items():
        yield {'ccl_query': ccl_query,
               'num_records': stats_['num records']}


datapackage["resources"] = [{PROP_STREAMING: True,
                             "name": "records", "path": "records.csv",
                             "schema": get_marc_records_schema()},
                            {PROP_STREAMING: True,
                             "name": "query_stats", "path": "query_stats.csv",
                             "schema": {"fields": [{"name": "ccl_query", "type": "string"},
                                                   {"name": "num_records", "type": "integer"},]}},
                            ]
datapackage['resources'][0]['schema']['fields'] += [{'name': 'ccl_query', 'type': 'string',}]


spew(datapackage, [get_resource(), get_query_stats_resource()], stats)
