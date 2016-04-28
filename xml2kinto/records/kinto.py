from kinto_client import Client
from kinto_client.exceptions import KintoException, BucketNotFound

from .base import Records
from .id_generator import create_id


class KintoRecords(Records):
    def _load(self):
        collection = self.options['collection_name']
        bucket = self.options['bucket_name']

        self.client = Client(server_url=self.options['server'],
                             auth=self.options['auth'],
                             bucket=bucket,
                             collection=collection)

        # Create bucket
        try:
            self.client.get_bucket(bucket)
        except BucketNotFound:
            self.client.create_bucket()

        try:
            self.client.get_collection(collection=collection, bucket=bucket)
        except KintoException:
            self.client.create_collection(collection,
                                          permissions=self.options['permissions'])

        # XXX to be removed later
        # remove the 'onecrl' bucket if it exists
        try:
            self.client.delete_bucket('onecrl')
        except KintoException:
            pass

        return [self._kinto2rec(rec) for rec in
                self.client.get_records()]

    def _kinto2rec(self, record):
        return record

    def delete(self, data):
        self.client.delete_record(data['id'])

    def create(self, data):
        if 'id' not in data:
            data['id'] = create_id(data)
        rec = self.client.create_record(data)
        return rec
