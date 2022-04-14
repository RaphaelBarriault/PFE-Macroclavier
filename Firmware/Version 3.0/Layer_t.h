#ifndef _LAYER_T_H_
#define _LAYER_T_H_

#include "Key_t.h"
#include "Led_t.h"
#include "Display_t.h"

#define NB_BTN 11   //8 mechanicals switches + 1 encoder button + CW encoder + CCW encoder

// Set of object composing the board
class Layer_t {
  private:
  public:
    Key_t key[NB_BTN]; //Keys on the keyboard
    Led_t led;         //Ledstrip (WS2812)
    Display_t display; //Eink display
};

#endif
