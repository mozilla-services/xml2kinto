import mock
import os
import pytest

from xml.etree import ElementTree

from xml2kinto import __main__ as main
from xml2kinto.xml import get_record_from_xml, get_record, get_xml_records

XML_TPL = """<?xml version="1.0" encoding="UTF-8"?>
             <blocklist xmlns="http://www.mozilla.org/2006/addons-blocklist"
                        lastupdate="1445462022000">
             {data}
             </blocklist>"""


ADDON_DATA = """
    <emItem blockID="i15" id="personas@christopher.beard">
        <versionRange minVersion="1.6" maxVersion="1.6">
            <targetApplication id="{ec8030f7-c20a-464f-9b0e-13a3a9e97384}">
                <versionRange minVersion="3.6" maxVersion="3.6.*"/>
            </targetApplication>
            <targetApplication id="{some-other-application}">
                <versionRange minVersion="1.2" maxVersion="1.4"/>
            </targetApplication>
        </versionRange>
        <versionRange minVersion="1.5" maxVersion="2.5" severity="1">
        </versionRange>
        <prefs>
            <pref>browser.startup.homepage</pref>
            <pref>browser.search.defaultenginename</pref>
        </prefs>
    </emItem>
"""


def _to_ElementTree(data):
    xml_data = XML_TPL.format(data=data)
    tree = ElementTree.fromstring(xml_data)
    return tree.getchildren()[0]


def test_addon_record():
    xml_node = _to_ElementTree(ADDON_DATA)
    expected = get_record_from_xml(main.ADDONS_ITEMS_FIELDS, xml_node)
    assert expected == {
        'blockID': 'i15',
        'id': '5a5172a7-c130-b45a-104b-dc121960bc91',
        'guid': 'personas@christopher.beard',
        'prefs': ['browser.startup.homepage',
                  'browser.search.defaultenginename'],
        'versionRange': [
            {'minVersion': '1.6',
             'maxVersion': '1.6',
             'targetApplication': [
                 {'guid': '{ec8030f7-c20a-464f-9b0e-13a3a9e97384}',
                  'minVersion': '3.6',
                  'maxVersion': '3.6.*'},
                 {'guid': '{some-other-application}',
                  'minVersion': '1.2',
                  'maxVersion': '1.4'}
                 ]},
            {'minVersion': '1.5',
             'maxVersion': '2.5',
             'targetApplication': [],
             'severity': '1'}]}


PLUGIN_DATA = """
    <pluginItem os="Linux" blockID="p328">
        <match name="filename" exp="Silverlight\.plugin"/>
        <match name="name" exp="some name"/>
        <match name="description" exp="some description"/>
        <infoURL>https://get.adobe.com/flashplayer/</infoURL>
        <versionRange minVersion="5.1" maxVersion="5.2"
                      severity="0" vulnerabilitystatus="1">
            <targetApplication id="{ec8030f7-c20a-464f-9b0e-13a3a9e97384}">
                <versionRange minVersion="19.0a1" maxVersion="*"/>
            </targetApplication>
        </versionRange>
    </pluginItem>
"""


def test_plugin_record():
    xml_node = _to_ElementTree(PLUGIN_DATA)
    expected = get_record_from_xml(main.PLUGINS_ITEMS_FIELDS, xml_node)
    assert expected == {
        'blockID': 'p328',
        'id': 'af9baa03-da4e-5a03-9a2c-9e20ec2d7994',
        'infoURL': 'https://get.adobe.com/flashplayer/',
        'os': 'Linux',
        'matchName': 'some name',
        'matchFilename': 'Silverlight\.plugin',
        'matchDescription': 'some description',
        'versionRange': [
            {'minVersion': '5.1',
             'maxVersion': '5.2',
             'severity': '0',
             'vulnerabilityStatus': '1',
             'targetApplication': [
                 {'guid': '{ec8030f7-c20a-464f-9b0e-13a3a9e97384}',
                  'minVersion': '19.0a1',
                  'maxVersion': '*'}]}]}


