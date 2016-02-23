from __future__ import absolute_import
from xml.etree import ElementTree

from .base import Records
from .id_generator import create_id


class XMLRecords(Records):
    def _load(self):
        self.filename = self.options['filename']
        self.xpath = self.options['xpath']
        self.url = '{http://www.mozilla.org/2006/addons-blocklist}'
        self.tree = ElementTree.parse(self.filename)
        self.root = self.tree.getroot()
        return [self._xml2rec(rec) for rec in
                self.root.iterfind('%s%s' % (self.url, self.xpath))]

    def _xml2rec(self, data):
        rec = {}

        # grabbing sub-elements
        for field in self.fields:
            if not isinstance(field, tuple):
                continue
            name, options = field
            if 'xpath' in options:
                rec[name] = [item.text for item in data.findall(self.url +
                             options['xpath'])]
            else:
                raise NotImplementedError(options)

        # grabbing child nodes (text or attribute)
        for child in data.getchildren():
            field_name = child.tag
            if field_name.startswith(self.url):
                field_name = field_name[len(self.url):]

            if field_name in self.fields:
                rec[field_name] = child.text

            keys = [('%s:%s' % (field_name, key), key) for key in child.keys()]
            for fullkey, key in keys:
                if fullkey in self.fields:
                    rec[key] = child.get(key)

        # grabbing attributes
        for key in data.keys():
            if key in self.fields:
                rec[key] = data.get(key)

        if 'id' not in data:
            rec['id'] = create_id(rec)
        return rec
