import codecs
import json
import os

from kinto_client import cli_utils
from xml2kinto.kinto import get_kinto_records
from xml2kinto.logger import logger
from xml2kinto.scrap import scrap_details_from_amo
from xml2kinto.synchronize import get_diff, push_changes
from xml2kinto.xml import get_xml_records

# options to move to a config file
XML_FILE = os.path.abspath(os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    'blocklist.xml'))

SCHEMA_FILE = os.path.abspath(os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    'schemas.json'))

AUTH = ('mark', 'p4ssw0rd')
COLLECTION_PERMISSIONS = {'read': ["system.Everyone"]}
CERT_BUCKET = u'blocklists'
CERT_COLLECTION = u'certificates'
GFX_BUCKET = u'blocklists'
GFX_COLLECTION = u'gfx'
ADDONS_BUCKET = u'blocklists'
ADDONS_COLLECTION = u'add-ons'
PLUGINS_BUCKET = u'blocklists'
PLUGINS_COLLECTION = u'plugins'
KINTO_SERVER = 'http://localhost:8888/v1'

CERT_ITEMS_FIELDS = ('serialNumber', 'issuerName')
GFX_ITEMS_FIELDS = ('blockID', 'os', 'vendor', 'feature', 'featureStatus',
                    'driverVersion', 'driverVersionMax',
                    'driverVersionComparator',
                    ('devices', {'xpath': 'devices/*'}))


ADDONS_ITEMS_FIELDS = (
    'blockID', 'os',
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


def sync_records(fields, filename, xpath, kinto_client, bucket, collection,
                 schema=None, with_scrapping=False, force_signature=True):
    xml_records = get_xml_records(
        fields=fields,
        filename=filename,
        xpath=xpath)
    kinto_records = get_kinto_records(
        kinto_client=kinto_client,
        bucket=bucket,
        collection=collection,
        schema=schema,
        permissions=COLLECTION_PERMISSIONS)

    to_create, to_delete = get_diff(xml_records, kinto_records)

    if with_scrapping:
        to_create = scrap_details_from_amo(to_create)

    push_changes((to_create, to_delete), kinto_client,
                 bucket=bucket, collection=collection,
                 to_be_signed=force_signature)


def main(args=None):
    parser = cli_utils.add_parser_options(
        description='Syncs a Kinto DB',
        default_collection=None,
        default_bucket=None,
        default_server=KINTO_SERVER,
        default_auth=AUTH,
        include_bucket=False,
        include_collection=False)

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

    parser.add_argument('-S', '--schema-file', help='JSON Schemas file',
                        type=str, default=SCHEMA_FILE)

    parser.add_argument('--no-schema', help='Should we handle schemas',
                        action="store_true")

    parser.add_argument('--with-scrapping', action="store_true",
                        help='Activate blocklist scrapping on AMO')

    parser.add_argument('-C', '--certificates',
                        help='Only import certificates',
                        action='store_true')

    parser.add_argument('-G', '--gfx', help='Only import GFX drivers',
                        action='store_true')

    parser.add_argument('-A', '--addons', help='Only import addons',
                        action='store_true')

    parser.add_argument('-P', '--plugins', help='Only import plugins',
                        action='store_true')

    args = parser.parse_args(args=args)
    # If none of the different "collections" were passed as parameter, then we
    # want to import them all.
    import_all = not any([
        args.certificates,
        args.gfx,
        args.addons,
        args.plugins])

    cli_utils.setup_logger(logger, args)

    kinto_client = cli_utils.create_client_from_args(args)

    # Load the schemas
    schemas = {}
    if not args.no_schema:
        with codecs.open(args.schema_file, 'r', encoding='utf-8') as f:
            schemas = json.load(f)

    # Import certificates
    collections = {
        # Certificates
        'certificates': dict(
            fields=CERT_ITEMS_FIELDS,
            filename=args.xml_file,
            xpath='certItems/*',
            kinto_client=kinto_client,
            bucket=args.cert_bucket,
            collection=args.cert_collection,
            schema=schemas.get(args.cert_collection,
                               schemas.get(CERT_COLLECTION))),
        # GFX drivers
        'gfx': dict(
            fields=GFX_ITEMS_FIELDS,
            filename=args.xml_file,
            xpath='gfxItems/*',
            kinto_client=kinto_client,
            bucket=args.gfx_bucket,
            collection=args.gfx_collection,
            schema=schemas.get(args.gfx_collection,
                               schemas.get(GFX_COLLECTION))),
        # Addons
        'addons': dict(
            fields=ADDONS_ITEMS_FIELDS,
            filename=args.xml_file,
            xpath='emItems/*',
            kinto_client=kinto_client,
            bucket=args.addons_bucket,
            collection=args.addons_collection,
            schema=schemas.get(args.addons_collection,
                               schemas.get(ADDONS_COLLECTION)),
            with_scrapping=args.with_scrapping),
        # Plugins
        'plugins': dict(
            fields=PLUGINS_ITEMS_FIELDS,
            filename=args.xml_file,
            xpath='pluginItems/*',
            kinto_client=kinto_client,
            bucket=args.plugins_bucket,
            collection=args.plugins_collection,
            schema=schemas.get(args.plugins_collection,
                               schemas.get(PLUGINS_COLLECTION)),
            with_scrapping=args.with_scrapping)}

    for collection_type, collection in collections.items():
        if getattr(args, collection_type) or import_all:
            sync_records(**collection)


if __name__ == '__main__':  # pragma: nocover
    main()
