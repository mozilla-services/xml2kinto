import os
import argparse

from kinto_client import Client
from xml2kinto.synchronize import get_diff, synchronize
from xml2kinto.records.kinto import get_kinto_records
from xml2kinto.records.xml import get_xml_records

# options to move to a config file
xml_file = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        '..', 'blocklist.xml'))
auth = ('mark', 'p4ssw0rd')
collection_permissions = {'read': ["system.Everyone"]}
cert_bucket = u'blocklists'
cert_collection = u'certificates'
gfx_bucket = u'blocklists'
gfx_collection = u'gfx'
addon_bucket = u'blocklists'
addon_collection = u'addons'
plugin_bucket = u'blocklists'
plugin_collection = u'plugins'
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
    ("match[@name='name']/exp", {'name': 'matchName'}),
    ("match[@name='description']/exp", {'name': 'matchDescription'}),
    ("match[@name='filename']/exp", {'name': 'matchFilename'}),
    'infoURL',
    ('versionRange', {
        'xpath': 'versionRange',
        'fields': (
            'minVersion',
            'maxVersion',
            'severity',
            ('vulnerabilitystatus', {'name': 'vulnerabilityStatus'}),
            ('targetApplication', {
                'xpath': 'targetApplication',
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

    parser.add_argument('--cert-bucket', help='Bucket name for certificates',
                        type=str, default=cert_bucket)

    parser.add_argument('--cert-collection',
                        help='Collection name for certificates',
                        type=str, default=cert_collection)

    parser.add_argument('--gfx-bucket', help='Bucket name for gfx',
                        type=str, default=gfx_bucket)

    parser.add_argument('--gfx-collection',
                        help='Collection name for gfx',
                        type=str, default=gfx_collection)

    parser.add_argument('--addon-bucket', help='Bucket name for addons',
                        type=str, default=addon_bucket)

    parser.add_argument('--addon-collection',
                        help='Collection name for addon',
                        type=str, default=addon_collection)

    parser.add_argument('--plugin-bucket', help='Bucket name for plugins',
                        type=str, default=plugin_bucket)

    parser.add_argument('--plugin-collection',
                        help='Collection name for plugin',
                        type=str, default=plugin_collection)

    parser.add_argument('-x', '--xml-file', help='XML Source file',
                        type=str, default=xml_file)

    parser.add_argument('-a', '--auth', help='BasicAuth user:pass',
                        type=str, default=':'.join(auth))

    args = parser.parse_args(args=args)

    kinto_client = Client(
        server_url=args.kinto_server, auth=tuple(args.auth.split(':')))

    # Import certificates
    certificate_xml_records = get_xml_records(
        fields=cert_items_fields,
        filename=args.xml_file,
        xpath='certItems/*')
    certificate_kinto_records = get_kinto_records(
        fields=cert_items_fields, kinto_client=kinto_client,
        bucket=args.cert_bucket, collection=args.cert_collection)

    diff = get_diff(certificate_xml_records, certificate_kinto_records)
    synchronize(
        diff, kinto_client, bucket=args.cert_bucket,
        collection=args.cert_collection, permissions=collection_permissions)

    # Import GFX drivers
    gfx_records = get_records(
        fields=gfx_items_fields,
        filename=args.xml_file,
        xpath='gfxItems/*')

    synchronize(gfx_records,
                gfx_items_fields,
                server=args.kinto_server,
                auth=tuple(args.auth.split(':')),
                bucket=args.gfx_bucket,
                collection=args.gfx_collection,
                permissions=collection_permissions)

    # Import addons
    addons_records = get_records(
        fields=addons_items_fields,
        filename=args.xml_file,
        xpath='emItems/*')

    synchronize(addons_records,
                server=args.kinto_server,
                auth=tuple(args.auth.split(':')),
                bucket=args.addon_bucket,
                collection=args.addon_collection,
                permissions=collection_permissions)

    # Import plugins
    plugins_records = get_records(
        fields=plugins_items_fields,
        filename=args.xml_file,
        xpath='pluginItems/*')

    synchronize(plugins_records,
                server=args.kinto_server,
                auth=tuple(args.auth.split(':')),
                bucket=args.plugin_bucket,
                collection=args.plugin_collection,
                permissions=collection_permissions)


if __name__ == '__main__':  # pragma: nocover
    main()
