import os
from xml2kinto.synchronize import synchronize

# options to move to a config file
xml_file = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        '..', 'blocklist.xml'))
auth = ('mark', 'p4ssw0rd')
collection_permissions = {'read': ["system.Everyone"]}
bucket_name = u'onecrl'
collection_name = u'blocklist'
kinto_server = 'http://localhost:8888/v1'
fields = ('subject', 'publicKeyHash', 'serialNumber', 'issuerName')


def main():
    synchronize(fields,
                xml_options={'filename': xml_file},
                kinto_options={
                    'server': kinto_server,
                    'bucket_name': bucket_name,
                    'collection_name': collection_name,
                    'auth': auth,
                    'permissions': collection_permissions
                })


if __name__ == '__main__':
    main()
