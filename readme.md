# Serial communication protocol
Arduino starts in a waiting state, to begin sending album data
the computer first wakes the arduino up with `f\n`. If anything
else is sent the arduino responds with `r`.

Once woken up with `f\n` the arduino will interpret any data sent to it
as album data. The expected format is one album per line:

```
scrobbles (2 bytes) | pallet len (1 byte) | c1 (3bytes) | ... \n

scrobbles: interpreted as a 16bit uint
pallet len: an ASCII digit (ASCII 0 to ASCII 9), largest value accepted is 6
        any value greater than 6 will just be read as a 6
colors: c1, c2, ..., cpalletlen. Each color is a 3 byte RGB value.
        There can be a maximum of 6 colors.
\n: each album is terminated by a \n
```

## responses

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

The arduino may also send multiple lines of debug messages along with
each response, each debug line *always* starts with `DEBUG: `.
The main message is always at the top of a response:
```
main message
DEBUG: ...
DEBUG: ...
```

## outline

To finish sending albums the computer sends `e\n` which puts the arduino back
into its waiting state.

Sending `f\n` will clear any previous album data stored on the arduino

```
Computer           Arduino
----------------------------
  |                waiting
  | -------f\n--->    |
  | <------f\n---- indicate ready
  |                   |
  | ---album 1---> 
  | ---album 2---> 
  |     ...
  | ---album n---> 
  | ------e\n----> stop reading, go back to waiting
```

