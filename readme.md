# Serial communication protocol
Arduino starts in a waiting state, to begin sending album data
the computer first wakes the arduino up with a wake command (`f\n` or `g\n`)
If anything else is sent the arduino responds with `r`.

## Messages

```
f\n : tell the arduino to start receiving album data and then display it
    as a "week chart"

g\n : tell the arduino to start receiving album data and then display it
    as a "month chart"

f\n : ACK to f\n or g\n from arduino to the computer

r: response from arduino telling computer that the last
    message was invalid (ie it should send a f\n again)

c\n : ask the arduino for a status check

c\n : response from arduino saying that its running
    and has album data (OK)

n\n : response from arduino saying that it needs
    album data
```

The arduino may also send multiple lines of debug messages along with
each response, each debug line *always* starts with `DEBUG: `.
The main message is always at the top of a response:
```
main message
DEBUG: ...
DEBUG: ...
```

## album data
Once woken up with `f\n` the arduino will interpret any data sent to it
as album data. Each albums data is sent in a 6 to 21 byte packet:

```
scrobbles (2 bytes) | pallet len (1 byte) | c1 (3bytes) | ...

scrobbles: interpreted as a 16bit uint
pallet len: an ASCII digit (ASCII 0 to ASCII 9), largest value accepted is 6
        any value greater than 6 will just be read as a 6
colors: c1, c2, ..., cpalletlen. Each color is a 3 byte RGB value.
        There can be a maximum of 6 colors.
```
The packets are NOT TERMINATED, the arduino will read the data as a single
packet if 21 bytes get sent or < 21 bytes are sent and then readByte() times out
whichever happens first

In response to each album sent the arduino sends back an ACK. The ACK is
an ASCII string with format:
```
bytes read|album #

bytes read: digits representing how many bytes were read
        (used to detect errors maybe)
| : "|" as a separator character
album #: digits representing the index in the albums list to which the
        album data was saved to.
```


## outline

To finish sending albums the computer sends `e\n` which puts the arduino back
into its waiting state.

Sending `f\n` or `g\n` will clear any previous album data stored on the arduino

```
Sending album data:
Computer           Arduino
----------------------------
  |                waiting
  | -------f\n--->    |
  | <------f\n---- indicate ready
  |                   |
  | ---album 1---> 
  | <-- b | a#----   ACK
  | ---album 2---> 
  | <-- b | a#----   ACK
  |     ...
  | ---album n---> 
  | <-- b | a#----   ACK
  | ------e\n----> stop reading, go back to waiting
  OR:
  |                waiting
  | -------g\n--->    |
  | <------f\n---- indicate ready
  |                   |
  | ---album 1---> 
  | <-- b | a#----   ACK
  | ---album 2---> 
  | <-- b | a#----   ACK
  |     ...
  | ---album n---> 
  | <-- b | a#----   ACK
  | ------e\n----> stop reading, go back to waiting

Status check:
Computer           Arduino
----------------------------
albums already sent:
  |                waiting
  | -------c\n--->    |
  | <------c\n---- running OK
  |                   |

albums not sent:
  |                waiting
  | -------c\n--->    |
  | <------n\n---  running, pls send album data

```

