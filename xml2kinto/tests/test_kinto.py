import mock
from xml2kinto.kinto import get_kinto_records


def test_get_kinto_records_try_to_create_the_bucket():
    kinto_client = mock.MagicMock()
    get_kinto_records(kinto_client, mock.sentinel.bucket,
                      mock.sentinel.collection, mock.sentinel.permissions)

    kinto_client.create_bucket.assert_called_with(mock.sentinel.bucket,
                                                  if_not_exists=True)


def test_get_kinto_records_try_to_create_the_collection_with_permissions():
    kinto_client = mock.MagicMock()
    get_kinto_records(kinto_client, mock.sentinel.bucket,
                      mock.sentinel.collection, mock.sentinel.permissions)

    kinto_client.create_collection.assert_called_with(
        mock.sentinel.collection, mock.sentinel.bucket,
        permissions=mock.sentinel.permissions, if_not_exists=True)


def test_get_kinto_records_gets_a_list_of_records():
    kinto_client = mock.MagicMock()
    get_kinto_records(kinto_client, mock.sentinel.bucket,
                      mock.sentinel.collection, mock.sentinel.permissions)

    kinto_client.get_records.assert_called_with(
        bucket=mock.sentinel.bucket, collection=mock.sentinel.collection)
