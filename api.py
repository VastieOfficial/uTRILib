import base64
import json
import os
import time
from urllib.parse import parse_qs, quote, urlparse

import requests


def refreshToken():
    with open('.token.do-not-share', 'r') as f:
        r = json.loads(f.read())
        clID = r["client_id"]
        clS = r["client_secret"]
        rURL = r["redirect_url"]
        tok = requests.post(
            "https://accounts.spotify.com/api/token",
            data={
                "client_id": clID,
                "refresh_token": r['token']['refresh_token'],
                "grant_type": "refresh_token",
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": f"Basic {(base64.b64encode(f'{clID}:{clS}'.encode()).decode())}",
            },
        ).json()
        if 'refresh_token' not in tok:
            tok['refresh_token'] = r['token']['refresh_token'] # if we don't need to update refresh_token
        with open('.token.do-not-share', 'w+') as f:
            f.write(json.dumps({"token": tok, "lastUpdate": int(time.time()), "client_id": clID, "client_secret": clS, "redirect_url": rURL }))
        return tok['access_token']

def get_token():
    if os.path.exists('.token.do-not-share'):
        with open('.token.do-not-share', 'r') as f:
            r = json.loads(f.read())
            if time.time() > r['lastUpdate']+(r['token']['expires_in']-300):
                return refreshToken()
            else:
                return r['token']['access_token']
    else:
        client_id = input(
            "We assume you have created an app at https://developer.spotify.com/dashboard/ and you have it's client_id, redirect_uri and client secret.\nIf that's the case, paste your client ID, and press enter.\nIf not, create an app, and return to this script.\n\nYour client ID: "
        ).strip()
        client_secret = input("Input your client secret: ").strip()
        redirect_url = input("Input your redirect URI: ").strip()

        print(
            f"https://accounts.spotify.com/ru/authorize?response_type=code&client_id={client_id}&scope={quote('streaming,user-read-playback-state,user-modify-playback-state,user-read-currently-playing')}&redirect_uri={quote(redirect_url)}&scope=1"
        )
        returned = input("Paste the redirect URI after authorization: ")

        tok = requests.post(
            "https://accounts.spotify.com/api/token",
            data={
                "code": parse_qs(urlparse(returned).query)["code"][0],
                "redirect_uri": redirect_url,
                "grant_type": "authorization_code",
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": f"Basic {(base64.b64encode(f'{client_id}:{client_secret}'.encode()).decode())}",
            },
        ).json()
        with open('.token.do-not-share', 'w+') as f:
            f.write(json.dumps({"token": tok, "lastUpdate": int(time.time()), "client_id": client_id, "client_secret": client_secret, "redirect_url": redirect_url }))
        return tok['access_token']

print(get_token())