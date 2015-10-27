import os
import xml.etree.ElementTree as ET


DATAFILE = os.path.join(os.path.dirname(__file__), 'blocklist.xml')
URL = '{http://www.mozilla.org/2006/addons-blocklist}'
tree = ET.parse(DATAFILE)
root = tree.getroot()

certs = []

for item in root.iterfind('%scertItems/*' % URL):
    cert = {'issuerName': item.get('issuerName'),
            'serialNumber': item.get('serialNumber')}

    certs.append(cert)

print certs

