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


def parse_response(res, split = '\r\n', filt = 'DEBUG:'):
    '''
    removes debug messages and extracts the
    actual response message
    res: the response to parse
    split: char sequence to split response message with
    filt: filter out lines that contain this substring
    '''
    lines = res.decode("utf-8").split(split)
    ret = [l for l in lines if (not filt in l) and l != '']
    return ret


def send_albums(albums, ser):
    if ser == None:
        return 1

    while (True):
        ser.write(b'f\n')
        time.sleep(.5)
        res = parse_response(ser.read(ser.in_waiting))
        print(res)
        if len(res) > 0 and res[0] == "f":
            break

    scrobbles = 16
    scrobbles = scrobbles.to_bytes(2, byteorder="big")
    msg = bytearray()
    msg.extend(scrobbles)
    msg.extend("5".encode()) # the palletlen
    msg.extend("cowrathopgaplip".encode()) # 5 sets of RGB bytes
    ser.write(msg)


    # ready to recv now
    # send album data
    # ser.read(ser.in_waiting)
    # split string at \r\n
    # drop DEBUG: lines
    # parse the ACK line
    # repeat


