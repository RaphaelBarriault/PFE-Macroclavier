#include "Led_t.h"

#include "Freenove_WS2812_Lib_for_ESP32.h"

#define LEDS_COUNT  1
#define LEDS_PIN  15
#define CHANNEL   0

Freenove_ESP32_WS2812 strip = Freenove_ESP32_WS2812(LEDS_COUNT, LEDS_PIN, CHANNEL);

void ledInit()
{
  strip.begin();
}

void Led_t::set_rgb(unsigned char r, unsigned char g, unsigned char b) {
  this->_r = r;
  this->_g = g;
  this->_b = b;
}
void Led_t::set_r(unsigned char r) {
  this->_r = r;
}
void Led_t::set_g(unsigned char g) {
  this->_g = g;
}
void Led_t::set_b(unsigned char b) {
  this->_b = b;
}

//Changes the strip's color to setting values
void Led_t::updateLED() {
  strip.setLedColorData(0, (((unsigned long)this->_r) << 16) + (((unsigned long)this->_g) << 8) + ((unsigned long)this->_b));
  strip.show();
}

unsigned char Led_t::get_r() {
  return this->_r;
}
unsigned char Led_t::get_g() {
  return this->_g;
}
unsigned char Led_t::get_b() {
  return this->_b;
}
