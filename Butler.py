import speech_recognition as sr
import pyttsx3 as ss
import pyaudio

import os
import sys
import select
import re
import boto3
from tts.TextToSpeech import TextToSpeech

class Butler():

    tasks = []
    keywords = []
    mic = None
    rec = None
    tts = None
    name = "jude"
    espeak = True
    sqs = None
    sqsUrl = "https://sqs.ap-northeast-1.amazonaws.com/132806373247/mybutler"
    sqsRegion = "ap-northeast-1"

    def init(self, adjust_noise = True, espeak = True):
        os.system("sphinx_jsgf2fsg -jsgf butler.jsgf > butler.fsg")
        self.rec = sr.Recognizer()
        self.mic = sr.Microphone(device_index=4)
        self.tts = TextToSpeech()
        self.espeak = espeak
        botoSess = boto3.Session(profile_name='mybutler')
        self.sqs = botoSess.client("sqs")
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
        stop = self.rec.listen_in_background(self.mic, self.background_callback)
        return stop

    def background_callback(self, rec, audio):
        if audio:
            reply = self.think(audio, silent_failure=True, use_name=True)
            self.talk(reply)


    def think(self, audio, silent_failure=False, use_name=False):
        text = ""
        try:

            kw = []
            for k in self.keywords:
                kw.append((k,1.0))
         
            recognizedKeyword = self.rec.recognize_sphinx(audio,grammar="butler.jsgf")
            idx = self.searchKeywords(recognizedKeyword.strip(), use_name=use_name)


            engine = self.rec.recognize_sphinx(audio, show_all=True)
            hyp = engine.hyp()
            recognizedKeywords = hyp.hypstr
            print("You: "+recognizedKeyword, flush=True)
            res = self.searchKeywords(recognizedKeyword.strip())
            if res is None:
                if not silent_failure:
                    return "I don't understand " + recognizedKeyword.strip() 
            else:            
                return self.tasks[res[0]].execute(res[1])
        except sr.UnknownValueError:
            if not silent_failure:
                return "I don't understand" 
        except sr.RequestError as e:
            if not silent_failure:
                return "error, {0}".format(e)
    

    def searchKeywords(self, input_string, use_name=False):
        idx = 0
        for kw in self.keywords:
            if use_name:
                kw = "hey "+self.name+" " + kw
            m = re.search(kw, input_string)
            if m:
               return idx,m
            idx+=1

        return None

    def talk(self, text):
        if text:
            print("says: " + text, flush=True)
            if self.espeak:
                speech = ss.init("espeak", True)
                speech.setProperty("voice", "en-rp+f4")
                speech.setProperty("rate", 140)
                speech.say(text)
                speech.runAndWait()
            else:
                self.tts.get_pronunciation(text)
    
    def checkPassive(self):
        response = self.sqs.receive_message(QueueUrl=self.sqsUrl)
        print(response)
        for m in response.get("Messages", []):
            msg = m.get("Body")
            if msg:
                self.talk(msg)
    def addTask(self, task):
        self.tasks.append(task)
        self.keywords.append(task.getKeyword())
