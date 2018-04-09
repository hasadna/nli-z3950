from datapackage_pipelines.wrapper import ingest, spew
import logging, re, pymarc, json


parameters, datapackage, resources, stats = ingest() + ({},)


output_fields = parameters['fields']


unique_records_resource_num = None


for i, resource in enumerate(datapackage['resources']):
    if resource['name'] == 'unique_records':
        unique_records_resource_num = i
        for output_field in output_fields:
            datapackage['resources'][unique_records_resource_num]['schema']['fields'].append({'name': output_field['name'],
                                                                                              'type': 'string'})


def get_resource(resource):
    for row in resource:
        for output_field in output_fields:
            if 'marc_tag' in output_field:
                for record in pymarc.JSONReader(json.dumps([row['json']])):
                    record_fields = record.get_fields(output_field['marc_tag'])
                    if len(record_fields) > 0:
                        record_field = record_fields[0]
                        row[output_field['name']] = record_field.format_field()
                        break
                    else:
                        row[output_field['name']] = ''
            elif 'marc_leader_position' in output_field and 'marc_leader_map' in output_field:
                key = row['json']['leader'][output_field['marc_leader_position']]
                row[output_field['name']] = output_field['marc_leader_map'][key]
        if row.get('item_type_999'):
            row['item_type'] = row['item_type_999']
        elif row.get('item_type_leader') == 'Language material' and row.get('bibliographic_level') == 'Monograph/Item':
            row['item_type'] = 'book'
        else:
            row['item_type'] = None
        if row['item_type']:
            yield row
        else:
            logging.info('could not determine item type: {}'.format((row.get('item_type_999'), row.get('item_type_leader'), row.get('bibliographic_level'))))


def get_resources():
    for i, resource in enumerate(resources):
        if i == unique_records_resource_num:
            yield get_resource(resource)
        else:
            yield resource


spew(datapackage, get_resources(), stats)
