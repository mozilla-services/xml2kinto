import os
import unittest
import mock
import pytest
from kinto_client.exceptions import KintoException
from xml2kinto.exceptions import SynchronizationError
from xml2kinto.synchronize import synchronize

FIELDS = ('serialNumber', 'issuerName')

existing_record = {
    "id": "85547569-b7f8-9f18-1641-ff7f056ef16a",
    "issuerName": "MDIxCzAJBgNVBAYTAkNOMQ4wDAYDVQQKEwVDTk5JQzE"
    "TMBEGA1UEAxMKQ05OSUMgUk9PVA==",
    "serialNumber": "STMAjg=="
}
updated_record = {
    "id": "a81803c3-3c06-1549-bbe3-4b7d4c739f25",
    "issuerName": "MDIxCzAJBgNVBAYTAkNOMQ4wDAYDVQQKEwVDTk5JQzE"
    "TMBEGA1UEAxMKQ05OSUMgUk9PVA==",
    "serialNumber": "STMAjg=="
}
deleted_record = {
    "id": "12345678",
    "issuerName": "MHExCzAJBgNVBAYTAkRFMRwwGgYDVQQKExNEZXV0c2NoZSBUZWxla29tI"
    "EFHMR8wHQYDVQQLExZULVRlbGVTZWMgVHJ1c3QgQ2VudGVyMSMwIQYDVQQDExpEZXV0c2No"
    "ZSBUZWxla29tIFJvb3QgQ0EgMg==",
    "serialNumber": "ARQ="
}


class TestSynchronize(unittest.TestCase):
    def setUp(self):
        here = os.path.dirname(__file__)
        test_file = os.path.join(here, 'test_synchronize.xml')
        certs = {'fields': FIELDS,
                 'filename': test_file,
                 'xpath': 'certItems/*',
                 'collection_name': 'certificates'}

        self.collections = {'certificates': certs}

    def test_synchronize_create_missing_records(self):
        with mock.patch('xml2kinto.synchronize.KintoRecords') as KintoRecords:
            KintoRecords.return_value.records = []
            KintoRecords.return_value.find.return_value = None
            kinto_options = mock.MagicMock()
            synchronize(self.collections, kinto_options=kinto_options)
            assert KintoRecords.return_value.create.call_count == 2

    def test_synchronize_delete_removed_records(self):
        with mock.patch('xml2kinto.synchronize.KintoRecords') as KintoRecords:
            KintoRecords.return_value.records = [deleted_record]
            KintoRecords.return_value.find.return_value = None

            synchronize(self.collections, kinto_options=mock.MagicMock())
            assert KintoRecords.return_value.delete.call_count == 1

    def test_synchronize_update_modified_records(self):
        with mock.patch('xml2kinto.synchronize.KintoRecords') as KintoRecords:
            KintoRecords.return_value.records = [existing_record,
                                                 updated_record]
            KintoRecords.return_value.find.return_value = True

            synchronize(self.collections, kinto_options=mock.MagicMock())
            assert KintoRecords.return_value.create.call_count == 1
            assert KintoRecords.return_value.delete.call_count == 0

    def test_synchronize_raises_SynchronizationError_if_delete_fails(self):
        error = KintoException()
        error.response = mock.MagicMock(content='foobar')

        with mock.patch('xml2kinto.synchronize.KintoRecords') as KintoRecords:
            KintoRecords.return_value.records = [deleted_record]
            KintoRecords.return_value.find.return_value = None
            KintoRecords.return_value.delete.side_effect = error

            with pytest.raises(SynchronizationError):
                synchronize(self.collections, kinto_options=mock.MagicMock())

    def test_synchronize_raises_SynchronizationError_if_create_fails(self):
        error = KintoException()
        error.response = mock.MagicMock(content='foobar')

        with mock.patch('xml2kinto.synchronize.KintoRecords') as KintoRecords:
            KintoRecords.return_value.records = []
            KintoRecords.return_value.find.return_value = None
            KintoRecords.return_value.create.side_effect = error

            with pytest.raises(SynchronizationError):
                synchronize(self.collections, kinto_options=mock.MagicMock())
