import mock
import os

from xml2kinto.scrap import (
    BLOCKLIST_DETAIL_URL, scrap_details_from_amo, log_error)


def test_scrap_details_from_amo():
    record = {'id': '123', 'blockID': 'foobar'}

    with open(os.path.join(os.path.dirname(__file__),
                           'blocked_item_detail_page.html')) as html_file:
        html = html_file.read()

    with mock.patch('grequests.map') as grequests_mock:
        response = mock.MagicMock()
        response.url = BLOCKLIST_DETAIL_URL.format('foobar')
        response.text = html
        grequests_mock.return_value = [response]

        records = scrap_details_from_amo([record])

    expected_record = {
        'id': '123',
        'blockID': 'foobar',
        'why': 'This add-on is believed to be silently installed in Firefox, '
               'in violation of the <a href="https://developer.mozilla.org/'
               'en-US/Add-ons/Add-on_guidelines">Add-on Guidelines</a>.',
        'who': 'All Firefox users who have this add-on installed. Users who '
               'wish\n to continue using this add-on can enable it in the '
               'Add-ons Manager.'}

    assert records == [expected_record]
    assert record != expected_record


def test_scrap_detail_should_not_scrap_records_with_missing_blockID():
    with mock.patch('grequests.map') as grequests_mock:
        records = scrap_details_from_amo([{"id": "foo"}])
        assert grequests_mock.call_count == 0
        assert records == [{"id": "foo"}]


def test_log_error_write_into_the_logger():
    with mock.patch('xml2kinto.scrap.logger') as logger:
        log_error(mock.sentinel.req, mock.sentinel.exception)
        logger.error.assert_called_with(mock.sentinel.exception)
