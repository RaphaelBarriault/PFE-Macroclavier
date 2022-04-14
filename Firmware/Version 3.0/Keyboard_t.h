#ifndef _KEYBOARD_T_H_
#define _KEYBOARD_T_H_

#include <BleKeyboard.h>
#include "Layer_t.h"

#include <string>
using namespace std;

// Pin for the mode switch
#define PIN_MODE1 34
#define PIN_MODE2 35

// Pin for the LiPo Charger Status
#define PIN_CHRG
#define PIN_STDBY

// Pin for the Battery voltage
#define PIN_VBAT_FB
#define PIN_VBAT_EN 33

// Pin for the status RGB LED
#define PIN_RGB_R 25
#define PIN_RGB_G 26
#define PIN_RGB_B 27

// Pin for the rotary encoder
#define PIN_ENCODER_A 13
#define PIN_ENCODER_B 14

// Pin for the E-ink
#define PIN_EINK_SDI 23
#define PIN_EINK_SCL 18
#define PIN_EINK_CS 5
#define PIN_EINK_RST 17
#define PIN_EINK_BUSY 16
#define PIN_EINK_DC 2

// Pin for the IO expander
#define PIN_I2C_SDA 21
#define PIN_I2C_SCL 22
#define PIN_IO_INT 15
// Pin on the IO expander
#define PIN_BTN1 PO0
#define PIN_BTN2 PO1
#define PIN_BTN3 PO2
#define PIN_BTN4 PO3
#define PIN_BTN5 PO4
#define PIN_BTN6 PO5
#define PIN_BTN7 PO6
#define PIN_BTN8 PO7
#define PIN_BTN_ENC PO10

///*** DEFINE ***///
// Definitions
#define MAX_KEYBIND 128
#define MAX_LAYER 9
#define FIRST_LAYER 0

// Switch Modes
#define MODE_OFF 0
#define MODE_USB 1
#define MODE_BLUETOOTH 2

// Top hierarchy object
class Keyboard_t {
  private:
    Layer_t _layer[MAX_LAYER];
    int _current_layer;
    int _last_layer;
    int _sending_mode;
    BleKeyboard bleKeyboard;

    void update_sending_mode(void); // Verification of the position of the mode switch

    void next_layer() ; //Changes current layer to next available layer
    void previous_layer() ; //Changes current layer to previous available layer
    int layer_change(int keyname); //Changes current layer to specified layer

    // Bluetooth functions
    int bleKeyboard_write(int keyname); //Types keys one by one
    int bleKeyboard_press(int keyname); //Types keys all at once, then releases
    int bleKeyboard_media(int keyname); //Types keys one by one, media keys only.

    // USB Serial functions

  public:

    Keyboard_t(); //Constructor
    void init(); //Initialises the keyboard

    // Keypress modes
    // MODE_PRINT: write one at the time
    // MODE_PRESS: press then releaseAll
    // MODE_LAYER: layer modifier
    // MODE_MEDIA: multimedia keys
    void keypress(int input);

    void set_keybind(int layer, int keyname , char mode, string bind);

    //Code executed during configuration mode
    //Receiving : [BYTE_START][LAYER][KEY][DATA][BYTE_END]
    //[DATA] = [MODE][KEYBIND][BYTE_LABEL][BITMAP/LABEL]
    //If layer mode (key = NB_BTN) : [DATA] = [INVERTED][R][G][B]
    void modeConfig(int serialInput);

    void updateDisplay(); //Updates eink display and led to current layer settings
};

#endif
