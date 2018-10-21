FROM ubuntu:trusty
RUN apt-get update && apt-get install -y --force-yes curl python-pip software-properties-common python-software-properties \
                                         libleveldb-dev libleveldb1

COPY mollyZ3950-2.04-molly1 ./mollyZ3950-2.04-molly1
RUN pip install -e mollyZ3950-2.04-molly1 &&\
    pip install pymarc
RUN add-apt-repository -y ppa:deadsnakes/ppa && apt-get update && apt-get install -y python3.6 python3.6-dev
RUN curl https://bootstrap.pypa.io/get-pip.py > get-pip.py && python3.6 ./get-pip.py

ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

# RUN pip install 'datapackage-pipelines[speedup,develop]'
# installing from master due to bug with --verbose, can change to normal pip installation once new version is released
RUN curl -L 'https://github.com/frictionlessdata/datapackage-pipelines/archive/master.zip' > datapackage-pipelines.zip &&\
    pip install 'datapackage-pipelines.zip[speedup,develop]'
RUN pip install pymarc
RUN pip install pipenv

COPY Pipfile Pipfile.lock ./
RUN pipenv install --system --deploy

COPY nli_z3950/*.py /nli_z3950/
COPY setup.py /
RUN pip install -e .

COPY *.py *.py2 *.sh *.yaml ./

# CCL = more general / user friendly query language
# CQL = stricter query language
ENV QUERY_TYPE=CCL

ENTRYPOINT ["./entrypoint.sh"]
