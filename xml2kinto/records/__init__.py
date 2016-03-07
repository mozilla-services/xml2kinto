from .base import Records

__all__ = ('same_record', 'Records')


def same_record(fields, one, two):
    for key in fields:
        if isinstance(key, tuple):
            # XXXimport pdb; pdb.set_trace()
            continue
        if one.get(key) != two.get(key):
            return False
    return True
