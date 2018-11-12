import logging


BIB_DATA_SUBFIELD_NAMES = {
    'g': 'bib_related_parts',
    't': 'bib_title',
    'd': 'bib_place_publisher_date',
    'u': 'bib_standard_technical_report_number'
}


def get_bib_data(marc_json):
    for field in marc_json['fields']:
        bibfield_names = [k for k in field if '773' == str(k)]
        if len(bibfield_names) > 0:
            assert len(bibfield_names) == 1
            bibfield = field[bibfield_names[0]]
            assert bibfield.pop('ind1') == ' '
            assert bibfield.pop('ind2') == ' '
            subfields = {}
            for subfield in bibfield.pop('subfields'):
                for subfield_name in subfield:
                    assert subfield_name not in subfields
                    subfields[subfield_name] = subfield[subfield_name]
            assert len(bibfield) == 0
            # https://www.loc.gov/marc/bibliographic/bd773.html
            bib_data = {}
            for subfield_name in subfields:
                assert subfield_name in BIB_DATA_SUBFIELD_NAMES, \
                    'invalid bib subfield: {} = {}'.format(subfield_name, subfields[subfield_name])
                bib_data[BIB_DATA_SUBFIELD_NAMES[subfield_name]] = subfields[subfield_name]
            yield bib_data


def parse_marc_bib_data(marc_json):
    bib_datas = list(get_bib_data(marc_json))
    if len(bib_datas) > 1:
        logging.warning('more then 1 bib data fields, using first one')
        return bib_datas[0]
    elif len(bib_datas) != 1:
        logging.warning('no bib data\n')
        return None
    else:
        return bib_datas[0]
