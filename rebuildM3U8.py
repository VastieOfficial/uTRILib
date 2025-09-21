import json
import os
import re
import unicodedata

import requests

from api import get_token

playlistThumbs = os.path.join(os.getcwd(), "playlistThumbs")
if not os.path.exists(playlistThumbs):
    os.mkdir(playlistThumbs)

cache = os.getenv("TRI_CACHE", os.path.join(os.getcwd(), "TRICACHE")) # cache MUST exist
lists = os.path.join(os.getcwd(), "lists") # where the lists'll go

if not os.path.exists(lists):
    os.mkdir(lists)

def slugify(value, allow_unicode=True):
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return value

def getImgUrl(playlistId):
    if playlistId is not None:
        file = os.path.join(playlistThumbs, playlistId+".jpg")
        if not os.path.exists(file):
            with open(file, 'wb+') as f:
                xd = requests.get(f'https://api.spotify.com/v1/playlists/{playlistId}', headers={"Authorization": f"Bearer {get_token()}"}).json()
                if 'images' in xd:
                    imgs = xd['images'] 
                    if not imgs or len(imgs) == 0:
                        return None
                    f.write(requests.get(imgs[0]['url']).content)
        return file

def savePlaylist(songs, title, id, filePath):
    if os.path.exists(filePath):
        return
    pictureUrl = getImgUrl(id)
    m3u8 = f'#EXTM3U\n#PLAYLIST:{title}\n#EXTALBUMARTURL:{pictureUrl}\n'
    m3u8 += '\n'.join([
        z[0] for z in 
        [
            [os.path.join(aa,bb) for bb in os.listdir(aa)] for aa in [
                os.path.join(y, 'spotify') for y in 
                [
                    os.path.join(cache, x['id'] or "None") for x in songs
                ] if os.path.exists(y) and os.path.isdir(y)
            ]
        ] 
        if len(z) != 0
    ])
    with open(filePath, 'w+', encoding='utf8') as f:
        f.write(m3u8)

with open('backup.json', encoding='utf8') as f:
    res = json.loads(f.read())

for x in res['playlists'].values():
    savePlaylist(x['tracks'], x['name'], x['id'], os.path.join(lists, f"{slugify(x['name'])} {x['id']}.m3u8"))

savePlaylist(res['saved'], "Liked Songs", None, os.path.join(lists, "liked.m3u8"))
