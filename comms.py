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
    '''
    lines = res.split(split)
    ret = [l for l in lines if (not filt in l) and l != b'']
    return ret


def send_albums(albums, ser):
    """
    albums: zip of (scrobbles, [colors])
            max 50 elements
    """
    if ser == None or albums == None:
        return 1

    while (True):
        ser.write(b'f\n')
        time.sleep(.5)
        res = parse_response(ser.read(ser.in_waiting), filt=b'')
        print(res)
        if len(res) > 0 and res[0] == b'f':
            break

    for album in albums:
        print("A: ", album[0], album[1])

        scrobbles = album[0]
        scrobbles = scrobbles.to_bytes(2, byteorder="big")
        palletlen = str(len(album[1]))
        # flatten + to bytes
        colors = [x.to_bytes(1, byteorder="big")
                  for xs in album[1] for x in xs]


        msg = bytearray()
        msg.extend(scrobbles)
        msg.extend(palletlen.encode())
#        msg.extend("cowrathopgaplip".encode()) # 5 sets of RGB bytes
        for byte in colors:
            msg.extend(byte)

        msg.extend('\n'.encode())
        ser.write(msg)

        print("msglen: ", len(msg))

        time.sleep(.5)
        print("Sending: ", msg)
        res = parse_response(ser.read(ser.in_waiting), filt=b"")
        print("RES: ", res)
        time.sleep(.5)

    ser.write(b'e\b')
    time.sleep(.5)
    res = parse_response(ser.read(ser.in_waiting), filt=b"")
    print("closer: ", res)
