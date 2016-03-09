# -*- coding: utf-8 -*-
# This is PY3 only code using asyncIO
import asyncio
import aiohttp
import base64
import json
from random import randint
from kinto_client import Client, Endpoints
from pyquery import PyQuery as pyquery

SERVER_URL = 'https://kinto.dev.mozaws.net/v1'
BUCKET = 'blocklists'
COLLECTION = 'addons'
AUTH = ('mark', 'p4ssw0rd')
THROTTLE = 15  # Split request on 15s


async def fetch_info(session, record):
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

    # 6. Pousser les modifications
    url = Endpoints(SERVER_URL).get('record', id=record['id'],
                                    bucket=BUCKET, collection=COLLECTION)

    auth = base64.b64encode(':'.join(AUTH).encode('utf-8')).decode('utf-8')
    headers = {'content-type': 'application/json',
               'Authorization': "Basic {}".format(auth)}
    data = json.dumps({"data": record})

    await asyncio.sleep(randint(0, THROTTLE))

    async with session.put(url, headers=headers, data=data) as resp:
        if resp.status != 200:
            body = await resp.text()
            raise ValueError('{} — {}'.format(resp.status, body))

    print("Updated {}".format(record['id']))


async def scrap_records():
    with aiohttp.ClientSession() as session:
        # 1. Recupèrer tous les records
        url = '{}'.format(Endpoints(SERVER_URL).get(
            'records', bucket=BUCKET, collection=COLLECTION))

        async with session.get(url) as resp:

            # XXX: Handle the Next-Page header
            if resp.status != 200:
                body = await resp.json()
                raise ValueError('{} — {}'.format(response.status, body))

            data = await resp.json()

        records = data['data']
        # 3. Ajouter un fetch_page pour chaque
        coros = [fetch_info(session, record) for record in records]

        # 4. Aller chercher toutes les pages.
        results = await asyncio.gather(*coros)
        print("Done")

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(scrap_records())
