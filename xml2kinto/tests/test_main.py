import mock
import unittest

from xml2kinto import __main__ as main


def test_sync_records_calls_the_scenario():
    with mock.patch(
            'xml2kinto.__main__.get_xml_records',
            return_value=mock.sentinel.xml_records) as get_xml_records:
        with mock.patch(
                'xml2kinto.__main__.get_kinto_records',
                return_value=mock.sentinel.kinto_records) as get_kinto_records:
            with mock.patch(
                    'xml2kinto.__main__.get_diff',
                    return_value=(
                        mock.sentinel.to_create,
                        mock.sentinel.to_delete)) as get_diff:
                with mock.patch(
                        'xml2kinto.__main__.push_changes') as push_changes:

                    main.sync_records(
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
                        permissions=main.COLLECTION_PERMISSIONS)

                    get_diff.assert_called_with(
                        mock.sentinel.xml_records, mock.sentinel.kinto_records)
                    push_changes.assert_called_with(
                        (mock.sentinel.to_create, mock.sentinel.to_delete),
                        mock.sentinel.kinto_client,
                        bucket=mock.sentinel.bucket,
                        collection=mock.sentinel.collection)


class TestMain(unittest.TestCase):
    def assert_arguments(self, mocked, kinto_client, **kwargs):
        kwargs.setdefault('kinto_server', main.KINTO_SERVER)
        kwargs.setdefault('auth', main.AUTH)
        kwargs.setdefault('filename', main.XML_FILE)
        kwargs.setdefault('cert_bucket', main.CERT_BUCKET)
        kwargs.setdefault('cert_collection', main.CERT_COLLECTION)
        kwargs.setdefault('gfx_bucket', main.GFX_BUCKET)
        kwargs.setdefault('gfx_collection', main.GFX_COLLECTION)
        kwargs.setdefault('addons_bucket', main.ADDONS_BUCKET)
        kwargs.setdefault('addons_collection', main.ADDONS_COLLECTION)
        kwargs.setdefault('plugins_bucket', main.PLUGINS_BUCKET)
        kwargs.setdefault('plugins_collection', main.PLUGINS_COLLECTION)

        kinto_client.assert_called_with(server_url=kwargs['kinto_server'],
                                        auth=kwargs['auth'],
                                        bucket=None,
                                        collection=None)

        cert_arguments = {
            'fields': main.CERT_ITEMS_FIELDS,
            'filename': kwargs['filename'],
            'xpath': 'certItems/*',
            'kinto_client': kinto_client.return_value,
            'bucket': kwargs['cert_bucket'],
            'collection': kwargs['cert_collection']
        }

        mocked.assert_any_call(**cert_arguments)

        gfx_arguments = {
            'fields': main.GFX_ITEMS_FIELDS,
            'filename': kwargs['filename'],
            'xpath': 'gfxItems/*',
            'kinto_client': kinto_client.return_value,
            'bucket': kwargs['gfx_bucket'],
            'collection': kwargs['gfx_collection']
        }

        mocked.assert_any_call(**gfx_arguments)

        addons_arguments = {
            'fields': main.ADDONS_ITEMS_FIELDS,
            'filename': kwargs['filename'],
            'xpath': 'emItems/*',
            'kinto_client': kinto_client.return_value,
            'bucket': kwargs['addons_bucket'],
            'collection': kwargs['addons_collection']
        }

        mocked.assert_any_call(**addons_arguments)

        plugins_arguments = {
            'fields': main.PLUGINS_ITEMS_FIELDS,
            'filename': kwargs['filename'],
            'xpath': 'pluginItems/*',
            'kinto_client': kinto_client.return_value,
            'bucket': kwargs['plugins_bucket'],
            'collection': kwargs['plugins_collection']
        }

        mocked.assert_any_call(**plugins_arguments)

    def test_main_default(self):
        # let's check that main() parsing uses our defaults
        with mock.patch('kinto_client.cli_utils.Client') as MockedClient:
            with mock.patch('xml2kinto.__main__.sync_records') as mocked:
                main.main([])
                self.assert_arguments(mocked, MockedClient)

    def test_main_custom_server(self):
        with mock.patch('kinto_client.cli_utils.Client') as MockedClient:
            with mock.patch('xml2kinto.__main__.sync_records') as mocked:
                main.main(['-s', 'http://yeah'])
                self.assert_arguments(mocked, MockedClient,
                                      kinto_server='http://yeah')

    def test_can_define_the_xml_file(self):
        with mock.patch('kinto_client.cli_utils.Client') as MockedClient:
            with mock.patch('xml2kinto.__main__.sync_records') as mocked:
                main.main(['-x', '/tmp/toto.xml'])
                self.assert_arguments(mocked, MockedClient,
                                      filename='/tmp/toto.xml')

    def test_can_define_the_certificates_bucket_and_collection(self):
        with mock.patch('kinto_client.cli_utils.Client') as MockedClient:
            with mock.patch('xml2kinto.__main__.sync_records') as mocked:
                main.main(
                    ['--cert-bucket', 'bucket',
                     '--cert-collection', 'collection'])
                self.assert_arguments(mocked, MockedClient,
                                      cert_bucket='bucket',
                                      cert_collection='collection')

    def test_can_define_the_gfx_bucket_and_collection(self):
        with mock.patch('kinto_client.cli_utils.Client') as MockedClient:
            with mock.patch('xml2kinto.__main__.sync_records') as mocked:
                main.main(
                    ['--gfx-bucket', 'bucket',
                     '--gfx-collection', 'collection'])
                self.assert_arguments(mocked, MockedClient,
                                      gfx_bucket='bucket',
                                      gfx_collection='collection')

    def test_can_define_the_addons_bucket_and_collection(self):
        with mock.patch('kinto_client.cli_utils.Client') as MockedClient:
            with mock.patch('xml2kinto.__main__.sync_records') as mocked:
                main.main(
                    ['--addons-bucket', 'bucket',
                     '--addons-collection', 'collection'])
                self.assert_arguments(mocked, MockedClient,
                                      addons_bucket='bucket',
                                      addons_collection='collection')

    def test_can_define_the_plugins_bucket_and_collection(self):
        with mock.patch('kinto_client.cli_utils.Client') as MockedClient:
            with mock.patch('xml2kinto.__main__.sync_records') as mocked:
                main.main(
                    ['--plugins-bucket', 'bucket',
                     '--plugins-collection', 'collection'])
                self.assert_arguments(mocked, MockedClient,
                                      plugins_bucket='bucket',
                                      plugins_collection='collection')

    def test_can_define_the_auth_credentials(self):
        with mock.patch('kinto_client.cli_utils.Client') as MockedClient:
            with mock.patch('xml2kinto.__main__.sync_records') as mocked:
                main.main(['--auth', 'user:pass'])
                self.assert_arguments(mocked, MockedClient,
                                      auth=('user', 'pass'))
