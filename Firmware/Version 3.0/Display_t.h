#ifndef _DISPLAY_T_H_
#define _DISPLAY_T_H_

#include <string> //Allows the use of string objects
using namespace std;

#define DISPLAY_POSITIONS 11
#define DISPLAY_BUTTONS_POSITIONS 8
#define DISPLAY_MAX_LABEL_LENGTH 10
#define DISPLAY_MAX_LABEL_LENGTH_ENCODER 2


void displayInit();

// Eink display for one layer
class Display_t {
  private:
    string bmpButtons [DISPLAY_POSITIONS]; //Labels for display
    bool inverted;

    void reset(); //Wipes the controller and sets the opposite font color
    void printText(string text, unsigned char textPosition); //Draws text into the controller's memory
    void showDisplay(); //Updates the display using the controller's memory
  public:
    Display_t();
    void setLabel(int key, string label);
    void updateDisplay(); //Wipes the display, then draw the right text and update the display
    void setInverted(bool invert);
};
#endif
