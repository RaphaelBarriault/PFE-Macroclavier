#include "Keyboard_t.h"
#include <arduino.h> //Serial and digital read required

#define KEYBOARD_CURRENT_LAYER this->_layer[this->_current_layer] //Shortens code lines


//Communication state machine
#define STATE_START 0
#define STATE_LAYER 1
#define STATE_KEY 2
#define STATE_MODE 3
#define STATE_KEYBIND 4
#define STATE_LABEL 5
#define STATE_R 6
#define STATE_G 7
#define STATE_B 8
#define STATE_END 9
#define STATE_ERROR 10

//Communication frame bytes
#define BYTE_START 0x1
#define BYTE_LABEL 0x2
#define BYTE_END 0x3

//Keypress modes
#define MODE_PRINT 0
#define MODE_PRESS 1
#define MODE_LAYER 2
#define MODE_MEDIA 3

//Modifier key values as received over serial
#define PRESS_ALT 0x0E //Shift out
#define PRESS_CTRL 0x0F //Shift in
#define PRESS_SHIFT 0x10 //Data Link Escape
#define PRESS_WIN 0x11 //Device Control 1
#define PRESS_GUI 0x12 //Device Control 2

//Media key values as received over serial
#define MEDIA_UP 0x41 //A
#define MEDIA_DOWN 0x42 //B
#define MEDIA_MUTE 0x43 //C
#define MEDIA_PLAY 0x44 //D

//Layer key values as received over serial
#define LAYER_NEXT 0x55 //U
#define LAYER_PREV 0x44 //D


// Verification of the position of the mode switch
void Keyboard_t::update_sending_mode() {
  if (digitalRead(PIN_MODE2)) {
    this->_sending_mode = MODE_USB;
  }
  else if (digitalRead(PIN_MODE1)) {
    this->_sending_mode = MODE_BLUETOOTH;
  }
  else {
    this->_sending_mode = MODE_OFF;
  }
  // Update rgb_status
  //enter sleep mode if mode_off
}

//Changes current layer to next available layer
void Keyboard_t::next_layer() {
  if ((this->_current_layer) < (this->_last_layer)) {
    this->_current_layer++;
  }
  else {
    this->_current_layer = FIRST_LAYER;
  }
}

//Changes current layer to previous available layer
void Keyboard_t::previous_layer() {
  if (this->_current_layer > FIRST_LAYER) {
    this->_current_layer--;
  }
  else {
    this->_current_layer = this->_last_layer;
  }
}

//Changes current layer to specified layer
int Keyboard_t::layer_change(int keyname) {
  int is_success = 1;
  const char * request = KEYBOARD_CURRENT_LAYER.key[keyname].get_bind().c_str();

  if (request[0] == LAYER_PREV) {
    previous_layer();
  } else if (request[0] == LAYER_NEXT) {
    next_layer();
  } else if (request[0] < this->_last_layer) {
    this->_current_layer = request[0]; //GO TO LAYER
  } else {
    is_success = 0;
    // Error message: Unrecognized layer change request
  }

  if (is_success) {
    this->updateDisplay();
  }
  return is_success;
}

//Types keys one by one
int Keyboard_t::bleKeyboard_write(int keyname) {
  if (keyname < NB_BTN) {
    int is_success = 0;
    if (bleKeyboard.isConnected()) {
      this->bleKeyboard.print(KEYBOARD_CURRENT_LAYER.key[keyname].get_bind().c_str());
      is_success = 1;
    } else {
      // Error message: Bluetooth not connected
    }
    return is_success;
  }
}

//Types keys all at once, then releases
int Keyboard_t::bleKeyboard_press(int keyname) {
  int is_success = 0;
  string bind = KEYBOARD_CURRENT_LAYER.key[keyname].get_bind();
  for (int i = 0; i < bind.length(); i++) {
    if (bleKeyboard.isConnected()) {
      switch (((uint8_t *)bind.c_str())[i]) { //Typecasts the constant char pointer into a unsigned int 8 (same size) pointer to use as switch argument
        case PRESS_ALT:
          bleKeyboard.press(KEY_LEFT_ALT);
          break;
        case PRESS_CTRL:
          bleKeyboard.press(KEY_LEFT_CTRL);
          break;
        case PRESS_SHIFT:
          bleKeyboard.press(KEY_LEFT_SHIFT);
          break;
        case PRESS_WIN:
        case PRESS_GUI:
          bleKeyboard.press(KEY_LEFT_GUI);
          break;
        default:
          bleKeyboard.press(((uint8_t *)bind.c_str())[i]);
          break;
      }
      is_success = 1;
    } else {
      Serial.println("PRESS : BLUETOOTH NOT CONNECTED");
      // Error message: Bluetooth not connected
      is_success = 0;
      break;
    }
  }
  bleKeyboard.releaseAll();
  return is_success;
}

