import unittest
import mock

from xml2kinto.__main__ import main, kinto_server, xml_file, auth


class TestMain(unittest.TestCase):
    def test_main_default(self):
        # let's check that main() parsing uses our defaults
        with mock.patch('xml2kinto.__main__.synchronize') as sync:
            main([])

            options = sync.call_args[1]['kinto_options']
            self.assertEqual(options['server'], kinto_server)
            self.assertEqual(options['auth'], auth)
            options = sync.call_args[0][0][0]['certificates']
            self.assertEqual(options['filename'], xml_file)

    def test_main_custom_server(self):
        with mock.patch('xml2kinto.__main__.synchronize') as sync:
            main(['-s', 'http://yeah'])
            options = sync.call_args[1]['kinto_options']
            self.assertEqual(options['server'], 'http://yeah')
