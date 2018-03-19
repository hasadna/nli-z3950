import subprocess, logging, json, pymarc
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
    res = subprocess.run(["python", "nli-z3950.py2", db_name, ccl_query],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logging.info(res.stderr.decode('utf-8'))
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
        logging.info(res.stdout.decode('utf-8'))
        raise Exception()
