#!/usr/bin/env python3 

import os
import sys
import select
import speech_recognition as sr
import pyttsx3 as ss
import pyaudio
import atexit
import time

from Butler import Butler
from tasks.Ping import Ping
from tasks.OpenApps import OpenApps
from tasks.Query import Query

def main():

    text = ""
    audio = None
    use_espeak = True
    r = sr.Recognizer()

    butler = Butler()
    butler.addTask(Ping())
    butler.addTask(OpenApps())
    butler.addTask(Query())

    # if stdin has data and no audio yet
    if not audio and select.select([sys.stdin,],[],[],0.0)[0]:
        with os.fdopen(sys.stdin.fileno(), 'rb') as input_file:
            butler.init(adjust_noise=Falsei, espeak = use_espeak)
            with sr.AudioFile(input_file) as source:
                audio = r.record(source)
                reply = butler.think(audio)
                butler.talk(reply)
    else:
        butler.init(espeak = use_espeak)
        stop = butler.listen()
        print("ready to listen")

        while True:
            butler.checkPassive()
            time.sleep(60)
 

if '__main__' == __name__ :
    main()

