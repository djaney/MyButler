import speech_recognition as sr
import pyttsx3 as ss
import pyaudio

import os
import sys
import select

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
            idx = self.searchKeywords(recognizedKeyword.strip())

            if 0 > idx:
                return "I don't understand " + recognizedKeyword.strip() 

            return self.tasks[idx].execute()
        except sr.UnknownValueError:
            return "I don't understand" 
        except sr.RequestError as e:
            self.talk("error, {0}".format(e))
    

    def searchKeywords(self, input_string):
        heuristicScores = []
        topScore = 0
        topKey = -1
        for k in self.keywords:
            score = 0
            if 0 <= input_string.find(k):
                score = 1
            heuristicScores.append(score)
        idx = 0
        for s in heuristicScores:
            if s > topScore:
                topKey = idx
            idx+=1

        return topKey

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
