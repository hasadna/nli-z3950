FROM ubuntu:trusty
RUN apt-get update && apt-get install -y --force-yes curl python-pip software-properties-common python-software-properties \
                                         libleveldb-dev libleveldb1
RUN curl 'https://pypi.python.org/packages/6a/34/8176b841926a2add20524a9f74c307ac5fe6e33e9f4af12a58e6f7223982/mollyZ3950-2.04-molly1.tar.gz#md5=a0e5d7bb395ae31026afc7f974711630' > mollyZ3950-2.04-molly1.tar.gz &&\
    pip install ./mollyZ3950-2.04-molly1.tar.gz &&\
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

COPY nli_z3950/*.py /nli_z3950/
COPY setup.py /
RUN pip install -e .

COPY *.py *.py2 *.sh *.yaml ./

ENTRYPOINT ["./entrypoint.sh"]
