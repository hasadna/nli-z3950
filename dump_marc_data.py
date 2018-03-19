from datapackage_pipelines.wrapper import ingest, spew
import logging
import pymarc
import json
import os


parameters, datapackage, resources, stats = ingest() + ({},)


def get_resource():
    os.makedirs(parameters["out-path"], exist_ok=True)
    dat_file = open(parameters["out-path"] + "/{}.dat".format('marc'), 'wb')
    marc_writer = pymarc.MARCWriter(dat_file)
    for row in next(resources):
        json_records_string = '[' + json.dumps(json.loads(row["json"])) + ']'
        for record in pymarc.JSONReader(json_records_string):
            marc_writer.write(record)
        yield row


spew(datapackage, [get_resource()], stats)
