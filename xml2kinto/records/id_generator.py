import hashlib
import uuid
from six import text_type


def create_id(data):
    hash = hashlib.md5()
    data = list(data.items())
    data.sort()
    for __, value in data:
        if isinstance(value, list):
            for item in value:
                hash.update(item.encode('utf-8'))
        else:
            hash.update(value.encode('utf-8'))
    return text_type(uuid.UUID(hash.hexdigest()))
