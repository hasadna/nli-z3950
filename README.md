# nli-z3950

Script to help getting bibliographical data from The National Library of Israel using Z3950 protocol and MARC format

The script dumps JSON serialization of the MARC data by default, optionally it can also dump MARC data in the original, binary MARC21 format


## Usage

Get records for the given search phrases

Requires a csv file under `data/search_phrases.csv` which contains a single `search_phrase` column where each row should contain a single keyword or phrase

```
docker run -it -v `pwd`/data:/data orihoch/nli-z3950 run ./keywords-search
```

Output data will be available under `data` directory

Get datapackage of records using CCL query "בדיקה"

```
docker run -it -v `pwd`/data:/data \
           -e NLI_DB_NAME=ULI02 \
           -e 'NLI_CCL_QUERY="בדיקה"' orihoch/nli-z3950 run ./load_marc_data
```

Stream binary MARC21 data directly

```
docker run --entrypoint python orihoch/nli-z3950 nli-z3950.py2 ULI02 '"בדיקה"' ----------
```


## Using CCL Queries

See https://software.indexdata.com/yaz/doc/tools.html#CCL for some examples


## Development

Build and run locally

```
docker build -t nli-z3950 . &&\
docker run -it -e NLI_DB_NAME=ULI02 \
           -e 'NLI_CCL_QUERY="בדיקה"' \
           -v `pwd`/data:/data \
           nli-z3950 run --verbose ./load_marc_data
```

Build in the Google cloud

```
IMAGE_TAG=gcr.io/hasadna-oknesset/nli-z3950
CLOUDSDK_CORE_PROJECT=hasadna-oknesset
PROJECT_NAME=nli-z3950
gcloud container builds submit --substitutions _IMAGE_TAG=${IMAGE_TAG},_CLOUDSDK_CORE_PROJECT=${CLOUDSDK_CORE_PROJECT},_PROJECT_NAME=${PROJECT_NAME} \
                               --config cloudbuild.yaml . &&\
gcloud docker -- pull gcr.io/hasadna-oknesset/nli-z3950-latest
```
