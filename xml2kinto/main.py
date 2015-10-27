import os
import hashlib
import uuid

import xml.etree.ElementTree as ET
from kinto_client import Bucket
from kinto_client.exceptions import KintoException


def create_id(cert):
    # XXX will do better later
    hash = hashlib.md5()
    for value in cert.values():
        hash.update(str(value))
    return str(uuid.UUID(hash.hexdigest()))


DATAFILE = os.path.join(os.path.dirname(__file__), 'blocklist.xml')
URL = '{http://www.mozilla.org/2006/addons-blocklist}'
tree = ET.parse(DATAFILE)
root = tree.getroot()

bucket = Bucket('default', server_url='http://localhost:8888/v1',
                auth=('tarek', 'p4ssw0rd'))

crl_collection = bucket.get_collection('onecrl')


for item in root.iterfind('%scertItems/*' % URL):
    cert = {}
    for key in ('subject', 'publicKeyHash', 'serialNumber', 'issuerName'):
        cert[key] = item.get(key)

    cert['id'] = create_id(cert)

    # can I save it at once and do a single query to kinto?
    try:
        record = crl_collection.create_record(cert)
        record.save()
    except KintoException as e:
        raise Exception(e.response.content)
