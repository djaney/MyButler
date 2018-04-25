import speech_recognition as sr
import pyttsx3 as ss
import pyaudio

import os
import re
import boto3
import time
from tts.TextToSpeech import TextToSpeech
from ttspico import TtsEngine as Pico


class Butler:
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
    energy = 300
    __last_attention = 0
    attention_span = 5
    conservative = True

    def __init__(self):
        self.botoSess = boto3.Session(profile_name='mybutler')
        self.google_credentials = None
        self.sqsUrl = os.environ["SQS_URL"]
        self.sqsRegion = os.environ["SQS_REGION"]

    def init(self, adjust_noise=True, tts="espeak", stt="cmusphinx",
             push_to_talk=True, energy=300):
        # os.system("sphinx_jsgf2fsg -jsgf butler.jsgf > butler.fsg")
        self.rec = sr.Recognizer()
        self.mic = sr.Microphone(device_index=None)
        self.tts = TextToSpeech()
        self.tts_engine = tts
        self.stt_engine = stt
        self.push_to_talk = push_to_talk
        self.energy = energy
        self.sqs = self.botoSess.client("sqs")

        if 0 == self.energy:
            if adjust_noise:
                with self.mic as source:
                    self.rec.adjust_for_ambient_noise(source)
                    print("Energy: " + str(self.rec.energy_threshold))
        else:
            self.rec.dynamic_energy_threshold = False
            self.rec.energy_threshold = self.energy

    def is_attention(self):
        return False if self.get_time_since_last_attention() > self.attention_span else True

    def get_time_since_last_attention(self):
        return time.time() - self.__last_attention

    def set_google_credentials(self, cred):
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
        if audio:
            reply = self.think(audio, use_name=True)
            if reply:
                self.talk(reply)

    def speech_to_text(self, audio):
        text = ""
        if "cmusphinx" == self.stt_engine:
            try:
                keywords = [("hey " + self.name, 1.0)]
                for t in self.tasks:
                    keywords += t.getKeySpotting()
                text = self.rec.recognize_sphinx(audio, keyword_entries=keywords)
            except sr.UnknownValueError as e:
                print("can't understand, {0}".format(e))
            except sr.RequestError as e:
                print("request error, {0}".format(e))
        elif "google" == self.stt_engine:
            try:
                text = self.rec.recognize_google_cloud(audio, preferred_phrases=["hey " + self.name.lower()])
            except sr.UnknownValueError as e:
                print("--no action--".format(e))
            except sr.RequestError as e:
                print("request error {0}".format(e))
        else:
            print("invalid stt engine")
        return text

    def think(self, audio, silent_failure=False, use_name=False):
        text = ""
        # if you already got the attention, no need to say the name
        if self.is_attention():
            use_name = False
        # force to use sphynx for searching trigger keyword
        if use_name and "cmusphinx" != self.stt_engine and self.conservative:
            print("--conservative mode, using sphinx--", flush=True)
            try:
                keywords = [("hey " + self.name, 1.0)]
                text = self.rec.recognize_sphinx(audio, keyword_entries=keywords)
                print(text, flush=True)
                if text:
                    m = re.search("hey " + self.name, text)
                    if not m:
                        print("--not activated--", flush=True)
                        return
                    else:
                        print("--activated--", flush=True)
            except sr.UnknownValueError as e:
                print("--sphinx does not understand-- {0}".format(e), flush=True)
                return
            except sr.RequestError as e:
                print("--sphinx error-- {0}".format(e), flush=True)
                return
        else:
            print("--aggressive mode--", flush=True)

        print("--thinking--", flush=True)
        if "cmusphinx" == self.stt_engine:
            try:
                keywords = [("hey " + self.name, 1.0)]
                for t in self.tasks:
                    keywords += t.getKeySpotting()
                text = self.rec.recognize_sphinx(audio, keyword_entries=keywords)
                return self.process_text(text, use_name)
            except sr.UnknownValueError as e:
                print("can't understand, {0}".format(e))
            except sr.RequestError as e:
                print("request error, {0}".format(e))
        elif "google" == self.stt_engine:
            try:
                text = self.rec.recognize_google_cloud(audio, preferred_phrases=["hey " + self.name.lower()])
                return self.process_text(text, use_name)
            except sr.UnknownValueError as e:
                print("--no action--".format(e))
            except sr.RequestError as e:
                print("request error {0}".format(e))

    def process_text(self, text, use_name):
        if text:
            print("You: " + text, flush=True)
            res = self.search_keywords(text.strip(), use_name=use_name)
            if res is None:
                pass
            else:
                task = self.tasks[res[0]]
                if task.isConversation():
                    task.converse(self)
                    return
                else:
                    return task.execute(res[1])

    def search_keywords(self, input_string, use_name=False):
        idx = 0
        for kw in self.keywords:
            if use_name:
                kw = "hey " + self.name.lower() + " .*" + kw
            m = re.search(kw, input_string.lower())
            if m:
                return idx, m
            idx += 1

        return None

    def talk(self, text):
        if text:
            print(self.name + ": " + text, flush=True)
            if "espeak" == self.tts_engine:
                speech = ss.init("espeak", True)
                speech.setProperty("voice", "en-rp+f4")
                speech.setProperty("rate", 140)
                speech.say(text)
                speech.runAndWait()
                self.__last_attention = time.time()
            if "pico" == self.tts_engine:
                pico = Pico()
                pico.rate = 100
                pico.speak(text, self.__pico_callback)
            elif "default" == self.tts_engine:
                self.tts.get_pronunciation(text)
                self.__last_attention = time.time()
            else:
                pass

    def check_passive(self):
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

    def load_task(self, task):
        self.tasks.append(task)
        self.keywords.append(task.getKeyword())

    def load_package(self, package):
        for t in package.load():
            self.load_task(t)

    def __pico_callback(self, format, audio, fin):
        p = pyaudio.PyAudio()
        stream = p.open(rate=format[0],
                        format=pyaudio.paInt16,
                        channels=format[2],
                        output=True)
        stream.write(audio)
        stream.stop_stream()
        stream.close()
        p.terminate()
        if fin:
            self.__last_attention = time.time()
