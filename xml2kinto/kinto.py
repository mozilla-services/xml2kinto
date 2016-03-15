from functools import partial


def update_schema_if_mandatory(old_collection, schema, patch_collection):
    if schema and ('schema' not in old_collection or
                   old_collection['schema'] != schema):

        patch_collection(data={'schema': schema})


def get_kinto_records(kinto_client, bucket, collection, permissions,
                      schema=None):
    """Return all the kinto records for this bucket/collection."""
    # Create bucket if needed
    kinto_client.create_bucket(bucket, if_not_exists=True)
    previous_collection = kinto_client.create_collection(
        collection, bucket, permissions=permissions, if_not_exists=True)

    patch_collection = partial(kinto_client.patch_collection,
                               bucket=bucket, collection=collection)

    update_schema_if_mandatory(previous_collection, schema, patch_collection)

    return kinto_client.get_records(bucket=bucket, collection=collection)
