from __future__ import print_function

from kinto_client.exceptions import KintoException

from xml2kinto.exceptions import SynchronizationError
from xml2kinto.records import KintoRecords, same_record


def get_diff(source, dest):
    """Get the diff between two records list."""
    to_delete = []
    to_update = []
    to_create = []
    # looking at dest to delete or to update
    for record in dest:
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


def synchronize(records, fields, server, auth, bucket, collection,
                permissions):
    print('Working on collection {}/{} on server {}'.format(
        bucket, collection, server))
    options['server'] = server
    options['auth'] = auth
    options['permissions'] = permissions
    fields = options['fields']

    print('Reading data from %r' % options['filename'])
    kinto = KintoRecords(fields, options=options)
    to_delete = []
    to_update = []
    to_create = []

    print('Syncing to %s/buckets/%s/collections/%s/records' % (
        options['server'],
        options['bucket_name'],
        options['collection_name']))

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
