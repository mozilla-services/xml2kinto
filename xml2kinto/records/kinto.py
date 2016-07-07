from kinto_client import Client
from kinto_client.exceptions import KintoException, BucketNotFound

from .base import Records
from .id_generator import create_id


# XXX backport of new APIs
class KintoClient(Client):

    def patch_collection(self, data=None, collection=None, bucket=None,
                         permissions=None, safe=True, last_modified=None):
        endpoint = self._get_endpoint('collection', bucket, collection)
        headers = self._get_cache_headers(safe, data, last_modified)
        resp, _ = self.session.request('patch', endpoint, data=data,
                                       permissions=permissions,
                                       headers=headers)
        return resp

    def _get_cache_headers(self, safe, data=None, last_modified=None):
        from kinto_client import utils
        has_data = data is not None and data.get('last_modified')
        if (last_modified is None and has_data):
            last_modified = data['last_modified']
        if safe and last_modified is not None:
            return {'If-Match': utils.quote(last_modified)}


class KintoRecords(Records):
    def _load(self):
        self.collection = collection = self.options['collection_name']
        self.bucket = bucket = self.options['bucket_name']

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
            perms = self.options['permissions']
            self.client.create_collection(collection, permissions=perms)

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

    def ask_for_signing(self):
        data = {"status": "to-sign"}
        self.client.patch_collection(data=data, bucket=self.bucket,
                                     collection=self.collection)
