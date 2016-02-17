import os
import mock
import pytest
from xml2kinto.records import Records, XMLRecords, KintoRecords, same_record

record = {'id': 'foobar'}


class RecordsTest(Records):
    def _load(self):
        return [record]


class TestRecords:
    def test_load_raises_a_not_implemented_error(self):
        with pytest.raises(NotImplementedError):
            Records({})

    def test_find_return_the_record_if_present_in_records(self):
        records = RecordsTest({})
        assert records.find('foobar') == record

    def test_fields_is_set_as_a_property(self):
        records = RecordsTest(mock.sentinel.fields)
        assert records.fields == mock.sentinel.fields

    def test_options_default_to_an_empty_dict_if_not_passed(self):
        records = RecordsTest(mock.sentinel.fields)
        assert records.options == {}

    def test_options_is_set_as_a_property_if_passed(self):
        records = RecordsTest({}, options=mock.sentinel.options)
        assert records.options == mock.sentinel.options

    def test_load_is_called_in_init(self):
        with mock.patch.object(RecordsTest, '_load') as mocked_load:
            RecordsTest({})
            mocked_load.assert_called_with()


class TestXMLRecords:
    def test_load_records_from_a_filename(self):
        here = os.path.dirname(__file__)
        test_file = os.path.join(here, 'test_blocklist.xml')
        xml_records = XMLRecords(('issuerName', 'serialNumber', 'subject',
                                  'pubKeyHash'), options={
            'filename': test_file,
            'xpath': 'certItems/*'
        })
        assert len(xml_records.records) == 10


class TestKintoRecords:
    collection_name = 'blocklist'

    def test_load_records_from_a_kinto_server(self):
        record = mock.MagicMock()
        record.id = "85547569-b7f8-9f18-1641-ff7f056ef16a"
        record.data = {
            "issuerName": "MDIxCzAJBgNVBAYTAkNOMQ4wDAYDVQQKEwVDTk5JQzETMBEG"
            "A1UEAxMKQ05OSUMgUk9PVA==",
            "serialNumber": "STMAjg=="
        }

        with mock.patch('xml2kinto.records.kinto.Client') as mocked_client:
            mocked_client.return_value.get_records.return_value = [record]
            kinto_records = KintoRecords(('issuerName', 'serialNumber'),
                                         options={
                                             'server': 'http://example.com/v1',
                                             'auth': ('user', 'pass'),
                                             'bucket_name': 'blocklists',
                                             'collection_name': 'certificates',
                                             'permissions': {}})
            assert len(kinto_records.records) == 1

    def test_create_collection_if_does_not_exists(self):
        with mock.patch('xml2kinto.records.kinto.Client') as mocked_client:
            mocked_client.return_value.get_records.return_value = []

            KintoRecords(('issuerName', 'serialNumber'),
                         options={
                             'server': 'http://example.com/v1',
                             'auth': ('user', 'pass'),
                             'bucket_name': 'blocklists',
                             'collection_name': 'certificates',
                             'permissions': {"read": ["system.Everyone"]}})
            mocked_client.return_value.create_collection. \
                assert_called_with('certificates',
                                   permissions={"read": ["system.Everyone"]})

    def test_can_delete_records(self):
        with mock.patch('xml2kinto.records.kinto.Client'):
            records = KintoRecords(('issuerName', 'serialNumber'),
                                   options={
                                       'server': 'http://example.com/v1',
                                       'auth': ('user', 'pass'),
                                       'bucket_name': 'blocklists',
                                       'collection_name': 'certificates',
                                       'permissions': {}})

        with mock.patch.object(records, 'client'):
            records.delete({'id': 'foobar'})
            records.client.delete_record.assert_called_with('foobar')

    def test_can_create_data(self):
        with mock.patch('xml2kinto.records.kinto.Client'):
            records = KintoRecords(('issuerName', 'serialNumber'),
                                   options={
                                       'server': 'http://example.com/v1',
                                       'auth': ('user', 'pass'),
                                       'bucket_name': 'blocklists',
                                       'collection_name': 'certificates',
                                       'permissions': {}})

        with mock.patch.object(records, 'client') as mocked_client:
            mocked_client.create_record = lambda x: x
            record = records.create({'issuerName': 'foo',
                                     'serialNumber': 'bar'})
            assert 'id' in record


class TestSameRecord:
    def test_return_false_if_different(self):
        fields = ('serialNumber', 'issuerName')
        record1 = {'serialNumber': 'foo', 'issuerName': 'bar'}
        record2 = {'serialNumber': 'BAR', 'issuerName': 'FOO'}
        assert not same_record(fields, record1, record2)
        record3 = {'subject': 'foo', 'pubKeyHash': 'bar'}
        assert not same_record(fields, record1, record3)

    def test_return_true_if_having_same_fields(self):
        fields = ('serialNumber', 'issuerName')
        record1 = {'serialNumber': 'foo', 'issuerName': 'bar',
                   'last_modified': 1234}
        record2 = {'serialNumber': 'foo', 'issuerName': 'bar',
                   'last_modified': 4567}
        assert same_record(fields, record1, record2)
