import os
from dotenv import load_dotenv
import argparse

import colorpallet
import lastfm
import comms

load_dotenv()
endpoint_url = lastfm.make_url_params("scringly", os.getenv('LASTFM_API_KEY'))

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--status", help="check arduino status", action="store_true")
parser.add_argument("chart", type=str, nargs=1
                    ,help="the chart to fetch: weeker or top")
parser.add_argument("--serial", type=str, const="", default="" , nargs="?"
                    ,help="specify a serial port to use")

# ===============================================
def top_albums(limit=50):
    data = lastfm.get_top_albums("7day", limit, endpoint_url)
    if data[1] != 200:
        return None

    data = data[0]
    urls = lastfm.extract_img_urls(data)

    colors = [colorpallet.compute_pallet(url) for url in urls]
    scrobbles = [int(album["playcount"]) for album in data["topalbums"]["album"]]
   
    ret = zip(scrobbles, colors)

    return ret


def weeker(limit=50):
    data = lastfm.get_weekly_chart(endpoint_url)
    if data[1] != 200:
        return None

    data = data[0]
    urls = lastfm.get_weekly_imgs(data, endpoint_url)[:limit]

    colors = [colorpallet.compute_pallet(url) for url in urls]
    scrobbles = [int(album["playcount"]) for album in data["weeklyalbumchart"]["album"]][:limit]

    ret = zip(scrobbles, colors)

    return ret


def connect_arduino(port):
    arport = port if len(port) > 0 else comms.find_arduino()
    if arport == None:
        return None
    return comms.connect(arport)


def main(testdata=None, overrideconnection=None):
    args = parser.parse_args()
    arduino = overrideconnection if overrideconnection else connect_arduino(args.serial)
    wants_albums = False
    albums = testdata

    import time
    time.sleep(5) # hilarious bug, gotta wait for the arduino to reset

    if not arduino:
        print("Arduino not connected")
        return

    if args.status:
        ar_status = comms.check_on_arduino(arduino)
        print(ar_status)
        if ar_status == -1:
            # TODO: reset it and try again
            print("Status Arduino unresponsive")
        elif ar_status == 1:
            wants_albums = True
        elif ar_status == 0:
            print("Status OK")

    if albums == None:
        if args.chart[0] == "top":
            albums = top_albums()
        elif args.chart[0] == "weeker":
            albums = weeker()

    if type(albums) == int:
        print(f"Failed to fetch top albums. errorcode: {albums}")
        return

    if wants_albums:
        comms.send_albums(albums, arduino)


def test(p):
    import json
    with open("topalbums.json", mode="r") as f:
        data = json.load(f)
        urls = lastfm.extract_img_urls(data)

        colors = [colorpallet.compute_pallet(url,2) for url in urls]
        scrobbles = [int(album["playcount"]) for album in data["topalbums"]["album"]]
       
        ret = zip(scrobbles, colors)
        arduino = comms.connect(p)
        main(ret, arduino)


main()
