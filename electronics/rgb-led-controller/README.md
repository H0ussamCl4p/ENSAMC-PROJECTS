# RGB LED controller

An ESP32 drives a 12V RGB LED strip through three TIP120 transistors. It serves a small web page on the local network with buttons to raise, lower or toggle each colour.

## Parts

- ESP32
- 3 × TIP120 NPN transistors
- 3 × 10 kΩ resistors
- 12V RGB LED strip
- 9V battery, breadboard, jumper wires, PCB

## Run it

1. Open `rgb-led-controller.ino` in the Arduino IDE with ESP32 board support installed.
2. Set `ssid` and `password` to your Wi-Fi network.
3. Upload, open the serial monitor to get the board's IP address, then open that address in a browser.

Pins: red 26, green 27, blue 25.

The full project report (in French) is in [rapport.pdf](rapport.pdf).
