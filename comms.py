"""
Handles communication with the arduino over serial
"""
import serial
import serial.tools.list_ports
import time

def find_arduino():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if ("arduino" in str(port.manufacturer).lower()):
            return port.device

    return None

def connect(device):
    ser = serial.Serial(device, 9600, timeout=0.1,write_timeout=0.1)
    return ser


def parse_response(res, split = b'\r\n', filt = b'DEBUG:'):
    '''
    removes debug messages and extracts the
    actual response message
    res: the response to parse
    split: char sequence to split response message with
    filt: filter out lines that contain this substring
        pass an empty string to disable filtering
    '''
    lines = res.split(split)
    if filt != b'':
        return [l for l in lines if (not filt in l) and l != b'']

    return [l for l in lines if l!= b'']


sync_chars = {"week": b'f\n', "month": b'g\n'}


def send_albums(albums, ser, chart_type, verbose=False):
    """
    albums: zip of (scrobbles, [colors])
            max 50 elements
    ser: seruial connection to use
    chart_type: what kind of chart is this? "week" / "month".
        This changes what the arduino displays the info as
    verbose: enable extra logs
    """
    if ser == None or albums == None:
        return 1

    while (True):
        ser.write(sync_chars[chart_type])
        time.sleep(.5)
        # empty filt problem
        res = parse_response(ser.read(ser.in_waiting), filt=b'')
        if verbose:
            print(res)
        if len(res) > 0 and res[0] == b'f':
            break

    for album in albums:
        scrobbles = album[0]
        scrobbles = scrobbles.to_bytes(2, byteorder="big")
        palletlen = str(len(album[1]))
        # flatten + to bytes
        colors = [x.to_bytes(1, byteorder="big")
                  for xs in album[1] for x in xs]


        msg = bytearray()
        msg.extend(scrobbles)
        msg.extend(palletlen.encode())
        for byte in colors:
            msg.extend(byte)

        ser.write(msg)

        if verbose:
            print("A: ", album[0], album[1])
            print("msglen: ", len(msg))
            print("Sending: ", msg)

        time.sleep(.5)
        res = parse_response(ser.read(ser.in_waiting), filt=b'')
        print("RES: ", res if verbose else (res[0] if len(res) else "NOTHING"))
        time.sleep(.5)

    ser.write(b'e\n')
    time.sleep(.5)
    res = parse_response(ser.read(ser.in_waiting), filt=b'')
    print("closer: ", res)

    # useful when debugging
#    while(True):
#        res = parse_response(ser.read(ser.in_waiting), filt=b'')
#        print(res)
#        time.sleep(3)

