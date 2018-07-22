from datapackage_pipelines.wrapper import ingest, spew
from datapackage_pipelines.utilities.resources import PROP_STREAMING
from nli_z3950.load_marc_data import get_marc_records_schema, parse_record
from pymarc.marcxml import parse_xml_to_array
import datetime, json


def get_resource(parameters, stats):
    stats['search_rows'] = 0
    for filenum in parameters['filenums']:
        filepath = parameters['files-path-template'].format(filenum=filenum)
        search_id = 'neaman{}'.format(filenum)
        with open(filepath) as f:
            for record_num, record in enumerate(parse_xml_to_array(f)):
                row = parse_record(record)
                migdar_id = '{}-{}'.format(search_id, record_num)
                row.update(migdar_id=migdar_id, first_ccl_query='neaman{}.xml'.format(filenum),
                           last_query_datetime=datetime.datetime.now(),
                           json=json.loads(row['json']))
                stats['search_rows'] += 1
                yield row


def get_resources(resources, parameters, stats):
    for resource in resources:
        yield resource
    yield get_resource(parameters, stats)


def get_datapackage(datapackage):
    schema = get_marc_records_schema()
    schema['fields'] += [{'name': 'migdar_id', 'type': 'string'},
                         {'name': 'first_ccl_query', 'type': 'string'},
                         {'name': 'last_query_datetime', 'type': 'datetime'},
                         {'name': 'json', 'type': 'object'}]
    datapackage['resources'].append({'name': 'search_haifa_files',
                                     'path': 'search_haifa_files.csv',
                                     PROP_STREAMING: True,
                                     'schema': schema})
    return datapackage


def main():
    parameters, datapackage, resources, stats = ingest() + ({},)
    spew(get_datapackage(datapackage),
         get_resources(resources, parameters, stats),
         stats)


if __name__ == '__main__':
    main()