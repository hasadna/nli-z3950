import subprocess, logging, json, pymarc, os, re, sys
from pymarc import JSONReader


# https://www.loc.gov/marc/bibliographic/
# Relevant fields for NLI z3950 data
# fields with less then 3 chars will cause to extract all the fields that match this prefix
# all the strings will be appended together
nli_metadata_fields = {
    '041': 'language_code',
    '09' : 'custom_metadata',  # seems to contain details like type of item, availability online
    '260': 'publication_distribution_details',
    '300': 'physical_description',  # details about the file format
    '5'  : 'notes',
    '650': 'tags',
    '856': 'url',
    '992': 'url',
}


def get_marc_records_schema():
    return {"fields": [{"name": "title", "type": "string"},
                       {"name": "pubyear", "type": "string"},
                       {"name": "publisher", "type": "string"},
                       {"name": "uniformtitle", "type": "string"},
                       {"name": "author", "type": "string"},
                       {"name": "isbn", "type": "string"},
                       {"name": "json", "type": "object"},
                       {"name": "language_code", "type": "string"},
                       {"name": "custom_metadata", "type": "string"},
                       {"name": "publication_distribution_details", "type": "string"},
                       {"name": "physical_description", "type": "string"},
                       {"name": "notes", "type": "string"},
                       {"name": "tags", "type": "string"},
                       {"name": "url", "type": "string"},
                       ]}


def load_marc_data(db_name, ccl_query, stats):
    res = subprocess.run([os.environ.get('NLI_PYTHON2', "python"), "nli-z3950.py2", db_name, ccl_query],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    sys.stderr.write(res.stderr.decode('utf-8'))
    if res.returncode == 0:
        reader = JSONReader(res.stdout.decode('utf-8'))
        stats["num records"] = 0
        for record in reader:
            row = {"title": record.title(),
                   "pubyear": record.pubyear(),
                   "publisher": record.publisher(),
                   "uniformtitle": record.uniformtitle(),
                   "author": record.author(),
                   "isbn": record.isbn(),
                   "json": record.as_json(),}
            raw = {field_name: [] for field_name in list(set(nli_metadata_fields.values()))}
            json_records_string = '[' + json.dumps(json.loads(row["json"])) + ']'
            for record in pymarc.JSONReader(json_records_string):
                for field in record.get_fields():
                    for match_tag in [field.tag, field.tag[:2], field.tag[:1]]:
                        field_name = nli_metadata_fields.get(match_tag)
                        if field_name:
                            raw_values = raw.setdefault(field_name, [])
                            raw_values += [field.format_field()]
            row.update(**{k: ', '.join(v) for k, v in raw.items()})
            stats["num records"] += 1
            yield row
    else:
        sys.stderr.write(res.stdout.decode('utf-8'))
        raise Exception()


def get_record_key(record):
    return '{}{}{}'.format(record['url'], record['tags'], record['title'])


def get_pubyear(record):
    if record.get('pubyear'):
        res = re.match('.*([12][0-9][0-9][0-9]).*', record['pubyear'])
        if res:
            return int(res.group(1))
        else:
            logging.warning('invalid year: {}'.format(record['pubyear']))
            return None
    else:
        return None


def extract_marc_data(row, output_fields):
    for output_field in output_fields:
        if 'marc_tag' in output_field:
            for record in pymarc.JSONReader(json.dumps([row['json']])):
                record_fields = record.get_fields(output_field['marc_tag'])
                if len(record_fields) > 0:
                    if output_field.get('first_subfield_only'):
                        record_field = record_fields[0]
                        row[output_field['name']] = record_field.format_field()
                    else:
                        row[output_field['name']] = ' | '.join([record_field.format_field() for record_field in record_fields])
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
        return row
    else:
        logging.warning('could not determine item type: {}'.format((row.get('item_type_999'), row.get('item_type_leader'), row.get('bibliographic_level'))))
        return None


def get_export_url(row):
    if row['url']:
        res = re.match('.*(http([^\s]+)).*', row['url'])
        if res:
            return res.group(1)
        else:
            logging.warning('item with invalid url: {}'.format(row['url']))
            return None
    else:
        logging.warning('item without url')
        return None


def get_export_value(row, k):
    v = row[k]
    if not v:
        return ''
    elif k == 'json':
        return json.dumps(v)
    else:
        return str(v)


def is_valid_export_row(row):
    if row['url']:
        return True
    else:
        logging.warning('invalid row: missing url')
        return False


def get_export_row(row, export_keys):
    row['url'] = get_export_url(row)
    if is_valid_export_row(row):
        row = {k: get_export_value(row, k) for k, v in row.items() if k in export_keys}
        return row
    else:
        return None
