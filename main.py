import os
from dotenv import load_dotenv

import colorpallet
import lastfm
import comms

load_dotenv()
endpoint_url = lastfm.make_url_params("scringly", os.getenv('LASTFM_API_KEY'))

def top_albums():
    data = lastfm.get_top_albums("7day", 3, endpoint_url)
    if data[1] != 200:
        return None

    data = data[0]
    urls = lastfm.extract_img_urls(data)

    colors = [colorpallet.compute_pallet(url) for url in urls]
    scrobbles = [int(album["playcount"]) for album in data["topalbums"]["album"]]
   
    ret = zip(scrobbles, colors)

    return ret


def weeker():
    data = lastfm.get_weekly_chart(endpoint_url)
    if data[1] != 200:
        return None

    data = data[0]
    urls = lastfm.get_weekly_imgs(data, endpoint_url)

    colors = [colorpallet.compute_pallet(url) for url in urls]
    scrobbles = [int(album["playcount"]) for album in data["weeklyalbumchart"]["album"]]

    ret = zip(scrobbles, colors)

    return ret


def main(overrideport=None, testdata=None):
    albums = testdata if testdata != None else top_albums()

    if type(albums) == int:
        print(f"Failed to fetch top albums {albums}")
        return

    arduino = comms.find_arduino()
    if arduino == None:
        print("No arduino found!\n")
        return

    if (overrideport != None):
        arduino = comms.connect(overrideport)
    else:
        arduino = comms.connect(arduino)

    comms.send_albums(albums, arduino)


def test(p):
    import json
    with open("topalbums.json", mode="r") as f:
        data = json.load(f)
        urls = lastfm.extract_img_urls(data)

        colors = [colorpallet.compute_pallet(url,2) for url in urls]
        scrobbles = [int(album["playcount"]) for album in data["topalbums"]["album"]]
       
        ret = zip(scrobbles, colors)

        main(p, ret)
