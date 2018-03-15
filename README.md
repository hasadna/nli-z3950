# nli-z3950

Script to help getting bibliographical data from The National Library of Israel using Z3950 protocol and MARC format

The script dumps JSON serialization of the MARC data by default, optionally it can also dump MARC data in the original, binary MARC21 format


## Usage

Get datapackage of records containing the text "בדיקה"

```
docker run -e NLI_DB_NAME=ULI02 \
           -e 'NLI_CCL_QUERY="בדיקה אחת שתיים שלוש"' \
           -v `pwd`/data:/data \
           orihoch/nli-z3950 run ./load_marc_data
```

Datapackages are available under `data/` directory

Stream binary MARC21 data directly

```
docker run --entrypoint python orihoch/nli-z3950 nli-z3950.py2 ULI02 '"בדיקה"' ----------
```


## Development

Build and run locally

```
docker build -t nli-z3950 . &&\
docker run -e NLI_DB_NAME=ULI02 \
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
