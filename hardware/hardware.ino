#include <FastLED.h>
#include <string.h>

#define LED_PIN  3

#define COLOR_ORDER GRB
#define CHIPSET     WS2811

#define BRIGHTNESS 10

// Params for width and height
const uint8_t kMatrixWidth = 8;
const uint8_t kMatrixHeight = 8;

// Param for different pixel layouts
const bool    kMatrixSerpentineLayout = true;
const bool    kMatrixVertical = false;


#define NUM_LEDS (kMatrixWidth * kMatrixHeight)
CRGB leds_plus_safety_pixel[ NUM_LEDS + 1];
CRGB* const leds( leds_plus_safety_pixel + 1);   // WRITE TO THIS

uint16_t XY( uint8_t x, uint8_t y);
uint16_t XYsafe( uint8_t x, uint8_t y);

/**================ state =====================**/
# define PALLET_MAX 6             // max number of colors per colorpallet
# define MAX_ALBUMS 40            // only store colors for these many albums 

struct album {
  uint16_t scrobbles;
  uint8_t palletlen;              // # colors in the pallet, max PALLET_MAX
  char colors[3*PALLET_MAX];      // dont feel like mallocing today
};

struct album topalbums[MAX_ALBUMS];


/** parse the first count chars of ascii numbers to ints 
  eg "345" -> 345
  returns -2 if it hits a non number char
  returns -1 if the passed array is a null ptr
*/
int ascii_to_int(const char *array, size_t count) {
  if (!array) {
    return -1;
  }

  int value = 0;
  for (size_t i = 0; i < count; i++) {
    if (isdigit((unsigned char)array[i])) {
      value = value * 10 + (array[i] - '0');
    } else {
      return -2;
    }
  }

  return value;
}

/**
  read top album data
  buffer: array of album structs
  len: length of buffer
  returns 0 on success
  returns 1 if nothing was read
  returns 2 if there was an error while reading albums
*/
int read_top_albums(struct album albums[], size_t len)
{
  Serial.println("f"); // ACK
  struct album albm;
  int buflen = sizeof(albm); // sizeof(albums[0])
  char abuf[buflen] = {0};

  memset(albums, 0, MAX_ALBUMS);

  int i = 0;
  while(i < MAX_ALBUMS) {
    Serial.println("DEBUG: ready!");
    while (!Serial.available())
    {
      // wait
    }

    if (Serial.peek() == 'e') {
      // TODO detect only e\n
      Serial.read();
      break;
    }

    memset(abuf, 0, buflen);
    int bytesread = Serial.readBytesUntil('\n', abuf, buflen);
    if (bytesread <= 0) return 1;

    // interpret first 2 bytes as a uint16
    albums[i].scrobbles = ((uint16_t)(uint8_t)abuf[0]<<8)|(uint16_t)(uint8_t)abuf[1];
    // 3rd byte is converted ascii number to int
    int plen = ascii_to_int(abuf + sizeof(albm.scrobbles), 1);
    if (plen < 0) return 2;
    albums[i].palletlen = min(PALLET_MAX, plen);
    // copy the rest into the colors array
    memcpy(albums[i].colors, abuf + sizeof(albm.scrobbles) + sizeof(albm.palletlen), sizeof(albm.colors));
    
    Serial.print(bytesread);
    Serial.print("|");
    Serial.println(i);

    Serial.print("DEBUG: ");
    Serial.print((int)albums[i].scrobbles);
    Serial.print(" ");
    Serial.print(albums[i].palletlen);
    Serial.print(" ");
    Serial.println(albums[i].colors[0]);
    i++;
  }
  return 0;
}

/** drops all chars in the Serial buffer upto and 
  including the \n
*/
void drop_till_nextline() {
  while(Serial.peek() != '\n') {
    Serial.read();
  }
  if (Serial.available()) Serial.read();
}

/** fill the rectangle defined by sx,sy,ex,ey with color */
void fill_color(CRGB color, uint8_t sx, uint8_t sy, uint8_t ex, uint8_t ey)
{
  for (int y = sy; y <= ey; y++) {
    for (int x = sx; x <= ex; x++)
      leds[XYsafe(x,y)] = color;
  }
}

void show_empty()
{
  fill_color(CRGB::Red, 2, 2, 5, 5);
  delay(50);
  FastLED.show();
}

void loop()
{
  static int have_albums = 0;
  //TODO: should use serialevent
  if (Serial.available()) {
    char b = Serial.read();
    if (b == 'f') {
      drop_till_nextline();

      int r = read_top_albums(topalbums, MAX_ALBUMS);
      if (r == 0) have_albums = 1;
      Serial.print("read returned ");
      Serial.println(r);
    } else if (b == 'c') {
      if (have_albums)
        Serial.println('c');
      else
        Serial.println('n');

      drop_till_nextline();
    } else {
      Serial.print('r');
    }
  }

  if (!have_albums) {
    show_empty();
    return;
  }

  // show a sequence of 2x2 tiles of the first color in each pallet
  for (int i = 0; i < MAX_ALBUMS; i += 4) {
    if (topalbums[i].scrobbles <= 0) break;
    fill_color(CRGB(
      topalbums[i].colors[0],
      topalbums[i].colors[1],
      topalbums[i].colors[2]),
      0,0,3,3
    );
    fill_color(CRGB(
      topalbums[i+1].colors[0],
      topalbums[i+1].colors[1],
      topalbums[i+1].colors[2]),
      4,0,7,3
    );
    fill_color(CRGB(
      topalbums[i+2].colors[0],
      topalbums[i+2].colors[1],
      topalbums[i+2].colors[2]),
      0,4,3,7
    );
    fill_color(CRGB(
      topalbums[i+3].colors[0],
      topalbums[i+3].colors[1],
      topalbums[i+3].colors[2]),
      4,4,7,7);
    delay(500);
    FastLED.show();
  }
}

void setup() {
  FastLED.addLeds<CHIPSET, LED_PIN, COLOR_ORDER>(leds, NUM_LEDS).setCorrection(TypicalSMD5050);
  FastLED.setBrightness( BRIGHTNESS );
  memset(topalbums, 0, MAX_ALBUMS);
  Serial.begin(9600);
}

/**================== Helpers ==================**/
uint16_t XY( uint8_t x, uint8_t y)
{
  uint16_t i;

  if( kMatrixSerpentineLayout == false) {
    if (kMatrixVertical == false) {
      i = (y * kMatrixWidth) + x;
    } else {
      i = kMatrixHeight * (kMatrixWidth - (x+1))+y;
    }
  }

  if( kMatrixSerpentineLayout == true) {
    if (kMatrixVertical == false) {
      if( y & 0x01) {
        // Odd rows run backwards
        uint8_t reverseX = (kMatrixWidth - 1) - x;
        i = (y * kMatrixWidth) + reverseX;
      } else {
        // Even rows run forwards
        i = (y * kMatrixWidth) + x;
      }
    } else { // vertical positioning
      if ( x & 0x01) {
        i = kMatrixHeight * (kMatrixWidth - (x+1))+y;
      } else {
        i = kMatrixHeight * (kMatrixWidth - x) - (y+1);
      }
    }
  }

  return i;
}

uint16_t XYsafe( uint8_t x, uint8_t y)
{
  if( x >= kMatrixWidth) return -1;
  if( y >= kMatrixHeight) return -1;
  return XY(x,y);
}