//Types keys one by one, media keys only.
int Keyboard_t::bleKeyboard_media(int keyname) {
  int is_success = 1;
  string bind = KEYBOARD_CURRENT_LAYER.key[keyname].get_bind();
  for (int i = 0; i < bind.length(); i++) {
    if (bleKeyboard.isConnected()) {
      switch (((uint8_t *)bind.c_str())[i]) { //Typecasts the constant char pointer into a unsigned int 8 (same size) pointer to use as switch argument
        case MEDIA_UP: //A
          bleKeyboard.write(KEY_MEDIA_VOLUME_UP);
          break;
        case MEDIA_DOWN: //B
          bleKeyboard.write(KEY_MEDIA_VOLUME_DOWN);
          break;
        case MEDIA_MUTE: //C
          bleKeyboard.write(KEY_MEDIA_MUTE);
          break;
        case MEDIA_PLAY: //D
          bleKeyboard.write(KEY_MEDIA_PLAY_PAUSE);
          break;
        default:
          Serial.println("MEDIA : INVALID MEDIAKEY");
          is_success = 0;
          break;
      }
    } else {
      is_success = 0;
      Serial.println("MEDIA : BLUETOOTH NOT CONNECTED");
      break;
      // Error message: Bluetooth not connected
    }
  }
  return is_success;
}

//Constructor
Keyboard_t::Keyboard_t() {
  this->_current_layer = 0;
  this->_last_layer = 0;
}

//Initialises the keyboard
void Keyboard_t::init() {
  displayInit();
  ledInit();
  this->bleKeyboard.begin();
}

// Keypress modes
// MODE_PRINT: write one at the time
// MODE_PRESS: press then releaseAll
// MODE_LAYER: layer modifier
// MODE_MEDIA: multimedia keys
void Keyboard_t::keypress(int input) {
  switch (KEYBOARD_CURRENT_LAYER.key[input].get_mode())
  {
    case MODE_PRINT:
      this->bleKeyboard_write(input);
      break;
    case MODE_PRESS:
      this->bleKeyboard_press(input);
      break;
    case MODE_LAYER:
      this->layer_change(input);
      break;
    case MODE_MEDIA:
      this->bleKeyboard_media(input);
      break;
    default:;
      // Error message: Unrecognized keybind mode
      break;
  }
}

void Keyboard_t::set_keybind(int layer, int keyname , char mode, string bind) {
  this->_layer[this->_current_layer].key[keyname].set_bind(mode, bind);
}

//Code executed during configuration mode
//Receiving : [BYTE_START][LAYER][KEY][DATA][BYTE_END]
//[DATA] = [MODE][KEYBIND][BYTE_LABEL][BITMAP/LABEL]
//If layer mode (key = NB_BTN) : [DATA] = [INVERTED][R][G][B]
void Keyboard_t::modeConfig(int serialInput) {
  //All variables are static to not lose their value and they are not reset
  static char state = STATE_START;
  static char layer, key, mode;
  static string keybind = "";
  static string label = "";
  static int r, g, b;
  static int length = 0;

  length++;
  switch (state) {
    case STATE_START:
      if (serialInput == BYTE_START) {
        state = STATE_LAYER;
      } else {
        state = STATE_ERROR;
      }
      break;
    case STATE_LAYER:
      if (serialInput < MAX_LAYER) {
        layer = serialInput;
        state = STATE_KEY;
      } else {
        state = STATE_ERROR;
      }
      break;
    case STATE_KEY:
      if (serialInput <= NB_BTN) {
        key = serialInput;
        state = STATE_MODE;
      } else {
        state = STATE_ERROR;
      }
      break;
    case STATE_MODE:
      mode = serialInput;
      if (key == NB_BTN) {
        state = STATE_R;
      } else {
        keybind = "";
        state = STATE_KEYBIND;
      }
      break;
    case STATE_KEYBIND:
      if ((serialInput != BYTE_LABEL) || ((keybind.length() == 0) && (mode == MODE_LAYER))) {
        keybind += serialInput;
        if (keybind.length() > MAX_KEYBIND) {
          keybind = "";
          state = STATE_ERROR;
        }
      } else {
        label = "";
        state = STATE_LABEL;
      }
      break;
    case STATE_LABEL:
      if (serialInput != BYTE_END) {
        label += serialInput;
        if (label.length() > DISPLAY_MAX_LABEL_LENGTH) {
          keybind = "";
          label = "";
          state = STATE_ERROR;
        }
      } else {
        this->set_keybind(layer, key, mode, keybind);
        this->_layer[layer].display.setLabel(key, label);
        if (layer > (this->_last_layer)) {
          _last_layer = layer;
        }
        state = STATE_START;
        //Serial.write(length);
        length = 0;
        Serial.write('S');
      }
      break;
    case STATE_R:
      r = serialInput;
      state = STATE_G;
    case STATE_G:
      g = serialInput;
      state = STATE_B;
    case STATE_B:
      b = serialInput;
      state = STATE_END;
      break;
    case STATE_END:
      if (serialInput == BYTE_END) {
        this->_layer[layer].led.set_rgb(r, g, b);
        this->_layer[layer].display.setInverted((boolean)mode);
        //Serial.write(length);
        length = 0;
        Serial.write('S');
        state = STATE_START;
      } else {
        state = STATE_ERROR;
      }
      break;
    default:
      state = STATE_START;
      break;
  }
  if (state == STATE_ERROR) {
    //Serial.write('\0');
    Serial.write('F');
    length = 0;
    state = STATE_START;
  }
}

//Updates eink display and led to current layer settings
void Keyboard_t::updateDisplay() {
  this->_layer[this->_current_layer].display.updateDisplay();
  this->_layer[this->_current_layer].led.updateLED();
}
