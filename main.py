import os
from dotenv import load_dotenv
import argparse

import colorpallet
import lastfm
import comms

load_dotenv()
endpoint_url = lastfm.make_url_params("scringly", os.getenv('LASTFM_API_KEY'))
api_session = lastfm.create_api_session()

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose", action="store_true"
                    , help="increase output verbosity")
parser.add_argument("-c", "--clear", action="store_true"
                    , help="set led panel to black")
parser.add_argument("chart", type=str, nargs=1
                    ,help="the chart to fetch: topweek / topmonth/ weeker")
parser.add_argument("--serial", type=str, const="", default="" , nargs="?"
                    ,help="specify a serial port to use")

# ===============================================
def top_albums(period="7day", limit=40):
    data = lastfm.get_top_albums(period, limit, endpoint_url, api_session)
    if data[1] != 200:
        return None

    data = data[0]
    urls_scrobs = extract_urls_scrobbles(data)

    colors = [colorpallet.compute_pallet(it[0], api_session) for it in urls_scrobs]
    scrobbles = [it[1] for it in urls_scrobs] # grugbrain
   
    return zip(scrobbles, colors)


def extract_urls_scrobbles(data, size=0):
    """
    extracts the image urls and scrobbles from data returned from get_top_albums
    size: select the target image size to extract
        0: small, 1: medium
    returns: [(url, scrobbles)]
    """
    ret = []
    for album in data["topalbums"]["album"]:
        if album["image"][size]["#text"]:
            ret.append((album["image"][size]["#text"], int(album["playcount"])))

    return ret


def weeker(limit=40):
    data = lastfm.get_weekly_chart(endpoint_url, api_session)
    if data[1] != 200:
        return None

    data = data[0]
    urls_scrobs = lastfm.get_weekly_imgs(data, endpoint_url, api_session)[:limit]

    colors = [colorpallet.compute_pallet(it[0], api_session) for it in urls_scrobs]
    scrobbles = [it[1] for it in urls_scrobs] # grugbrain

    return zip(scrobbles, colors)


def connect_arduino(port):
    arport = port if len(port) > 0 else comms.find_arduino()
    if arport == None:
        return None
    return comms.connect(arport)


def main():
    args = parser.parse_args()
    arduino = connect_arduino(args.serial)

    def prepare_send(albums, chart_type):
        if type(albums) == int:
            print(f"Failed to fetch {chart_type} albums. errorcode: {albums}")
            return None

        def aux(arduino, verbose):
            return comms.send_albums(albums, arduino, chart_type, verbose)
        return aux


    import time
    time.sleep(5) # hilarious bug, gotta wait for the arduino to reset

    if not arduino:
        print("Arduino not connected")
        return

    if args.clear:
        comms.send_clearcmd(arduino, args.verbose)
        return

    send = None

    if args.chart[0] == "topweek":
        send = prepare_send(top_albums(), "week")
    elif args.chart[0] == "topmonth":
        send = prepare_send(top_albums("1month"), "month")
    elif args.chart[0] == "weeker":
        send = prepare_send(weeker(), "week")
    else:
        print(f"{args.chart[0]} is not a valid chart")

    if send:
        send(arduino, args.verbose)


main()
