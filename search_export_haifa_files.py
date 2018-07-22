from datapackage_pipelines.wrapper import process
import yaml
from functools import lru_cache
from nli_z3950 import load_marc_data


@lru_cache(maxsize=1)
def pipeline_spec():
    with open('pipeline-spec.yaml', 'r') as f:
        return yaml.load(f)


@lru_cache(maxsize=1)
def extract_marc_data_fields():
    return pipeline_spec()['search_export']['pipeline'][2]['parameters']['fields']


@lru_cache(maxsize=1)
def export_keys():
    return pipeline_spec()['search_export']['pipeline'][3]['parameters']['export_keys']


def process_row(row, row_index, spec, resource_index, parameters, stats):
    if spec['name'] == 'search_export_haifa_files':
        record = load_marc_data.extract_marc_data(row, extract_marc_data_fields())
        row = None
        if record:
            record = load_marc_data.get_export_row(record, export_keys())
            if record:
                del record['json']
                stats['export_rows'] += 1
                row = record
    return row


def modify_datapackage(datapackage, parameters, stats):
    stats['export_rows'] = 0
    for descriptor in datapackage['resources']:
        if descriptor['name'] == 'search_export_haifa_files':
            fields = [{'name': k, 'type': 'string'}
                      for k in export_keys()
                      if k != 'json']
            descriptor['schema']['fields'] = fields
    return datapackage


if __name__ == '__main__':
    process(modify_datapackage, process_row)
