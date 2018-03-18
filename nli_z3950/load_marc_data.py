import subprocess, logging
from pymarc import JSONReader


def load_marc_data(db_name, ccl_query, stats):
    res = subprocess.run(["python", "nli-z3950.py2", db_name, ccl_query],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logging.info(res.stderr.decode('utf-8'))
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
                   "json": record.as_json(), }
            stats["num records"] += 1
    else:
        logging.info(res.stdout.decode('utf-8'))
        raise Exception()
