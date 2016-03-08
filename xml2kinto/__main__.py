import os
import argparse

from kinto_client import Client
from xml2kinto.kinto import get_kinto_records
from xml2kinto.synchronize import get_diff, push_changes
from xml2kinto.xml import get_xml_records

# options to move to a config file
XML_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        '..', 'blocklist.xml'))
AUTH = ('mark', 'p4ssw0rd')
COLLECTION_PERMISSIONS = {'read': ["system.Everyone"]}
CERT_BUCKET = u'blocklists'
CERT_COLLECTION = u'certificates'
GFX_BUCKET = u'blocklists'
GFX_COLLECTION = u'gfx'
ADDONS_BUCKET = u'blocklists'
ADDONS_COLLECTION = u'addons'
PLUGINS_BUCKET = u'blocklists'
PLUGINS_COLLECTION = u'plugins'
KINTO_SERVER = 'http://localhost:8888/v1'

CERT_ITEMS_FIELDS = ('serialNumber', 'issuerName')
GFX_ITEMS_FIELDS = ('blockID', 'os', 'vendor', 'feature', 'featureStatus',
                    'driverVersion', 'driverVersionComparator',
                    ('devices', {'xpath': 'devices/*'}))

ADDONS_ITEMS_FIELDS = (
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

PLUGINS_ITEMS_FIELDS = (
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


def sync_records(fields, filename, xpath, kinto_client, bucket, collection):
    xml_records = get_xml_records(
        fields=fields,
        filename=filename,
        xpath=xpath)
    kinto_records = get_kinto_records(
        kinto_client=kinto_client,
        bucket=bucket,
        collection=collection,
        permissions=COLLECTION_PERMISSIONS)

    diff = get_diff(xml_records, kinto_records)
    push_changes(diff, kinto_client,
                 bucket=bucket, collection=collection)


def main(args=None):
    parser = argparse.ArgumentParser(description='Syncs a Kinto DB.')

    parser.add_argument('-s', '--kinto-server', help='Kinto Server',
                        type=str, default=KINTO_SERVER)

    parser.add_argument('--cert-bucket', help='Bucket name for certificates',
                        type=str, default=CERT_BUCKET)

    parser.add_argument('--cert-collection',
                        help='Collection name for certificates',
                        type=str, default=CERT_COLLECTION)

    parser.add_argument('--gfx-bucket', help='Bucket name for gfx',
                        type=str, default=GFX_BUCKET)

    parser.add_argument('--gfx-collection',
                        help='Collection name for gfx',
                        type=str, default=GFX_COLLECTION)

    parser.add_argument('--addons-bucket', help='Bucket name for addons',
                        type=str, default=ADDONS_BUCKET)

    parser.add_argument('--addons-collection',
                        help='Collection name for addon',
                        type=str, default=ADDONS_COLLECTION)

    parser.add_argument('--plugins-bucket', help='Bucket name for plugins',
                        type=str, default=PLUGINS_BUCKET)

    parser.add_argument('--plugins-collection',
                        help='Collection name for plugin',
                        type=str, default=PLUGINS_COLLECTION)

    parser.add_argument('-x', '--xml-file', help='XML Source file',
                        type=str, default=XML_FILE)

    parser.add_argument('-a', '--auth', help='BasicAuth user:pass',
                        type=str, default=':'.join(AUTH))

    args = parser.parse_args(args=args)

    kinto_client = Client(
        server_url=args.kinto_server, auth=tuple(args.auth.split(':')))

    # Import certificates
    collections = [
        # Certificates
        dict(fields=CERT_ITEMS_FIELDS,
             filename=args.xml_file,
             xpath='certItems/*',
             kinto_client=kinto_client,
             bucket=args.cert_bucket,
             collection=args.cert_collection),
        # GFX drivers
        dict(fields=GFX_ITEMS_FIELDS,
             filename=args.xml_file,
             xpath='gfxItems/*',
             kinto_client=kinto_client,
             bucket=args.gfx_bucket,
             collection=args.gfx_collection),
        # Addons
        dict(fields=ADDONS_ITEMS_FIELDS,
             filename=args.xml_file,
             xpath='emItems/*',
             kinto_client=kinto_client,
             bucket=args.addons_bucket,
             collection=args.addons_collection),
        # Plugins
        dict(fields=PLUGINS_ITEMS_FIELDS,
             filename=args.xml_file,
             xpath='pluginItems/*',
             kinto_client=kinto_client,
             bucket=args.plugins_bucket,
             collection=args.plugins_collection)]

    for collection in collections:
        sync_records(**collection)


if __name__ == '__main__':  # pragma: nocover
    main()
