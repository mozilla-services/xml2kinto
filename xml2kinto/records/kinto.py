from six import text_type

from kinto_client import Bucket

from .base import Records
from .id_generator import create_id


class KintoRecords(Records):
    def _load(self):
        self.bucket = Bucket(self.options['bucket_name'],
                             server_url=self.options['server'],
                             auth=self.options['auth'], create=True)

        colls = self.bucket.list_collections()
        if self.options['collection_name'] not in colls:
            self.bucket.create_collection(
                self.options['collection_name'],
                permissions=self.options['permissions'])

        self.collection = self.bucket.get_collection(
            self.options['collection_name'])

        return [self._kinto2rec(rec) for rec in
                self.collection.get_records()]

    def _kinto2rec(self, record):
        rec = {}
        for key in self.fields:
            rec[key] = record.data.get(key)
        rec['id'] = text_type(record.id)
        return rec

    def delete(self, data):
        self.collection.delete_record(data['id'])

    def create(self, data):
        if 'id' not in data:
            data['id'] = create_id(data)
        rec = self.collection.create_record(data)
        return rec
