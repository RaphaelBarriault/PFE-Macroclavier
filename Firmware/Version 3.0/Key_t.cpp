#include "Key_t.h"

Key_t::Key_t() {
  this->_bind = string("");
  this->_mode = 0;
}

void Key_t::set_bind(char mode, string bind) {
  this->_bind = bind;
  this->_mode = mode;
}

char Key_t::get_mode() {
  return this->_mode;
}

string Key_t::get_bind() {
  return this->_bind;
}

int Key_t::get_length() {
  return this->_bind.length();
}
