from datapackage_pipelines.wrapper import ingest, spew
from datapackage_pipelines.utilities.resources import PROP_STREAMING
import logging
import yaml
from functools import lru_cache


@lru_cache(maxsize=1)
def pipeline_spec():
    with open('pipeline-spec.yaml', 'r') as f:
        return yaml.load(f)


@lru_cache(maxsize=1)
def export_keys():
    return pipeline_spec()['search_export']['pipeline'][3]['parameters']['export_keys']


parameters, datapackage, resources, stats = ingest() + ({},)


resource_names = [descriptor['name'] for descriptor in datapackage['resources']]


for idx, name in enumerate(reversed(resource_names)):
    if name in ('kns_committee', 'kns_committeesession',
                'document_background_material_titles', 'kns_documentcommitteesession'):
        del datapackage['resources'][len(resource_names)-idx-1]


schema_fields = [{'name': k, 'type': 'string'}
                  for k in export_keys()
                  if k != 'json']


datapackage['resources'].append({PROP_STREAMING: True,
                                 'name': 'women_committee_background_material',
                                 'path': 'women_committee_background_material.csv',
                                 'schema': {'fields': [{'name': k, 'type': 'string'}
                                                       for k in export_keys()
                                                       if k != 'json']}})


def get_resources():
    committees = {}
    sessions = {}
    documents = {}
    titles = {}

    def get_resource():
        for document_file_path, document_title in titles.items():
            document_file_path = document_file_path.replace('\\', '/')
            document = documents[document_file_path]
            session = sessions[document['CommitteeSessionID']]
            committee = committees[session['CommitteeID']]
            yield {'title': document_title['title'],
                   'pubyear': str(session['StartDate'].year),
                   'publisher': 'חומר רקע ישיבות {}'.format(committee['Name']),
                   'author': 'כנסת ישראל',
                   'language_code': 'heb',
                   'custom_metadata': '',
                   'publication_distribution_details': '',
                   'notes': 'הנושאים שנדונו בישיבה שאליה הוגש חומר הרקע: ' + ', '.join(session['topics']),
                   'tags': '',
                   'url': 'http://main.knesset.gov.il/Activity/committees/Women/Pages/CommitteeMaterial.aspx?ItemID={}'.format(document['CommitteeSessionID']),
                   'migdar_id': 'knscomdoc{}'.format(document['DocumentCommitteeSessionID']),
                   'item_type': '',
                   'first_ccl_query': '',
                   'marc_856': ''}

    for resource_name, resource in zip(resource_names, resources):
        for row in resource:
            if resource_name == 'kns_committee':
                committees[row['CommitteeID']] = row
            elif resource_name == 'kns_committeesession':
                sessions[row['CommitteeSessionID']] = row
            elif resource_name == 'kns_documentcommitteesession':
                documents[row['FilePath']] = row
            elif resource_name == 'document_background_material_titles':
                titles[row['FilePath']] = row
    yield get_resource()


spew(datapackage, get_resources(), stats)
