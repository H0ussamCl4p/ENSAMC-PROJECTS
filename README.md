# ENSAMC Projects

Projects I built as a student at ENSAM Casablanca: course projects, electronics, small tools, and the apps I made for the students' association with Nova.

## Course projects

| Project | What it is | Stack |
|---|---|---|
| [GPS tracker](academic/gps-tracker) | Vehicle tracker sending its position over GSM to Firebase, with a live map (Automotive Technology) | ESP8266, SIM800A, Firebase, JavaScript |
| [SIRD app](academic/sird-covid) | Covid-19 in Indonesia with the SIRD model: interpolation, integration, ODEs (Numerical Analysis) | Python |
| [Backdoor](academic/backdoor) | Lab proof of concept of an in-memory payload loader, with detection rules (Security) | Python, Metasploit |

## Nova and the students' association

| Project | What it is | Stack |
|---|---|---|
| [Ticket app](nova/ticket-app) | QR-code tickets and door check-in for a 2025 party | Flask, Firestore |
| [RC-Maps](nova/rc-maps) | 3D map of the clubs fair and a live vote for the best club | React, Three.js, Express |
| [EDTECH](nova/edtech) | Website for an educational technology event | SvelteKit |
| [Nova site](nova/site) | Link page for the Nova list | HTML, CSS |

## Electronics

| Project | What it does | Hardware |
|---|---|---|
| [RGB LED controller](electronics/rgb-led-controller) | Control a 12V RGB LED strip from a web page served by an ESP32 | ESP32, TIP120 transistors |
| [Irrigation system](electronics/irrigation-system) | Waters a plant when the soil gets dry | Arduino Uno, soil sensor, relay, pump |

## Software

| Project | What it does | Stack |
|---|---|---|
| [TTS-AI](software/tts-ai) | Text-to-speech, speech-to-text, Braille-to-speech and translation in one desktop app | Python, customtkinter, gTTS |
| [Graph app](software/graph-app) | Plot X/Y data with a linear regression line and save it as PNG | Python, Tkinter, matplotlib |
| [Birthday script](software/birthday-script) | Blinking "Happy Birthday" banner in the terminal | Python, pyfiglet |

## Clubs

| Project | What it is |
|---|---|
| [Arts & Crafts Aeronautics](clubs/aeronautics) | Link page for the ENSAM Casablanca aeronautics club |

The static sites are served from this repo with GitHub Pages:
[Nova](https://h0ussamcl4p.github.io/ENSAMC-PROJECTS/nova/site/) ·
[Aeronautics club](https://h0ussamcl4p.github.io/ENSAMC-PROJECTS/clubs/aeronautics/)

## Licence

MIT, see [LICENSE](LICENSE).
