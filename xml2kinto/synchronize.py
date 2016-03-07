from __future__ import print_function


def get_diff(source, dest):
    """Get the diff between two records list in this order:
        - to_create
        - to_delete
    """
    # First build a dict from the lists, with the ID as the key.
    source_dict = {record['id']: record for record in source}
    dest_dict = {record['id']: record for record in dest}

    source_keys = set(source_dict.keys())
    dest_keys = set(dest_dict.keys())
    to_create = source_keys - dest_keys
    to_delete = dest_keys - source_keys

    return ([source_dict[k] for k in to_create],
            [dest_dict[k] for k in to_delete])


def synchronize(diff, kinto_client, bucket, collection, permissions):
    to_create, to_delete = diff

    print('Syncing to {}{}'.format(
        kinto_client.session_kwargs['server_url'],
        kinto_client.endpoints.get(
            'records', bucket=bucket, collection=collection)))

    print('- {} records to create.'.format(len(to_create)))
    print('- {} records to delete.'.format(len(to_delete)))

    with kinto_client.batch(bucket=bucket, collection=collection) as batch:
        for record in to_delete:
            batch.delete_record(record)
        for record in to_create:
            batch.create_record(record)

    print('Done!')
