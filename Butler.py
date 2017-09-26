import speech_recognition as sr
import pyttsx3 as ss
import pyglet

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
    stt = None
    name = "Jude"
    tts_engine = None
    stt_engine = None
    push_to_talk = True
    sqs = None
    sqsUrl = "https://sqs.ap-northeast-1.amazonaws.com/132806373247/mybutler"
    sqsRegion = "ap-northeast-1"
    energy = 300

    def init(self, adjust_noise = True, tts = "espeak", stt = "cmusphinx",
            push_to_talk = True, energy = 300):
        #os.system("sphinx_jsgf2fsg -jsgf butler.jsgf > butler.fsg")
        self.rec = sr.Recognizer()
        self.mic = sr.Microphone(device_index=None)
        self.tts = TextToSpeech()
        self.tts_engine = tts
        self.stt_engine = stt
        self.push_to_talk = push_to_talk
        self.energy = energy
        self.botoSess = boto3.Session(profile_name='mybutler')
        self.sqs = self.botoSess.client("sqs")
        self.google_credentials = None

        if 0 == self.energy:
            if adjust_noise:
                with self.mic as source:
                    self.rec.adjust_for_ambient_noise(source)
                    print("Energy: "+ str(self.rec.energy_threshold))
        else:
            self.rec.dynamic_energy_threshold = False
            self.rec.energy_threshold = self.energy
    
    def setGoogleCredentials(self, cred):
        self.google_credentials = cred

    def ask(self):
        self.talk("Yes Zen?")
        with self.mic as source:
            audio = self.rec.listen(source)
            if audio:
                reply = self.think(audio)
                self.talk(reply)

    def listen(self):
        stop = self.rec.listen_in_background(self.mic,
                self.background_callback, phrase_time_limit=5)
        return stop

    def background_callback(self, rec, audio):
        print("--voice detected--", flush=True)
        if audio:
            reply = self.think(audio,use_name=True)
            if reply:
                self.talk(reply)


    def think(self, audio, silent_failure=False, use_name=False):
        text = ""
        if "cmusphinx"==self.stt_engine:
            try:
                keywords = [("hey "+self.name, 1.0)]
                for t in self.tasks:
                    keywords+=t.getKeySpotting()
                text = self.rec.recognize_sphinx(audio,keyword_entries=keywords)
                return self.processText(text, use_name)
            except sr.UnknownValueError as e:
                print("can't understand, {0}".format(e))
            except sr.RequestError as e:
                print("request error, {0}".format(e))
        elif "google"==self.stt_engine:
            try:
                text = self.rec.recognize_google_cloud(audio,preferred_phrases=["hey "+self.name.lower()])
                return self.processText(text, use_name)
            except sr.UnknownValueError as e:
                print("can't understand, {0}".format(e))
            except sr.RequestError as e:
                print("request error {0}".format(e))
    def processText(self, text, use_name):
        if text:
            print("You: "+text,flush=True)
            res = self.searchKeywords(text.strip(), use_name=use_name)
            if res is None:
                print("Not understood: "+text)
            else:
                return self.tasks[res[0]].execute(res[1])

    def searchKeywords(self, input_string, use_name=False):
        idx = 0
        for kw in self.keywords:
            if use_name:
                kw = "hey "+self.name.lower()+" .*" + kw
            m = re.search(kw, input_string.lower())
            if m:
               return idx,m
            idx+=1

        return None
    
    def talk(self,text):
        if text:
            print(self.name+": " + text, flush=True)
            if "espeak"==self.tts_engine:
                speech = ss.init("espeak", True)
                speech.setProperty("voice", "en-rp+f4")
                speech.setProperty("rate", 140)
                speech.say(text)
                speech.runAndWait()
            elif "default"==self.tts_engine:
                self.tts.get_pronunciation(text)
            else:
                pass
    def checkPassive(self):
        try:
            response = self.sqs.receive_message(QueueUrl=self.sqsUrl,
                    WaitTimeSeconds=20, MaxNumberOfMessages=10)
            toSay = []
            for m in response.get("Messages", []):
                msg = m.get("Body")
                if msg:
                    self.sqs.delete_message(QueueUrl=self.sqsUrl,
                            ReceiptHandle=m.get("ReceiptHandle"))
                    toSay.append(msg)
            for s in toSay:
                self.talk(s)
        except:
            pass
    def addTask(self, task):
        self.tasks.append(task)
        self.keywords.append(task.getKeyword())
