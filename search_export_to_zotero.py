from datapackage_pipelines.wrapper import ingest, spew
import logging, re, pymarc, json


parameters, datapackage, resources, stats = ingest() + ({},)


search_export_resource_num = None


for i, resource in enumerate(datapackage['resources']):
    if resource['name'] == parameters['resource']:
        search_export_resource_num = i


def get_dat_file_name(row):
    name = row['first_ccl_query']
    name = ''.join((c for c in name if c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZאבגדהוזחטיכלמנסעפצקרשת '))
    name = name.replace(' ', '_')
    return parameters["out-path"] + "/nli_{}.dat".format(name)


def get_resource(resource):
    last_ccl_query, dat_file = None, None
    for row in resource:
        if row['first_ccl_query'] != last_ccl_query:
            if dat_file:
                dat_file.close()
            dat_file = open(get_dat_file_name(row), 'wb')
            marc_writer = pymarc.MARCWriter(dat_file)
            last_ccl_query = row['first_ccl_query']
        assert marc_writer
        for record in pymarc.JSONReader(json.dumps([json.loads(row['json'])])):
            marc_writer.write(record)
        yield row


def get_resources():
    for i, resource in enumerate(resources):
        if i == search_export_resource_num:
            yield get_resource(resource)
        else:
            yield resource


spew(datapackage, get_resources(), stats)
