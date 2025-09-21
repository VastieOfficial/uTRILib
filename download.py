import asyncio
import base64
import json
import os
import random
import shutil
import traceback

import aiohttp
import mutagen.aac
import mutagen.flac
import mutagen.mp3
import mutagen.oggvorbis
from api import get_token
from mutagen.flac import Picture
from oggFixer import fixVorbis

cache = os.getenv("TRI_CACHE", os.path.join(os.getcwd(), "TRICACHE"))
port = int(os.getenv("TRI_SPOTIFY_PORT", "3500"))

if not os.path.exists(cache):
    os.mkdir(cache)


async def dl(id):
    token = get_token()
    if os.path.exists(os.path.join(cache, id)):
        return [True, ""] # track is already downloaded
    try:
        async with aiohttp.ClientSession() as s:
            async with s.post(f"http://127.0.0.1:{port}/dl", json={
                "url": f"spotify:track:{id}",
                "title": "",
                "hash": id,
                "token": token
            }, timeout=300) as r:
                r = await r.json()
                return [r['ok'], r['error']]
    except Exception:
        traceback.print_exc()
        return [False, traceback.format_exc()]
    
def mod_track(id, i = 0):
    try:
        path = os.path.join(cache, id, "spotify", os.listdir(os.path.join(cache, id, "spotify"))[0])
        path_metadata = os.path.join("prefetch", id+".json")
        with open(path_metadata) as f:
            r = json.loads(f.read())
        type = mutagen.oggvorbis if path.endswith('.ogg') else mutagen.mp3 if path.endswith('.mp3') else mutagen.aac if path.endswith('.aac') else mutagen.flac
        file = type.Open(path)
        file.tags['title'] = r['title']
        file.tags['artist'] = [x['name'] for x in r['artists']]
        
        with open(path_metadata.replace('.json', '.jpg'), "rb") as h:
            data = h.read()

        picture = Picture()
        picture.data = data
        picture.mime = u"image/jpeg"

        picture_data = picture.write()
        encoded_data = base64.b64encode(picture_data)
        vcomment_value = encoded_data.decode("ascii")
        file.tags['metadata_block_picture'] = [vcomment_value]
        file.tags['date'] = r['releaseDate']['isoString']
        file.tags['RELEASEDATE'] = r['releaseDate']['isoString']
        file.tags['album'] = r['album'] if 'album' in r else 'N/A'
        file.tags['comments'] = f'Downloaded & encoded with TRILIB: https://github.com/VastieOfficial/TRILIB-Spotify\nMetadata from Spotify.\nSpotify ID: {id}'
        file.save()
        fixVorbis(path)
        return True
    except Exception as e:
        if i > 3:
            #traceback.print_exc()
            raise e
        return mod_track(id, i+1)
    
async def download_track(track):
    for a in range(1, 5): # up to 120 seconds in cooldowns
        d = await dl(track)
        if not d[0]:
            print(f"Failed {track}: {d[1]}")
            if 'Bad credentials' in d[1]:
                print("Error: Please check the token and try again.")                
                return 
            if 'no files available' in d[1]:
                with open(os.path.join(cache, track), 'w+') as ff:
                    ff.write("")
            break
        try:
            mod_track(track)
        except Exception as ex:
            if ', expected' in ''.join(traceback.format_exception(ex)):
                print(f"Track {track} is damaged. Need a cooldown, probably cannot retrieve key. Attempt {a}")
                shutil.rmtree(os.path.join(cache, track), True)
                tim = 25*a
                await asyncio.sleep(tim)
                continue
            else:
                traceback.print_exception(ex)
        print(f"Done {track} at {a} attempt")
        return ""
    return "queue.Me"

async def main():
    tracks_dld = os.listdir(cache)
    tracks = list(set([x.replace('.json', '') for x in os.listdir('prefetch') if x.endswith('.json') and x.replace('.json', '') not in tracks_dld]))
    random.shuffle(tracks)
    
    for x in tracks:
        if "queue.Me" == await download_track(x):
            tracks.append(x)
        

asyncio.run(main())