# TTS-AI

Desktop app that turns text into speech and speech into text. It also reads Braille input aloud and translates text between languages.

Modes:

1. Text to speech
2. Braille to speech
3. Translate text
4. Translate text, then speak it
5. Speech to text
6. Speech to text, translate, then speak it

Speech uses Google Text-to-Speech and the `speech_recognition` library. Translation calls the DeepSeek API.

## Run it

```bash
pip install -r requirements.txt
export DEEPSEEK_API_KEY=your-key   # only needed for translation
python TTS-AI.py
```

On Windows PowerShell, set the key with `$env:DEEPSEEK_API_KEY = "your-key"`.
