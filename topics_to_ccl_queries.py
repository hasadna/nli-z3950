from datapackage_pipelines.wrapper import ingest, spew

parameters, datapackage, resources, stats = ingest() + ({},)


def get_resource():
    for resource in resources:
        for row in resource:
            topic, match_type = row['topic'], row['match_type']
            if match_type and 'women' in match_type.lower():
                ccl_query = '"{}" {}'.format(row['topic'], 'WOMEN')
            else:
                ccl_query = '"{}"'.format(row['topic'])
            for lang in ['heb', 'eng', 'arb']:
                yield {'ccl_query': '{} {}'.format(ccl_query, lang)}


datapackage['resources'][0].update(name='ccl_queries', path='ccl_queries.csv',
                                   schema={'fields': [{'name': 'ccl_query', 'type': 'string'},]})


spew(datapackage, [get_resource()], stats)
