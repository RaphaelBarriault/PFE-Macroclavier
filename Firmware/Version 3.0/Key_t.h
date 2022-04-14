#ifndef _KEY_T_H_
#define _KEY_T_H_

#include <string> //Allows the use of string objects
using namespace std;

// One key of the Keymap
class Key_t {
  private:
    string _bind;
    char _mode;
  public:
    Key_t() ;

    void set_bind(char mode, string bind);

    char get_mode();

    string get_bind();

    int get_length();
};


#endif
