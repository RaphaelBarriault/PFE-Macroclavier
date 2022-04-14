#include "Display_t.h"
#include <GxEPD2_BW.h>                //Display library
#include <Fonts/FreeMonoBold9pt7b.h>  //Font default on screen

//Pre-processor macro required for the display with the corresponding pins
GxEPD2_BW<GxEPD2_290_T94_V2, GxEPD2_290_T94_V2::HEIGHT> display(GxEPD2_290_T94_V2(/*CS=5*/ 5, /*DC=*/ 2, /*RST=*/ 17, /*BUSY=*/ 16)); // GDEM029T94, Waveshare 2.9" V2 variant

#define DISPLAY_ORIENTATION_PORTRAIT      0
#define DISPLAY_ORIENTATION_LANDSCAPE     1
#define DISPLAY_ORIENTATION_INV_PORTRAIT  2
#define DISPLAY_ORIENTATION_INV_LANDSCAPE 3

#define DISPLAY_FONT_OFFSET 2 //Small offset to counter a bad behavior of text printing on the display

#define POS_X 0
#define POS_Y 1

unsigned int displayPosition[DISPLAY_POSITIONS][2]; //Positions on the e-ink display for buttons

//Initialises the display
void displayInit() {
  display.init();
  display.setRotation(DISPLAY_ORIENTATION_PORTRAIT); //Rotation may change on final product
  display.setFont(&FreeMonoBold9pt7b); //A default readable font size
  display.setFullWindow();
  display.firstPage(); //Wipes the controller

  //BTN1
  displayPosition[0][POS_X] = 0;
  displayPosition[0][POS_Y] = (unsigned int)(display.height() * 3 / 19);
  //BTN2
  displayPosition[1][POS_X] = 0;
  displayPosition[1][POS_Y] = (unsigned int)(display.height() * 7 / 19);
  //BTN3
  displayPosition[2][POS_X] = 0;
  displayPosition[2][POS_Y] = (unsigned int)(display.height() * 11 / 19);
  //BTN4
  displayPosition[3][POS_X] = 0;
  displayPosition[3][POS_Y] = (unsigned int)(display.height() * 15 / 19);
  //BTN5
  displayPosition[4][POS_X] = (unsigned int)(display.width());
  displayPosition[4][POS_Y] = (unsigned int)(display.height() * 4 / 19);
  //BTN6
  displayPosition[5][POS_X] = (unsigned int)(display.width());
  displayPosition[5][POS_Y] = (unsigned int)(display.height() * 8 / 19);
  //BTN7
  displayPosition[6][POS_X] = (unsigned int)(display.width());
  displayPosition[6][POS_Y] = (unsigned int)(display.height() * 12 / 19);
  //BTN8
  displayPosition[7][POS_X] = (unsigned int)(display.width());
  displayPosition[7][POS_Y] = (unsigned int)(display.height() * 16 / 19);
  //ENCODER LEFT
  displayPosition[8][POS_X] = 0;
  displayPosition[8][POS_Y] = (unsigned int)(display.height() - 6);
  //ENCODER MIDDLE
  displayPosition[9][POS_X] = (unsigned int)(display.width() / 2);
  displayPosition[9][POS_Y] = displayPosition[8][POS_Y];
  //ENCODER RIGHT
  displayPosition[10][POS_X] = (unsigned int)(display.width());
  displayPosition[10][POS_Y] = displayPosition[8][POS_Y];
}

//Wipes the controller and sets the opposite font color
void Display_t::reset() {
  if (this->inverted) { //Inverted = black screen and white text
    display.fillScreen(GxEPD_BLACK);
    display.setTextColor(GxEPD_WHITE);
  } else { //Not inverted = white screen and black text
    display.fillScreen(GxEPD_WHITE);
    display.setTextColor(GxEPD_BLACK);
  }
}

//Draws text into the controller's memory
void Display_t::printText(string text, unsigned char textPosition) {
  if ((text != "") && (textPosition < DISPLAY_POSITIONS)) { //If text is non-null and we use a valid position
    int16_t tbx, tby; uint16_t tbw, tbh; //Text Boundary : X, Y, Width, Height
    int x;    //Adjusted position
    const char * ctext = text.c_str(); //Position 0 of a null terminated char table
    display.getTextBounds(ctext, 0, 0, &tbx, &tby, &tbw, &tbh);
    tbw += DISPLAY_FONT_OFFSET; //The text is slightly bigger than the actual size
    x = displayPosition[textPosition][POS_X] - (tbw / 2); //Text centered on desired position
    //Avoid out-of-borders text
    if (x < 0) {
      x = 0;
    } else if ((x + tbw) >= display.width()) {
      x = display.width() - tbw;
    }
    display.setCursor(x, displayPosition[textPosition][POS_Y]); //Set cursor to the final position
    display.print(ctext);
  }
}

//Updates the display using the controller's memory
void Display_t::showDisplay() {
  display.nextPage();
}


Display_t::Display_t() {
  this->inverted = false;
}

void Display_t::setLabel(int key, string label) {
  if ((key < DISPLAY_POSITIONS) && (label != "")) { //Does not accept out of index position nor null string
    //If the string is too long, we remove the overflow
    if ((label.length() > DISPLAY_MAX_LABEL_LENGTH) && (key < DISPLAY_BUTTONS_POSITIONS)) {
      label.resize(DISPLAY_MAX_LABEL_LENGTH);
    } else if ((label.length() > DISPLAY_MAX_LABEL_LENGTH_ENCODER) && (key >= DISPLAY_BUTTONS_POSITIONS)) {
      label.resize(DISPLAY_MAX_LABEL_LENGTH_ENCODER);
    }
    this->bmpButtons[key] = label;
  }
}

//Wipes the display, then draw the right text and update the display
void Display_t::updateDisplay() {
  this->reset();
  for (int i = 0; i < DISPLAY_POSITIONS; i++) {
    this->printText(this->bmpButtons[i], i);
  }
  this->showDisplay();
}


void Display_t::setInverted(bool invert) {
  this->inverted = invert;
}
