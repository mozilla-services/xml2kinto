from xml.etree import ElementTree

from .base import Records
from .id_generator import create_id


class XMLRecords(Records):
    def _load(self):
        self.filename = self.options['filename']
        self.url = '{http://www.mozilla.org/2006/addons-blocklist}'
        self.tree = ElementTree.parse(self.filename)
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
            if field_name in self.fields:
                rec[field_name] = child.text

        # grabbing attributes
        for key in data.keys():
            if key in self.fields:
                rec[key] = data.get(key)

        if 'id' not in data:
            rec['id'] = create_id(rec)
        return rec
