import mock
import os
import unittest

from xml2kinto.__main__ import (
    main, sync_records, COLLECTION_PERMISSIONS,
    cert_items_fields, addons_items_fields,
    plugins_items_fields, gfx_items_fields
)


def test_sync_records_calls_the_scenario():
    with mock.patch('xml2kinto.__main__.get_xml_records',
                    return_value=[]) as get_xml_records:
        with mock.patch('xml2kinto.__main__.get_kinto_records',
                        return_value=[]) as get_kinto_records:
            with mock.patch('xml2kinto.__main__.get_diff',
                            return_value=([], [])) as get_diff:
                with mock.patch(
                        'xml2kinto.__main__.synchronize') as synchronize:

                    sync_records(
                        mock.sentinel.fields, mock.sentinel.filename,
                        mock.sentinel.xpath, mock.sentinel.kinto_client,
                        mock.sentinel.bucket, mock.sentinel.collection)

                    get_xml_records.assert_called_with(
                        fields=mock.sentinel.fields,
                        filename=mock.sentinel.filename,
                        xpath=mock.sentinel.xpath)

                    get_kinto_records.assert_called_with(
                        kinto_client=mock.sentinel.kinto_client,
                        bucket=mock.sentinel.bucket,
                        collection=mock.sentinel.collection,
                        permissions=COLLECTION_PERMISSIONS)

                    get_diff.assert_called_with([], [])
                    synchronize.assert_called_with(
                        ([], []),
                        mock.sentinel.kinto_client,
                        bucket=mock.sentinel.bucket,
                        collection=mock.sentinel.collection)


class TestMain(unittest.TestCase):
    def assert_arguments(self, mocked, kinto_client, **kwargs):
        filename = os.path.join(
            os.path.dirname(
                os.path.dirname(
                    os.path.dirname(__file__))), 'blocklist.xml')

        kwargs.setdefault('kinto_server', 'http://localhost:8888/v1')
        kwargs.setdefault('auth', ('mark', 'p4ssw0rd'))
        kwargs.setdefault('filename', filename)
        kwargs.setdefault('cert_bucket', 'blocklists')
        kwargs.setdefault('cert_collection', 'certificates')
        kwargs.setdefault('gfx_bucket', 'blocklists')
        kwargs.setdefault('gfx_collection', 'gfx')
        kwargs.setdefault('addons_bucket', 'blocklists')
        kwargs.setdefault('addons_collection', 'addons')
        kwargs.setdefault('plugins_bucket', 'blocklists')
        kwargs.setdefault('plugins_collection', 'plugins')

        kinto_client.assert_called_with(server_url=kwargs['kinto_server'],
                                        auth=kwargs['auth'])

        cert_arguments = {
            'fields': cert_items_fields,
            'filename': kwargs['filename'],
            'xpath': 'certItems/*',
            'kinto_client': kinto_client.return_value,
            'bucket': kwargs['cert_bucket'],
            'collection': kwargs['cert_collection']
        }

        mocked.assert_any_call(**cert_arguments)

        gfx_arguments = {
            'fields': gfx_items_fields,
            'filename': kwargs['filename'],
            'xpath': 'gfxItems/*',
            'kinto_client': kinto_client.return_value,
            'bucket': kwargs['gfx_bucket'],
            'collection': kwargs['gfx_collection']
        }

        mocked.assert_any_call(**gfx_arguments)

        addons_arguments = {
            'fields': addons_items_fields,
            'filename': kwargs['filename'],
            'xpath': 'emItems/*',
            'kinto_client': kinto_client.return_value,
            'bucket': kwargs['addons_bucket'],
            'collection': kwargs['addons_collection']
        }

        mocked.assert_any_call(**addons_arguments)

        plugins_arguments = {
            'fields': plugins_items_fields,
            'filename': kwargs['filename'],
            'xpath': 'pluginItems/*',
            'kinto_client': kinto_client.return_value,
            'bucket': kwargs['plugins_bucket'],
            'collection': kwargs['plugins_collection']
        }

        mocked.assert_any_call(**plugins_arguments)

    def test_main_default(self):
        # let's check that main() parsing uses our defaults
        with mock.patch('xml2kinto.__main__.Client') as MockedClient:
            with mock.patch('xml2kinto.__main__.sync_records') as mocked:
                main([])
                self.assert_arguments(mocked, MockedClient)

    def test_main_custom_server(self):
        with mock.patch('xml2kinto.__main__.Client') as MockedClient:
            with mock.patch('xml2kinto.__main__.sync_records') as mocked:
                main(['-s', 'http://yeah'])
                self.assert_arguments(mocked, MockedClient,
                                      kinto_server='http://yeah')

    def test_can_define_the_xml_file(self):
        with mock.patch('xml2kinto.__main__.Client') as MockedClient:
            with mock.patch('xml2kinto.__main__.sync_records') as mocked:
                main(['-x', '/tmp/toto.xml'])
                self.assert_arguments(mocked, MockedClient,
                                      filename='/tmp/toto.xml')

    def test_can_define_the_certificates_bucket_and_collection(self):
        with mock.patch('xml2kinto.__main__.Client') as MockedClient:
            with mock.patch('xml2kinto.__main__.sync_records') as mocked:
                main(['--cert-bucket', 'bucket',
                      '--cert-collection', 'collection'])
                self.assert_arguments(mocked, MockedClient,
                                      cert_bucket='bucket',
                                      cert_collection='collection')

    def test_can_define_the_gfx_bucket_and_collection(self):
        with mock.patch('xml2kinto.__main__.Client') as MockedClient:
            with mock.patch('xml2kinto.__main__.sync_records') as mocked:
                main(['--gfx-bucket', 'bucket',
                      '--gfx-collection', 'collection'])
                self.assert_arguments(mocked, MockedClient,
                                      gfx_bucket='bucket',
                                      gfx_collection='collection')

    def test_can_define_the_addons_bucket_and_collection(self):
        with mock.patch('xml2kinto.__main__.Client') as MockedClient:
            with mock.patch('xml2kinto.__main__.sync_records') as mocked:
                main(['--addons-bucket', 'bucket',
                      '--addons-collection', 'collection'])
                self.assert_arguments(mocked, MockedClient,
                                      addons_bucket='bucket',
                                      addons_collection='collection')

    def test_can_define_the_plugins_bucket_and_collection(self):
        with mock.patch('xml2kinto.__main__.Client') as MockedClient:
            with mock.patch('xml2kinto.__main__.sync_records') as mocked:
                main(['--plugins-bucket', 'bucket',
                      '--plugins-collection', 'collection'])
                self.assert_arguments(mocked, MockedClient,
                                      plugins_bucket='bucket',
                                      plugins_collection='collection')

    def test_can_define_the_auth_credentials(self):
        with mock.patch('xml2kinto.__main__.Client') as MockedClient:
            with mock.patch('xml2kinto.__main__.sync_records') as mocked:
                main(['--auth', 'user:pass'])
                self.assert_arguments(mocked, MockedClient,
                                      auth=('user', 'pass'))
