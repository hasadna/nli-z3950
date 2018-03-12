#!/usr/bin/env python2
from PyZ3950 import zoom
import pymarc, sys


if len(sys.argv) < 3:
    print("Usage: nli-z3950 <DB_NAME> <CCL_QUERY> [BINARY_MARC_SEPARATOR]")
    print("DB_NAME - National Library Z3950 DB Name, one of:")
    print("    ULI02 - The Israel Union List (ULI)")
    print("    NNL10 - National Library Name Authority File")
    print("CCL_QUERY - see https://software.indexdata.com/yaz/doc/tools.html#CCL")
    print("BINARY_MARC_SEPARATOR - (optional) - "
          "outputs using MARC binary format with the given separator between records")
    exit(1)


conn = zoom.Connection('uli.nli.org.il', 9991)
conn.databaseName = sys.argv[1]
conn.preferredRecordSyntax = 'USMARC'
conn.elementSetName='F'
i = 0
marc_separator = sys.argv[3] if len(sys.argv) > 3 else None
if not marc_separator:
    print('[')
for r in conn.search(zoom.Query('CCL', '"' + sys.argv[2].decode('UTF-8') + '"')):
  for record in pymarc.MARCReader(r.data):
    if i > 0:
        if marc_separator:
            print(marc_separator)
        else:
            print(',')
    if marc_separator:
        print(record.as_marc())
    else:
        print(record.as_json())
    i += 1
if not marc_separator:
    print(']')
