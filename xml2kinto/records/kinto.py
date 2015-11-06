from kinto_client import Client

from .base import Records
from .id_generator import create_id


class KintoRecords(Records):
    def _load(self):
        self.client = Client(server_url=self.options['server'],
                             auth=self.options['auth'],
                             bucket=self.options['bucket_name'],
                             collection=self.options['collection_name'])

        # Create bucket
        self.client.create_bucket()
        self.client.create_collection(self.options['collection_name'],
                                      permissions=self.options['permissions'])

        return [self._kinto2rec(rec) for rec in
                self.client.get_records()]

    def _kinto2rec(self, record):
        return record.data

    def delete(self, data):
        self.client.delete_record(data['id'])

    def create(self, data):
        if 'id' not in data:
            data['id'] = create_id(data)
        rec = self.client.create_record(data)
        return rec
