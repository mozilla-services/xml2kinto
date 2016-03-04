import os
import argparse

from xml2kinto.synchronize import synchronize
from xml2kinto.records.xml import get_records

# options to move to a config file
xml_file = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        '..', 'blocklist.xml'))
auth = ('mark', 'p4ssw0rd')
collection_permissions = {'read': ["system.Everyone"]}
bucket_name = u'blocklists'
collection_name = u'certificates'
kinto_server = 'http://localhost:8888/v1'

cert_items_fields = ('serialNumber', 'issuerName')
gfx_items_fields = ('blockID', 'os', 'vendor', 'feature', 'featureStatus',
                    'driverVersion', 'driverVersionComparator',
                    ('devices', {'xpath': 'devices/*'}))

addons_items_fields = (
    'blockID',
    ('id', {'name': 'guid'}),
    ('prefs', {'xpath': 'prefs/*'}),
    ('versionRange', {
        'xpath': 'versionRange',
        'fields': (
            'minVersion',
            'maxVersion',
            'severity',
            ('targetApplication', {
                'xpath': 'targetApplication',
                'fields': (
                    ('id', {'name': 'guid'}),
                    ('versionRange/minVersion', {'name': 'minVersion'}),
                    ('versionRange/maxVersion', {'name': 'maxVersion'})
                )
            })
        )
    })
)

plugins_items_fields = (
    'blockID', 'os',
    ('match/name=name', {'name': 'matchName'}),
    ('match/name=description', {'name': 'matchDescription'}),
    ('match/name=filename', {'name': 'matchFilename'}),
    'infoURL',
    ('versionRange', {
        'fields': (
            'minVersion',
            'maxVersion',
            'severity',
            'vulnerabilitystatus',
            ('targetApplication', {
                'fields': (
                    ('id', {'name': 'guid'}),
                    ('versionRange/minVersion', {'name': 'minVersion'}),
                    ('versionRange/maxVersion', {'name': 'maxVersion'})
                )
            })
        )})
)


def main(args=None):
    parser = argparse.ArgumentParser(description='Syncs a Kinto DB.')

    parser.add_argument('-s', '--kinto-server', help='Kinto Server',
                        type=str, default=kinto_server)

    parser.add_argument('-x', '--xml-file', help='XML Source file',
                        type=str, default=xml_file)

    parser.add_argument('-a', '--auth', help='BasicAuth user:pass',
                        type=str, default=':'.join(auth))

    args = parser.parse_args(args=args)

    # Import certificates

    # 1. Get XML Records
    # certificate_records = get_records(
    #     fields=cert_items_fields,
    #     filename=args.xml_file,
    #     xpath='certItems/*')

    # gfx_records = get_records(
    #     fields=gfx_items_fields,
    #     filename=args.xml_file,
    #     xpath='gfxItems/*')

    # addons_records = get_records(
    #     fields=addons_items_fields,
    #     filename=args.xml_file,
    #     xpath='emItems/*')

    plugins_records = get_records(
        fields=plugins_items_fields,
        filename=args.xml_file,
        xpath='pluginItem/*')

    print plugins_records
    import sys
    sys.exit()
    import ipdb; ipdb.set_trace()

    # 2. Sync the records with the remote server
    synchronize(certificate_records,
                kinto_options={'server': args.kinto_server,
                               'auth': tuple(args.auth.split(':')),
                               'bucket': args.bucket,
                               'collection': args.certificate_collection,
                               'permissions': collection_permissions})

    # # Import GFX drivers

    # # Import addons

    # # Import plugins

    # collections = {'certificates': {'fields': cert_items_fields,
    #                                 'filename': args.xml_file,
    #                                 'xpath': 'certItems/*',
    #                                 'bucket_name': bucket_name,
    #                                 'collection_name': collection_name},
    #                'gfx': {'fields': gfx_items_fields,
    #                        'filename': args.xml_file,
    #                        'xpath': 'gfxItems/*',
    #                        'bucket_name': bucket_name,
    #                        'collection_name': 'gfx'}}

    # synchronize(collections,
    #             kinto_options={'server': args.kinto_server,
    #                            'auth': tuple(args.auth.split(':')),
    #                            'permissions': collection_permissions})


if __name__ == '__main__':  # pragma: nocover
    main()
