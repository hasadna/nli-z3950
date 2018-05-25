from datapackage_pipelines.wrapper import ingest, spew
import re, logging
from datapackage_pipelines.utilities.resources import PROP_STREAMING


parameters, datapackage, resources, stats = ingest() + ({'valid rows': 0, 'invalid years': 0,
                                                         'null years': 0, 'years not in range': 0,
                                                         'migdar_id not in range': 0},)


year_stats = {}


min_year = parameters['min_year']


def get_resource():
    for resource in resources:
        for row in resource:
            if parameters.get('min_migdar_id') and row['migdar_id'] >= parameters['min_migdar_id']:
                if row.get('pubyear'):
                    res = re.match('.*([12][0-9][0-9][0-9]).*', row['pubyear'])
                    if res:
                        row['__year'] = year = int(res.group(1))
                        if year >= min_year:
                            yield row
                            stats['valid rows'] += 1
                        else:
                            stats['years not in range'] += 1
                        year_stats.setdefault(year, 0)
                        year_stats[year] += 1
                    else:
                        stats['invalid years'] += 1
                else:
                    stats['null years'] += 1
            else:
                stats['migdar_id not in range'] += 1


def get_year_stats_resource():
    for year in sorted(year_stats, reverse=True):
        yield {'year': year, 'num_items': year_stats[year]}


datapackage['resources'] = [datapackage['resources'][0]]
datapackage['resources'][0]['schema']['fields'] += [{'name': '__year', 'type': 'integer'}]

datapackage['resources'] += [{'name': 'year_stats', 'path': 'year_stats.csv', PROP_STREAMING: True,
                              'schema': {'fields': [{'name': 'year', 'type': 'integer'},
                                                    {'name': 'num_items', 'type': 'integer'},]}}]


spew(datapackage, [get_resource(), get_year_stats_resource()], stats)
