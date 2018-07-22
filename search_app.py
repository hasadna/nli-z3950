from flask import Flask, jsonify, send_file
from nli_z3950.load_marc_data import (load_marc_data, get_record_key, get_marc_records_schema, get_pubyear,
                                      extract_marc_data, get_export_row, MIN_YEAR)
import uuid, csv, datetime, json, os, openpyxl, yaml, logging, sys
from slugify import slugify
from tabulator import Stream
from search_app_index import get_all_gdrive_record_keys_cached


last_download_time = None


def get_ccl_query(search_text, language):
    return '{} {}'.format(search_text, language)


def get_preview_record(record):
    return {k: record[k] for k in ('author', 'title', 'url', 'tags', 'pubyear')}


app = Flask(__name__)


@app.route('/search/<search_query>/<search_text>/<language>/<noncache>')
def search(search_query, search_text, language, noncache):
    all_gdrive_record_keys = [row['record_key'] for row in get_all_gdrive_record_keys_cached(noncache=(noncache == 'true'))]
    res = {'csv_records': 0,
           'xlsx_records': 0,
           'total_records': 0,
           'first_10_new_records': []}
    search_id = str(uuid.uuid4()).replace('-','')
    search_dir = './data/search_app/{}'.format(search_id)
    logging.warning(search_dir)
    os.makedirs(search_dir, exist_ok=True)
    with open('{}/records.csv'.format(search_dir), 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csv_header_row = [field['name'] for field in get_marc_records_schema()['fields']
                         ] + ['migdar_id', 'first_ccl_query', 'last_query_datetime', 'json']
        csvwriter.writerow(csv_header_row)
        wb = openpyxl.Workbook()
        ws = wb.active
        with open('pipeline-spec.yaml', 'r') as f:
            pipeline_spec = yaml.load(f)
        extract_marc_data_fields = pipeline_spec['search_export']['pipeline'][2]['parameters']['fields']
        export_keys = pipeline_spec['search_export']['pipeline'][3]['parameters']['export_keys']
        is_first_output_row = True
        for record_num, record in enumerate(load_marc_data("ULI02", search_query, {}, 'PQF')):
            record_key = get_record_key(record)
            pubyear = get_pubyear(record)
            if not pubyear or pubyear < MIN_YEAR:
                logging.warning('invalid pubyear: {}'.format(record_key))
            elif record_key in all_gdrive_record_keys:
                logging.warning('already in gdrive: {}'.format(record_key))
            else:
                migdar_id = '{}-{}'.format(search_id, record_num)
                csv_row = [record[field['name']] for field in get_marc_records_schema()['fields']
                          ] + [migdar_id, search_query, datetime.datetime.now(), record['json']]
                csvwriter.writerow(csv_row)
                res['csv_records'] += 1
                row = dict(zip(csv_header_row, csv_row))
                row['json'] = json.loads(row['json'])
                row = extract_marc_data(row, extract_marc_data_fields)
                if row:
                    row = get_export_row(row, export_keys)
                    if row:
                        del row['json']
                        if is_first_output_row:
                            is_first_output_row = False
                            ws.append(list(row.keys()))
                        ws.append(list(row.values()))
                        res['xlsx_records'] += 1
                        if len(res['first_10_new_records']) < 10:
                            res['first_10_new_records'].append(get_preview_record(row))
            res["total_records"] += 1
        wb.save('{}/records.xlsx'.format(search_dir))
    with open('{}/metadata.json'.format(search_dir), 'w') as f:
        json.dump({'search_text': search_text, 'language': language, 'ccl_query': search_query}, f)
    with open('./data/search_app/index.csv', 'a') as f:
        csvwriter = csv.writer(f)
        csvwriter.writerow([search_text, language, search_query, datetime.datetime.now(), search_id])
    res['search_id'] = search_id
    res = jsonify(res)
    res.headers['Access-Control-Allow-Origin'] = '*'
    return res


@app.route('/download/<search_id>.<extension>')
def download(search_id, extension):
    csv_file_name = 'data/search_app/{}/records.csv'.format(search_id)
    xlsx_file_name = 'data/search_app/{}/records.xlsx'.format(search_id)
    with open('data/search_app/{}/metadata.json'.format(search_id)) as f:
        metadata = json.load(f)
    if extension == 'csv':
        return send_file(csv_file_name)
    elif extension == 'xlsx':
        filename = '{}-{}.xlsx'.format(slugify(metadata['search_text']), metadata['language'])
        with open('data/search_app/{}/metadata.json'.format(search_id), 'w') as f:
            metadata['last_download'] = str(datetime.datetime.now())
            json.dump(metadata, f)
        return send_file(xlsx_file_name, as_attachment=True, attachment_filename=filename)
    else:
        raise NotImplementedError('unhandled extension: {}'.format(extension))

