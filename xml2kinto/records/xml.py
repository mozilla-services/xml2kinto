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

            if '/' in field:  # Eg: 'versionRange/minVersion'
                tag, attr = field.split('/')
                try:
                    node = data.findall('%s%s' % (XML_NAMESPACE, tag))[0]
                except IndexError:  # Didn't find a node for that.
                    continue
                rec[name] = node.get(attr)
                continue  # We got all we need, don't dig further

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
                    #         ......
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
            field_name = child.tag  # eg versionRange
            if field_name.startswith(XML_NAMESPACE):
                field_name = field_name[len(XML_NAMESPACE):]
            if field_name == field:
                # eg <prefs>foo</pref> => rec['prefs'] = 'foo'
                rec[name] = child.text

        # grabbing attributes
        for key in data.keys():
            if key == field:
                # eg <emItem blockID="i24" ...> => rec['blockID'] = 'i24'
                rec[name] = data.get(key)

    return rec


def get_record_from_xml(fields, data):
    rec = get_info(fields, data)
    if 'id' not in rec:
        rec['id'] = create_id(rec)
    return rec


def get_xml_records(fields, filename, xpath):
    tree = ElementTree.parse(filename)
    root = tree.getroot()
    records = root.iterfind('%s%s' % (XML_NAMESPACE, xpath))
    return [get_record_from_xml(fields, rec) for rec in records]
