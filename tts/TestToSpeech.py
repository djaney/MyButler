#!/usr/bin/env python3
#Written by Alex I. Ramirez @alexram1313
#arcompware.com
import re
import wave
import pyaudio
import _thread
import time
import os;

class TextToSpeech:
    
    CHUNK = 1024

    def __init__(self, words_pron_dict:str = '/cmudict-0.7b.txt'):
        self.path = os.path.dirname(os.path.realpath(__file__))
        words_pron_dict = self.path + words_pron_dict
        self._l = {}
        self._load_words(words_pron_dict)

    def _load_words(self, words_pron_dict:str):
        with open(words_pron_dict, 'r') as file:
            for line in file:
                if not line.startswith(';;;'):
                    key, val = line.split('  ',2)
                    self._l[key] = re.findall(r"[A-Z]+",val)

    def get_pronunciation(self, str_input):
        list_pron = []
        for word in re.findall(r"[\w']+",str_input.upper()):
            if word in self._l:
                list_pron += self._l[word]
        print(list_pron)
        delay=0
        for pron in list_pron:
            pron = pron.lower()
            try:
                with wave.open(self.path+"/sounds/"+pron+".wav", 'rb') as wf:
                    _thread.start_new_thread( self._play_audio, (pron,delay,))
                    frames = wf.getnframes()
                    rate = wf.getframerate()
                    duration = frames / float(rate)
                    delay += duration
            except:
                pass
    
    def _play_audio(self, sound, delay):
        try:
            time.sleep(delay)

            with wave.open(self.path+"/sounds/"+sound+".wav", 'rb') as wf:
                p = pyaudio.PyAudio()
                stream = p.open(format=p.get_format_from_width(wf.getsampwidth()), channels=wf.getnchannels(), rate=wf.getframerate(), output=True)
            
                data = wf.readframes(TextToSpeech.CHUNK)
            
                while data:
                    stream.write(data)
                    data = wf.readframes(TextToSpeech.CHUNK)
        
            stream.stop_stream()
            stream.close()

            p.terminate()
            return
        except:
            pass
    
 
 

if __name__ == '__main__':
    tts = TextToSpeech()
    while True:
        tts.get_pronunciation(input('Enter a word or phrase: '))
