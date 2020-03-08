from gtts import gTTS
import os

def tts(message, filename):
    tts = gTTS(text=message, lang='en')
    tts.save(f'{filename}.mp3')
    os.system(f'mpg321 {filename}.mp3')