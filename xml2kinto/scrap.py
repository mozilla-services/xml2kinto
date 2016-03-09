from pyquery import PyQuery as pyquery


async def fetch_record_info(session, record):
    if 'blockID' not in record:
        print("{} doesn't have a blockID".format(record['id']))
        return

    # 2. Pour chaque record, calculer l'url de blocklists
    url = "https://addons.mozilla.org/fr/firefox/blocked/{}".format(
        record['blockID'])

    async with session.get(url) as resp:
        if resp.status != 200:
            body = await resp.text()
            raise ValueError('{} — {}'.format(resp.status, body))

        print("Scrapped {}".format(record['blockID']))

        data = await resp.text()

    doc = pyquery(data)
    # 5. Modifier les records avec les infos
    # Find out informations
    record['why'] = doc('.blocked dl>dd').eq(0).html()
    record['who'] = doc('.blocked dl>dd').eq(1).html()

    return record
