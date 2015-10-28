import os
import hashlib
import uuid

import xml.etree.ElementTree as ET
from kinto_client import Bucket
from kinto_client.exceptions import KintoException


DATAFILE = os.path.join(os.path.dirname(__file__), 'blocklist.xml')
user = 'mark'
permissions = {'read': ["system.Everyone"]}
bucket_name = 'onecrl'
collection_name = 'blocklist'
kinto_server = 'http://localhost:8888/v1'


class KintoRecords(object):
    def __init__(self):
        self.bucket = Bucket(bucket_name, server_url=kinto_server,
                             auth=(user, 'p4ssw0rd'), create=True,
                             permissions=permissions)
        colls = self.bucket.list_collections()

        if collection_name not in colls:
            self.bucket.create_collection(collection_name)
        self.collection = self.bucket.get_collection(collection_name)

    def create_record(self, data):
        if 'id' not in data:
            data['id'] = self._create_id(data)
        rec = self.collection.create_record(data)
        rec.save()   # XXX
        return rec

    def _create_id(self, data):
        hash = hashlib.md5()
        for value in cert.values():
            hash.update(str(value))
        return str(uuid.UUID(hash.hexdigest()))


class XMLRecords(object):
    def __init__(self, filename):
        self.filename = filename
        self.url = '{http://www.mozilla.org/2006/addons-blocklist}'
        self.tree = ET.parse(self.filename)
        self.root = self.tree.getroot()
        self.records = self.root.iterfind('%scertItems/*' % self.url)



xml = XMLRecords(DATAFILE)
kinto = KintoRecords()


for record in xml.records:
    cert = {}
    for key in ('subject', 'publicKeyHash', 'serialNumber', 'issuerName'):
        cert[key] = record.get(key)

    try:
        kinto.create_record(cert)
    except KintoException as e:
        raise Exception(e.response.content)
