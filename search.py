from datapackage_pipelines.wrapper import ingest, spew
from datapackage_pipelines.utilities.resources import PROP_STREAMING
import logging
from nli_z3950.load_marc_data import load_marc_data


parameters, datapackage, resources, stats = ingest() + ({},)


query_stats = {}


def get_resource():
    stats["total records"] = 0
    stats["total searches"] = 0
    for resource in resources:
        for row in resource:
            ccl_query = row["ccl_query"]
            if ccl_query not in query_stats:
                query_stats[ccl_query] = {}
                for record in load_marc_data("ULI02", ccl_query, query_stats[ccl_query]):
                    yield record
                    stats['total records'] += 1
                logging.info("'{}': {}, total records={}".format(ccl_query, query_stats[ccl_query], stats['total records']))
                stats["total searches"] += 1
            if parameters.get('max-records') and parameters['max-records'] < stats['total records']:
                break


def get_query_stats_resource():
    for ccl_query, stats_ in query_stats.items():
        yield {'ccl_query': ccl_query,
               'num_records': stats_['num records']}


datapackage["resources"] = [{PROP_STREAMING: True,
                             "name": "records", "path": "records.csv",
                             "schema": {"fields": [{"name": "title", "type": "string"},
                                                   {"name": "pubyear", "type": "string"},
                                                   {"name": "publisher", "type": "string"},
                                                   {"name": "uniformtitle", "type": "string"},
                                                   {"name": "author", "type": "string"},
                                                   {"name": "isbn", "type": "string"},
                                                   {"name": "json", "type": "object"},]}},
                            {PROP_STREAMING: True,
                             "name": "query_stats", "path": "query_stats.csv",
                             "schema": {"fields": [{"name": "ccl_query", "type": "string"},
                                                   {"name": "num_records", "type": "integer"},]}},
                            ]


spew(datapackage, [get_resource(), get_query_stats_resource()], stats)