GFX_DATA = """
    <gfxBlacklistEntry blockID="g35">
        <os>WINNT 6.1</os>
        <vendor>0x10de</vendor>
        <devices>
            <device>0x0a6c</device>
            <device>0x0a6d</device>
        </devices>
        <feature>DIRECT2D</feature>
        <featureStatus>BLOCKED_DRIVER_VERSION</featureStatus>
        <driverVersion>8.17.12.5896</driverVersion>
        <driverVersionComparator>LESS_THAN_OR_EQUAL</driverVersionComparator>
    </gfxBlacklistEntry>
"""


def test_gfx_record():
    xml_node = _to_ElementTree(GFX_DATA)
    expected = get_record_from_xml(main.GFX_ITEMS_FIELDS, xml_node)
    assert expected == {
        'blockID': 'g35',
        'id': '6da38ca9-31e5-dd0d-b937-d06ffee543b4',
        'os': 'WINNT 6.1',
        'vendor': '0x10de',
        'feature': 'DIRECT2D',
        'featureStatus': 'BLOCKED_DRIVER_VERSION',
        'driverVersion': '8.17.12.5896',
        'driverVersionComparator': 'LESS_THAN_OR_EQUAL',
        'devices': ['0x0a6c', '0x0a6d']}


CERTIFICATE_DATA = """
    <certItem issuerName="MIGQMQswCQYDVQQGEwJHQjEbMBkGA1UECBMSR3JlYXRlciBNYW5jaGVzdGVyMRAwDgYDVQQHEwdTYWxmb3JkMRowGAYDVQQKExFDT01PRE8gQ0EgTGltaXRlZDE2MDQGA1UEAxMtQ09NT0RPIFJTQSBEb21haW4gVmFsaWRhdGlvbiBTZWN1cmUgU2VydmVyIENB">
        <serialNumber>D9UltDPl4XVfSSqQOvdiwQ==</serialNumber>
    </certItem>
"""  # noqa


def test_certificate_record():
    xml_node = _to_ElementTree(CERTIFICATE_DATA)
    expected = get_record_from_xml(main.CERT_ITEMS_FIELDS, xml_node)
    assert expected == {
        'id': '7c8a594f-2d88-4175-75f3-5b7b2d569036',
        'issuerName': 'MIGQMQswCQYDVQQGEwJHQjEbMBkGA1UECBMSR3JlYXRlciBNYW5jaGVzdGVyMRAwDgYDVQQHEwdTYWxmb3JkMRowGAYDVQQKExFDT01PRE8gQ0EgTGltaXRlZDE2MDQGA1UEAxMtQ09NT0RPIFJTQSBEb21haW4gVmFsaWRhdGlvbiBTZWN1cmUgU2VydmVyIENB',  # noqa
        'serialNumber': 'D9UltDPl4XVfSSqQOvdiwQ=='}


def test_get_record_raise_if_an_option_is_not_supported():
    with pytest.raises(NotImplementedError):
        get_record(
            (("id", {"unsupported": "unsupported"}),), mock.sentinel.data)


def test_if_match_name_cannot_be_found():
    plugin_data = """
        <pluginItem os="Linux" blockID="p328">
            <match name="description" exp="some description"/>
            <infoURL>https://get.adobe.com/flashplayer/</infoURL>
            <versionRange minVersion="5.1" maxVersion="5.2"
                          severity="0" vulnerabilitystatus="1">
            </versionRange>
        </pluginItem>
    """

    xml_node = _to_ElementTree(plugin_data)
    expected = get_record_from_xml(main.PLUGINS_ITEMS_FIELDS, xml_node)
    assert expected == {
        'blockID': 'p328',
        'id': '772b9bb5-8eb4-edc1-359e-43d1932c0b47',
        'matchDescription': 'some description',
        'os': 'Linux',
        'infoURL': 'https://get.adobe.com/flashplayer/',
        'versionRange': [
            {'minVersion': '5.1',
             'maxVersion': '5.2',
             'severity': '0',
             'vulnerabilityStatus': '1',
             'targetApplication': []}]}


def test_get_xml_records_can_load_xml_file():
    filename = os.path.join(os.path.dirname(__file__), "test_blocklist.xml")
    records = get_xml_records(fields=main.CERT_ITEMS_FIELDS,
                              filename=filename,
                              xpath='certItems/*')

    assert len(records) == 10
