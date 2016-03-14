def get_kinto_records(kinto_client, bucket, collection, permissions,
                      schema=None):
    """Return all the kinto records for this bucket/collection."""
    # Create bucket if needed
    kinto_client.create_bucket(bucket, if_not_exists=True)
    collection_data = {}
    if schema is not None:
        collection_data['schema'] = schema

    resp = kinto_client.create_collection(
        collection, bucket, permissions=permissions, if_not_exists=True)

    if 200 <= resp.status_code < 300:
        previous_collection = resp.json()['data']
    elif resp.status_code == 412:
        previous_collection = resp.json()['details']['existing']

    if schema and ('schema' not in previous_collection or
                   previous_collection['schema'] != schema):
        kinto_client.patch_collection(collection, bucket, data=collection_data)

    return kinto_client.get_records(bucket=bucket, collection=collection)
