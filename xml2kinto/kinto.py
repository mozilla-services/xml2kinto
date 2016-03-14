def get_kinto_records(kinto_client, bucket, collection, permissions):
    """Return all the kinto records for this bucket/collection."""
    # Create bucket if needed
    kinto_client.create_bucket(bucket, if_not_exists=True)
    kinto_client.create_collection(
        collection, bucket, permissions=permissions, if_not_exists=True)
    return kinto_client.get_records(bucket=bucket, collection=collection)
