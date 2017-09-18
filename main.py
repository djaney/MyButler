#!/usr/bin/env python3 

import os
import sys
import select
import speech_recognition as sr
import pyttsx3 as ss
import pyaudio
import atexit

from Butler import Butler
from tasks.Ping import Ping 
from tasks.OpenApps import OpenApps

def main():

    text = ""
    audio = None
    r = sr.Recognizer()

    butler = Butler()
    butler.addTask(Ping())
    butler.addTask(OpenApps())

    # if stdin has data and no audio yet
    if not audio and select.select([sys.stdin,],[],[],0.0)[0]:
        with os.fdopen(sys.stdin.fileno(), 'rb') as input_file:
            butler.init(adjust_noise=False)
            with sr.AudioFile(input_file) as source:
                audio = r.record(source)
                reply = butler.think(audio)
                butler.talk(reply)
    else:
        bulter.init()
        butler.ask()
 

if '__main__' == __name__ :
    main()

