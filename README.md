# nli-z3950

Script to help getting bibliographical data from The National Library of Israel using Z3950 protocol and MARC format

The script dumps JSON serialization of the MARC data by default, optionally it can also dump MARC data in the original, binary MARC21 format


## Usage

### Stateful search using [CCL queries](https://software.indexdata.com/yaz/doc/tools.html#CCL)

Search queries should be provided in `data/ccl_queries/ccl_queries.csv` with a single `ccl_query` column

Search takes the result as input and only updates new entires

```
docker run -it -v `pwd`/data:/data orihoch/nli-z3950 run ./search
```

Output data will be available under `data/search_results` directory

### Export search results

```
docker run -it -v `pwd`/data:/data orihoch/nli-z3950 run ./search_export
```

## Using CCL Queries

See https://software.indexdata.com/yaz/doc/tools.html#CCL for some examples


## Development

### Using Docker

Build and run locally

```
docker build -t nli-z3950 . &&\
docker run -it -v `pwd`/data:/data orihoch/nli-z3950 run --verbose ./search
```

### Locally

See the Dockerfile for installation instructions. You need both Python 2.7 and Python 3.6 and some dependencies.

```
NLI_PYTHON2=python2 MAX_RECORDS=50 dpp run --verbose ./search
```

### Sync with google storage

```
sudo chown -R $USER data
gsutil -m rsync -r ./data gs://knesset-data-pipelines/hasadna-migdar-data/$USER-`date +%Y-%m-%d_%H-%m`
```

### Jupyter Lab

Activate the virtualenv

```
pipenv shell
```

Install Jupyter

```
pip install jupyter jupyterlab ipython
```

Start Jupyter lab

```
jupyter lab
```