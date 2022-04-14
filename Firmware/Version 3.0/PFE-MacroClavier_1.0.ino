/*
                      MACRO-KEYBOARD 2.0 FIRMWARE
   FEATURES TODO :
      -Communication needs correcting
      -IO Expander compatibility
      -Persistent memory
      -LED additional functions
      -Serial HID
*/

#include "Keyboard_t.h"

Keyboard_t keyboard; //Main keyboard object

void setup()
{
  Serial.begin(115200); //Initialises serial output at 115200 baudrate
  keyboard.init();      //Initialises the keyboard
}


void loop() {
  while (Serial.available()) { //If serial has received data
    keyboard.modeConfig(Serial.read()); //Keep reading
  }
  //  TODO read io expander
  //if (digitalRead(PIN_IO_INT)) {
  //
  //}
}
