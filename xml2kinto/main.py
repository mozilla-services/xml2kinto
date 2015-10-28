import os
import hashlib
import uuid

import xml.etree.ElementTree as ET
from kinto_client import Bucket
from kinto_client.exceptions import KintoException


# options to move to a config file
xml_file = os.path.join(os.path.dirname(__file__), 'blocklist.xml')
user = 'mark'
permissions = {'read': ["system.Everyone"]}
bucket_name = u'onecrl'
collection_name = u'blocklist'
kinto_server = 'http://localhost:8888/v1'
fields = ('subject', 'publicKeyHash', 'serialNumber', 'issuerName')


def create_id(data):
    hash = hashlib.md5()
    data = data.items()
    data.sort()
    for __, value in data:
        hash.update(str(value))
    return str(uuid.UUID(hash.hexdigest()))


class KintoRecords(object):
    def __init__(self):
        self.bucket = Bucket(bucket_name, server_url=kinto_server,
                             auth=(user, 'p4ssw0rd'), create=True,
                             permissions=permissions)
        colls = self.bucket.list_collections()

        if collection_name not in colls:
            self.bucket.create_collection(collection_name)
        self.collection = self.bucket.get_collection(collection_name)
        self.records = [self._kinto2rec(rec) for rec in
                        self.collection.get_records()]

    def _kinto2rec(self, data):
        rec = {}
        for key in fields:
            rec[key] = data.data.get(key)
        rec['id'] = str(data.id)
        return rec

    def delete_record(self, data):
        self.collection.delete_record(data['id'])

    def create_record(self, data):
        if 'id' not in data:
            data['id'] = create_id(data)
        rec = self.collection.create_record(data)
        rec.save()   # XXX
        return rec

    def find(self, id):
        for rec in self.records:
            if rec['id'] == id:
                return rec


class XMLRecords(object):
    def __init__(self, filename):
        self.filename = filename
        self.url = '{http://www.mozilla.org/2006/addons-blocklist}'
        self.tree = ET.parse(self.filename)
        self.root = self.tree.getroot()
        self.records = [self._xml2rec(rec) for rec in
                        self.root.iterfind('%scertItems/*' % self.url)]

    def _xml2rec(self, data):
        rec = {}
        for key in fields:
            rec[key] = data.get(key)
        if 'id' not in data:
            rec['id'] = create_id(data)
        return rec

    def find(self, id):
        for rec in self.records:
            if rec['id'] == id:
                return rec


def same_record(one, two):
    for key in fields:
        if one[key] != two[key]:
            return False
    return True


def synchronize():
    xml = XMLRecords(xml_file)
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

    print('%d records to create.' % len(to_create))
    print('%d records to delete.' % len(to_delete))
    print('%d records to update.' % len(to_update))

    for record in to_delete:
        try:
            kinto.delete_record(record)
        except KintoException as e:
            raise Exception(e.response.content)

    for record in to_create + to_update:
        try:
            kinto.create_record(record)
        except KintoException as e:
            raise Exception(e.response.content)

    print('Done!')


if __name__ == '__main__':
    synchronize()
