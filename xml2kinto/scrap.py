from pyquery import PyQuery
from xml2kinto.logger import logger


def fetch_record_info(session, record):
    if 'blockID' not in record:
        print("{} doesn't have a blockID".format(record['id']))
        return

    logger.debug('Ask AMO for record: {}'.format(record['id']))
    # 2. Pour chaque record, calculer l'url de blocklists
    url = "https://addons.mozilla.org/fr/firefox/blocked/{}".format(
        record['blockID'])

    resp = session.get(url)
    resp.raise_for_status()

    logger.info('AMO answered for record: {}'.format(record['id']))

    doc = PyQuery(resp.text)
    # 5. Modifier les records avec les infos
    # Find out informations
    record['why'] = doc('.blocked dl>dd').eq(0).html()
    record['who'] = doc('.blocked dl>dd').eq(1).html()

    return record
