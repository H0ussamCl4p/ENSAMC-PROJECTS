# GPS tracker

Automotive Technology module at ENSAM Casablanca, supervised by Mr. El Kebch Ali.

A vehicle tracker: an ESP8266 NodeMCU reads a GPS module and sends the position to Firebase Realtime Database over GSM (SIM800A), so it keeps working without Wi-Fi. A web dashboard shows the live position on a map and can draw a route with OpenRouteService.

```
GPS module -> ESP8266 -> SIM800A (GSM) -> Firebase -> web dashboard
```

## Hardware

- NodeMCU ESP8266
- GPS module (NEO-6M)
- GSM module (SIM800A) and a SIM card with data
- Breadboard, wires, power supply

## Run it

1. Open `firmware/GPS-GSM-Firebase.ino` in the Arduino IDE. Set your Wi-Fi, Firebase details and the phone number for SMS alerts, then upload.
2. In `dashboard/app.js`, set your Firebase config and an OpenRouteService API key.
3. Open `dashboard/index.html` in a browser.
