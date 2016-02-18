import os
import argparse

from xml2kinto.synchronize import synchronize

# options to move to a config file
xml_file = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        '..', 'blocklist.xml'))
auth = ('mark', 'p4ssw0rd')
collection_permissions = {'read': ["system.Everyone"]}
bucket_name = u'blocklists'
collection_name = u'certificates'
kinto_server = 'http://localhost:8888/v1'

cert_items_fields = ('subject', 'pubKeyHash', 'serialNumber', 'issuerName')
gfx_items_fields = ('os', 'vendor', 'feature', 'featureStatus',
                    'driverVersion', 'driverVersionComparator',
                    ('devices', {'xpath': 'devices/*'}))


def main(args=None):
    parser = argparse.ArgumentParser(description='Syncs a Kinto DB.')

    parser.add_argument('-s', '--kinto-server', help='Kinto Server',
                        type=str, default=kinto_server)

    parser.add_argument('-x', '--xml-file', help='XML Source file',
                        type=str, default=xml_file)

    parser.add_argument('-a', '--auth', help='BasicAuth user:pass',
                        type=str, default=':'.join(auth))

    args = parser.parse_args(args=args)

    collections = {'certificates': {'fields': cert_items_fields,
                                    'filename': args.xml_file,
                                    'xpath': 'certItems/*',
                                    'bucket_name': bucket_name,
                                    'collection_name': collection_name},
                   'gfx': {'fields': gfx_items_fields,
                           'filename': args.xml_file,
                           'xpath': 'gfxItems/*',
                           'bucket_name': bucket_name,
                           'collection_name': 'gfx'}}

    synchronize(collections,
                kinto_options={'server': args.kinto_server,
                               'auth': tuple(args.auth.split(':')),
                               'permissions': collection_permissions})


if __name__ == '__main__':  # pragma: nocover
    main()
