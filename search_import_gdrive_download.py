import logging, os
import googleapiclient.discovery
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseDownload
import csv
from tabulator import Stream


def main():
    # you should create a service account (on any google project) and share the drive to the service account's email
    SERVICE_ACCOUNT_FILE = os.environ['SERVICE_ACCOUNT_FILE']

    logging.info('authenticating using credentials from google service account')
    SCOPES = ['https://www.googleapis.com/auth/drive']
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    drive_service = googleapiclient.discovery.build('drive', 'v3', credentials=credentials)

    if os.path.exists('data/search_import/index.csv'):
        with Stream('data/search_import/index.csv', headers=1) as stream:
            existing_files = {row['id']: row for row in stream.iter(keyed=True)}
    else:
        existing_files = {}
    logging.info('downloading files to data/search_import')
    results = drive_service.files().list(q="'1-J9ox-6Zy9b3CdFNev3FtMmKsdWjYmeq' in parents", fields='files(id,kind,name,mimeType,modifiedTime)').execute()
    items = results.get('files', [])
    if items:
        assert not os.path.exists('data/search_import/temp_index.csv')
        with open('data/search_import/temp_index.csv', 'w') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(['id', 'name', 'modifiedTime'])
            for item in items:
                # print(item)
                if item['kind'] == 'drive#file' and item['mimeType'] == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
                    if (item['id'] in existing_files
                            and 'modifiedTime' in existing_files[item['id']]
                            and existing_files[item['id']]['modifiedTime'] == item['modifiedTime']
                    ):
                        print('skipping unmodified file {}'.format(item['name']))
                        csvwriter.writerow([item['id'], item['name'], item['modifiedTime']])
                    else:
                        with open('data/search_import/{}'.format(item['name']), 'wb') as f:
                            request = drive_service.files().get_media(fileId=item['id'])
                            downloader = MediaIoBaseDownload(f, request)
                            done = False
                            while done is False:
                                status, done = downloader.next_chunk()
                                print("Download %d%%." % int(status.progress() * 100))
                            csvwriter.writerow([item['id'], item['name'], item['modifiedTime']])
        os.rename('data/search_import/temp_index.csv', 'data/search_import/index.csv')

    with open('data/search_import/index.csv') as f:
        print(f.read())

    print('Great Success!')

    return 0


if __name__ == '__main__':
    exit(main())
