import speech_recognition as sr
import pyttsx3 as ss
import pyaudio

import os
import sys
import select
import re

class Butler():

    tasks = []
    keywords = []
    mic = None
    rec = None

    def init(self, adjust_noise = True):
        os.system("sphinx_jsgf2fsg -jsgf butler.jsgf > butler.fsg")
        self.rec = sr.Recognizer()
        self.mic = sr.Microphone(device_index=4)
        
        if adjust_noise:
            with self.mic as source:
                self.rec.adjust_for_ambient_noise(source)

    def ask(self):
        self.talk("Yes Zen?")
        with self.mic as source:
            audio = self.rec.listen(source)
            if audio:
                reply = self.think(audio)
                self.talk(reply)

    def listen(self):
        pass

    def think(self, audio):
        text = ""
        try:

            kw = []
            for k in self.keywords:
                kw.append((k,1.0))
         
            recognizedKeyword = self.rec.recognize_sphinx(audio,grammar="butler.jsgf")
            idx = self.searchKeywords(recognizedKeyword.strip())


            engine = self.rec.recognize_sphinx(audio, show_all=True)
            hyp = engine.hyp()
            recognizedKeywords = hyp.hypstr
            print("You: "+recognizedKeyword, flush=True)
            res = self.searchKeywords(recognizedKeyword.strip())
            if res is None:
                return "I don't understand " + recognizedKeyword.strip() 
            return self.tasks[res[0]].execute(res[1])
        except sr.UnknownValueError:
            return "I don't understand" 
        except sr.RequestError as e:
            self.talk("error, {0}".format(e))
    

    def searchKeywords(self, input_string):
        idx = 0
        for kw in self.keywords:
            m = re.search(kw, input_string)
            if m:
               return idx,m
            idx+=1

        return None

    def talk(self, text):
        if text:
            speech = ss.init("espeak", True)
            speech.setProperty("voice", "en-rp+f4")
            speech.setProperty("rate", 140)
            speech.say(text)
            print("says: " + text, flush=True)
            speech.runAndWait()
            
    def addTask(self, task):
        self.tasks.append(task)
        self.keywords.append(task.getKeyword())
