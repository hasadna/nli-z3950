from datapackage_pipelines.wrapper import ingest, spew
from datapackage_pipelines.utilities.resources import PROP_STREAMING
from nli_z3950.load_marc_data import load_marc_data
import os


parameters, datapackage, resources, stats = ingest() + ({},)
db_name = os.environ["NLI_DB_NAME"]
ccl_query = os.environ["NLI_CCL_QUERY"]
datapackage["resources"] = [{PROP_STREAMING: True,
                             "name": "records", "path": "records.csv",
                             "schema": {"fields": [{"name": "title", "type": "string"},
                                                   {"name": "pubyear", "type": "string"},
                                                   {"name": "publisher", "type": "string"},
                                                   {"name": "uniformtitle", "type": "string"},
                                                   {"name": "author", "type": "string"},
                                                   {"name": "isbn", "type": "string"},
                                                   {"name": "json", "type": "object"},]}}]
spew(datapackage, [load_marc_data(db_name, ccl_query, stats)], stats)
