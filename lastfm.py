"""
lastfm API handling
"""
import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()
endpoint = "https://ws.audioscrobbler.com/2.0/?"

def make_url_params(user, key):
    def aux(params):
        return f"{params}&user={user}&api_key={key}&format=json"
    return aux


def get_top_albums(period, limit, url):
    params = url(f"method=user.gettopalbums&period={period}&limit={limit}")
    res = requests.get(endpoint+params)
    data = None

    if (res.status_code == 200):
        data = json.loads(res.text)
    
    return (data, res.status_code)


# doesnt have img urls have to use https://www.last.fm/api/show/album.getInfo
# to get the images one by one
def get_weekly_chart(url):
    params = url(f"method=user.getweeklyalbumchart")
    res = requests.get(endpoint+params)
    data = None

    if (res.status_code == 200):
        data = json.loads(res.text)
    
    return (data, res.status_code)


def extract_img_urls(data, size=0):
    """
    extracts the image urls from data returned from get_top_albums
    size: select the target image size to extract
        0: small, 1: medium
    """
    urls = []
    for album in data["topalbums"]["album"]:
        urls.append(album["image"][size]["#text"])

    return urls


# TODO: move this and all env stuff to main.py
url = make_url_params("scringly", os.getenv('LASTFM_API_KEY'))
#print(get_top_albums("7day",3,url))
#print(get_weekly_chart(url))
