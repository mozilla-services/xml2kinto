import hashlib
import os
import uuid
import xml.etree.ElementTree as ET

from kintoclient import Bucket
from kintoclient.exceptions import KintoException


# options to move to a config file
xml_file = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        'blocklist.xml'))
user = 'mark'
collection_permissions = {'read': ["system.Everyone"]}
bucket_name = u'onecrl'
collection_name = u'blocklist'
kinto_server = 'http://localhost:8888/v1'
fields = ('subject', 'publicKeyHash', 'serialNumber', 'issuerName')


def SynchronizationError(Exception):
    pass


def create_id(data):
    hash = hashlib.md5()
    data = list(data.items())
    data.sort()
    for __, value in data:
        hash.update(value.encode('utf-8'))
    return str(uuid.UUID(hash.hexdigest()))


class Records(object):
    def __init__(self, options=None):
        if options is None:
            self.options = {}
        else:
            self.options = options
        self.records = self._load()

    def _load(self):
        raise NotImplementedError()

    def find(self, id):
        for rec in self.records:
            if rec['id'] == id:
                return rec


class KintoRecords(Records):
    def _load(self):
        self.bucket = Bucket(bucket_name, server_url=kinto_server,
                             auth=(user, 'p4ssw0rd'), create=True)

        colls = self.bucket.list_collections()
        if collection_name not in colls:
            self.bucket.create_collection(collection_name,
                                          permissions=collection_permissions)

        self.collection = self.bucket.get_collection(collection_name)
        return [self._kinto2rec(rec) for rec in
                self.collection.get_records()]

    def _kinto2rec(self, data):
        rec = {}
        for key in fields:
            rec[key] = data.data.get(key)
        rec['id'] = str(data.id)
        return rec

    def delete(self, data):
        self.collection.delete_record(data['id'])

    def create(self, data):
        if 'id' not in data:
            data['id'] = create_id(data)
        rec = self.collection.create_record(data)
        return rec


class XMLRecords(Records):
    def _load(self):
        self.filename = self.options['filename']
        self.url = '{http://www.mozilla.org/2006/addons-blocklist}'
        self.tree = ET.parse(self.filename)
        self.root = self.tree.getroot()
        return [self._xml2rec(rec) for rec in
                self.root.iterfind('%scertItems/*' % self.url)]

    def _xml2rec(self, data):
        rec = {}

        # grabbing child nodes
        for child in data.getchildren():
            field_name = child.tag
            if field_name.startswith(self.url):
                field_name = field_name[len(self.url):]
            if field_name in fields:
                rec[field_name] = child.text

        # grabbing attributes
        for key in data.keys():
            if key in fields:
                rec[key] = data.get(key)

        if 'id' not in data:
            rec['id'] = create_id(rec)
        return rec


def same_record(one, two):
    for key in fields:
        if one.get(key) != two.get(key):
            return False
    return True


def synchronize():
    print('Working on %r' % kinto_server)
    print('Reading data from %r' % xml_file)
    xml = XMLRecords(options={'filename': xml_file})
    kinto = KintoRecords()
    to_delete = []
    to_update = []
    to_create = []

    # looking at kinto to list records
    # to delete or to update
    for record in kinto.records:
        xml_rec = xml.find(record['id'])
        if xml_rec is None:
            to_delete.append(record)
        else:
            if not same_record(xml_rec, record):
                to_update.append(xml_rec)

    # new records ?
    for record in xml.records:
        kinto_rec = kinto.find(record['id'])
        if not kinto_rec:
            to_create.append(record)

    print('- %d records to create.' % len(to_create))
    print('- %d records to delete.' % len(to_delete))
    print('- %d records to update.' % len(to_update))

    for record in to_delete:
        try:
            kinto.delete(record)
        except KintoException as e:
            raise SynchronizationError(e.response.content)

    for record in to_create + to_update:
        try:
            kinto.create(record)
        except KintoException as e:
            raise SynchronizationError(e.response.content)

    print('Done!')


if __name__ == '__main__':
    synchronize()
