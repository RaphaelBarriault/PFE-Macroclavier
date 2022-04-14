#ifndef _LED_T_H_
#define _LED_T_H_

void ledInit();

// Led strip of 10 WS2812b on board
class Led_t {
  private:
    unsigned char _r;
    unsigned char _g;
    unsigned char _b;
    int _mode;
  public:
    void set_rgb(unsigned char r, unsigned char g, unsigned char b);
    void set_r(unsigned char r);
    void set_g(unsigned char g);
    void set_b(unsigned char b);
    void updateLED(); //Changes the strip's color to setting values
    unsigned char get_r();
    unsigned char get_g();
    unsigned char get_b();
    // Insert animation here
};


#endif
