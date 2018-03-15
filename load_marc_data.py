from datapackage_pipelines.wrapper import ingest, spew
from datapackage_pipelines.utilities.resources import PROP_STREAMING
import subprocess, json, logging, os
from pymarc import JSONReader


parameters, datapackage, resources, stats = ingest() + ({},)


db_name = os.environ["NLI_DB_NAME"]
ccl_query = os.environ["NLI_CCL_QUERY"]


def get_resource():
    res = subprocess.run(["python", "nli-z3950.py2", db_name, ccl_query],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode == 0:
        reader = JSONReader(res.stdout.decode('utf-8'))
        stats["num records"] = 0
        for record in reader:
            yield {"title": record.title(),
                   "pubyear": record.pubyear(),
                   "publisher": record.publisher(),
                   "uniformtitle": record.uniformtitle(),
                   "author": record.author(),
                   "isbn": record.isbn(),
                   "json": record.as_json(),}
            stats["num records"] += 1
    else:
        logging.info(res.stdout)
        raise Exception()


datapackage["resources"] = [{PROP_STREAMING: True,
                             "name": "records", "path": "records.csv",
                             "schema": {"fields": [{"name": "title", "type": "string"},
                                                   {"name": "pubyear", "type": "string"},
                                                   {"name": "publisher", "type": "string"},
                                                   {"name": "uniformtitle", "type": "string"},
                                                   {"name": "author", "type": "string"},
                                                   {"name": "isbn", "type": "string"},
                                                   {"name": "json", "type": "object"},]}}]


spew(datapackage, [get_resource()], stats)
