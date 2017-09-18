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
from tasks.OpenGoogle import OpenGoogle

def main():

    text = ""
    audio = None
    r = sr.Recognizer()

    # if stdin has data and no audio yet
    if not audio and select.select([sys.stdin,],[],[],0.0)[0]:
        with os.fdopen(sys.stdin.fileno(), 'rb') as input_file:
            with sr.AudioFile(input_file) as source:
                audio = r.record(source)
                reply = think(audio)
                talk(reply)

    butler = Butler()
    butler.addTask(Ping())
    butler.addTask(OpenGoogle())

    butler.init()
    butler.ask()
 

if '__main__' == __name__ :
    main()

