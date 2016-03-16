from datetime import datetime
import grequests

from copy import deepcopy
from pyquery import PyQuery
from xml2kinto.logger import logger

BLOCKLIST_DETAIL_URL = "https://addons.mozilla.org/en-us/firefox/blocked/{}"
THROTTLE = 10


def scrap_details_from_amo(records):
    records_to_scrap = {}

    for record in records:
        # Do not scrap record without blockID parameter
        if 'blockID' not in record:
            continue

        url = BLOCKLIST_DETAIL_URL.format(record['blockID'])
        records_to_scrap[url] = deepcopy(record)

    nb_to_fetch = len(records_to_scrap)
    # Scrap all plugin pages
    if nb_to_fetch:
        logger.info('Ask for {} block item details'.format(nb_to_fetch))
        rs = (grequests.get(u) for u in records_to_scrap.keys())
        scrapped = grequests.map(rs, size=THROTTLE,
                                 exception_handler=log_error)

        logger.info('{} block item details retrieved'.format(nb_to_fetch))

        # Add the information fetch from the blocklist detail to each
        # record and add update the list of records to create.
        records = [
            fill_record_info(record=records_to_scrap[response.url],
                             html=response.text) for response in scrapped]
    return records


def fill_record_info(record, html):
    logger.info('Parse AMO record blocklist info for record: {}'.format(
        record['id']))

    doc = PyQuery(html)
    name = doc('h1>b').html()
    bug = doc('footer>a').attr('href')
    created_date = doc('footer').text().split('on ')[1].split('.')[0]
    created_date = datetime.strptime(created_date, '%B %d, %Y')
    created_date = created_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    info = doc('.blocked dl>dd')

    if len(info) > 0:
        record['details'] = {
            'name': name,
            'bug': bug,
            'why': info.eq(0).html(),
            'who': info.eq(1).html(),
            'created': created_date
        }

    return record


def log_error(req, exc):
    logger.error(exc)
