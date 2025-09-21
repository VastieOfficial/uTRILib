import asyncio
import json
import os
import random
import traceback

import aiofiles
import aiohttp
import crawleruseragents

trackIDs = set()
if not os.path.exists("prefetch"):
    os.mkdir("prefetch")

with open('backup.json') as f:
    res = json.loads(f.read())

for x in res['playlists'].values():
    for t in x['tracks']:
        trackIDs.add(t['id'])
for t in res['saved']:
    trackIDs.add(t['id'])

[trackIDs.remove(x.replace('.json', '')) for x in os.listdir('prefetch') if x.replace('.json','') in trackIDs]

async def parse_covers():
    async with aiohttp.ClientSession() as s:
        for x in os.listdir('prefetch'):
            path = os.path.join('prefetch', x)
            imgpath = path.replace('.json', '.jpg')
            if os.path.exists(imgpath):
                continue
            print(imgpath)
            async with aiofiles.open(path) as f:
                r = json.loads(await f.read())
                try:
                    async with s.get(sorted(r['visualIdentity']['image'], key=lambda d: d['maxHeight']*d['maxWidth'])[-1]['url'], ssl=False) as rr:
                        async with aiofiles.open(imgpath, 'wb+') as f2:
                            await f2.write(await rr.read())
                            print(f"Done DL cover for {x}")
                except Exception:
                    traceback.print_exc()
                    print(f"Failed to DL cover for {x}")

print(len(trackIDs))

async def parse():
    async with aiohttp.ClientSession() as s:
        await parse_covers() # if we were interrupted
        for x in trackIDs:
            if not x:
                continue
            path = os.path.join('prefetch', x)+".json"
            async with s.get(f'https://open.spotify.com/embed/track/{x}', ssl=False) as r:
                try:
                    data = (await r.text()).split('<script id="__NEXT_DATA__" type="application/json">')[1].split('</script>')[0]
                    data = json.loads(data)['props']['pageProps']['state']['data']['entity']
                    album = "N/A"
                    try:
                        usera = random.choice(random.choice(crawleruseragents.CRAWLER_USER_AGENTS_DATA)['instances']) # for some reason, if we're unauthorized we are sometimes not welcome to all data, but using crawler's user agent (or almost any non-browser user agent works)
                        async with s.get(f'https://open.spotify.com/track/{x}', ssl=False, headers={"User-Agent": usera}) as r:
                            async with s.get((await r.text()).split('<meta name="music:album" content="')[1].split('"')[0], ssl=False, headers={"User-Agent": usera}) as rr:
                                album = json.loads((await rr.text()).split('<script type="application/ld+json">')[1].split('</script>')[0])['name']
                        print(f"Got album name from extended data: {album}")
                    except Exception:
                        print("Failed to load extended data (album)")
                        traceback.print_exc()
                    data['album'] = album
                    async with aiofiles.open(path, 'w+') as f:
                        await f.write(json.dumps(data))
                    print(f"Done {data['name']}")
                except:
                    print(f"Failed https://open.spotify.com/track/{x}")

    await parse_covers()
asyncio.run(parse())