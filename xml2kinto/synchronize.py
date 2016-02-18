from __future__ import print_function

from kinto_client.exceptions import KintoException

from xml2kinto.exceptions import SynchronizationError
from xml2kinto.records import XMLRecords, KintoRecords, same_record


def synchronize(collections, kinto_options):
    server = kinto_options['server']
    auth = kinto_options['auth']
    permissions = kinto_options['permissions']

    print('Working on %r' % server)

    for collection, options in collections.items():
        print('Working on %s' % collection)
        options['server'] = server
        options['auth'] = auth
        options['permissions'] = permissions
        fields = options['fields']

        print('Reading data from %r' % options['filename'])
        xml = XMLRecords(fields, options=options)
        kinto = KintoRecords(fields, options=options)
        to_delete = []
        to_update = []
        to_create = []

        print('Syncing to %s/buckets/%s/collections/%s/records' % (
            options['server'],
            options['bucket_name'],
            options['collection_name']))

        # looking at kinto to list records
        # to delete or to update
        for record in kinto.records:
            xml_rec = xml.find(record['id'])
            if xml_rec is None:
                to_delete.append(record)
            else:
                if not same_record(fields, xml_rec, record):
                    to_update.append(xml_rec)

        # new records ?
        for record in xml.records:
            kinto_rec = kinto.find(record['id'])
            if not kinto_rec:
                to_create.append(record)

        print('- %d records to create.' % len(to_create))
        print('- %d records to delete.' % len(to_delete))
        print('- %d records to update.' % len(to_update))

        for record in to_delete:
            try:
                kinto.delete(record)
            except KintoException as e:
                raise SynchronizationError(e.response.content)

        for record in to_create + to_update:
            try:
                kinto.create(record)
            except KintoException as e:
                raise SynchronizationError(e.response.content)

    print('Done!')
