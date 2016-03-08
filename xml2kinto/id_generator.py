import hashlib
import json
import uuid
from six import text_type


def create_id(data):
    serialized = json.dumps(data, sort_keys=True, separators=(',', ':'))
    hashed = hashlib.md5(serialized.encode('utf-8'))
    return text_type(uuid.UUID(hashed.hexdigest()))
