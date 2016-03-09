import os

import mock

from xml2kinto.scrap import fetch_record_info


def test_fetch_record_info():
    with open(os.path.join(os.path.dirname(__file__),
                           'blocked_item_detail_page.html')) as html_file:
        html = html_file.read()
    response = mock.MagicMock()
    response.text = html
    session = mock.MagicMock()
    session.get.return_value = response
    res = fetch_record_info(session, {'id': '123', 'blockID': 'foobar'})
    assert res == {
        'id': '123',
        'blockID': 'foobar',
        'why': 'This add-on is believed to be silently installed in Firefox, '
               'in violation of the <a href="https://developer.mozilla.org/'
               'en-US/Add-ons/Add-on_guidelines">Add-on Guidelines</a>.',
        'who': 'All Firefox users who have this add-on installed. Users who '
               'wish\n to continue using this add-on can enable it in the '
               'Add-ons Manager.'}
