from __future__ import absolute_import
from xml.etree import ElementTree

from .base import Records
from .id_generator import create_id

XML_NAMESPACE = '{http://www.mozilla.org/2006/addons-blocklist}'
SUPPORTED_OPTIONS = ['name', 'xpath', 'fields']


def get_info(fields, data):
    rec = {}

    # grabbing sub-elements
    for field in fields:
        name = field
        if isinstance(field, tuple):
            field, options = field
            name = field

            for option in options:
                if option not in SUPPORTED_OPTIONS:
                    raise NotImplementedError(options)

            if 'name' in options:
                name = options['name']

            if 'xpath' in options:
                if 'fields' in options:
                    # Use the current node to get the list of matching
                    # xpath childrens
                    # eg:
                    #
                    # ('targetApplication', {
                    #     'xpath': 'targetApplication',
                    #     'fields': (
                    #         ('id', {'name': 'guid'}),
                    #         'minVersion',
                    #         'maxVersion',
                    #     )
                    # })
                    subrecords = data.iterfind(
                        '%s%s' % (XML_NAMESPACE, options['xpath']))
                    rec[name] = [get_info(options['fields'], r)
                                 for r in subrecords]
                else:
                    # Handle the case when we return a list
                    # ('prefs', {'xpath': 'prefs/*'}),
                    rec[name] = [item.text for item in data.findall(
                        XML_NAMESPACE + options['xpath'])]

            # If the xpath has been handled for this field we don't
            # need to look for attributes and nodes.
            continue

        # grabbing child nodes
        for child in data.getchildren():
            field_name = child.tag
            if field_name.startswith(XML_NAMESPACE):
                field_name = field_name[len(XML_NAMESPACE):]
            if field_name == field:
                rec[name] = child.text

        # grabbing attributes
        for key in data.keys():
            if key == field:
                rec[key] = data.get(key)

    if 'id' not in data:
        rec['id'] = create_id(rec)

    return rec


def get_certificate_records(fields, filename, xpath='certItems/*'):
    tree = ElementTree.parse(filename)
    root = tree.getroot()
    records = root.iterfind('%s%s' % (XML_NAMESPACE, xpath))
    return [get_info(fields, rec) for rec in records]


def get_gfx_records(fields, filename, xpath='gfxItems/*'):
    tree = ElementTree.parse(filename)
    root = tree.getroot()
    records = root.iterfind('%s%s' % (XML_NAMESPACE, xpath))
    return [get_info(fields, rec) for rec in records]


def get_addons_records(fields, filename, xpath='emItems/*'):
    tree = ElementTree.parse(filename)
    root = tree.getroot()
    records = root.iterfind('%s%s' % (XML_NAMESPACE, xpath))
    return [get_info(fields, rec) for rec in records]


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
