#!/usr/bin/env python3 
from optparse import OptionParser
import os
import sys
import select
import speech_recognition as sr
import time

from Butler import Butler
from packages.computer import loader as PackageComputer
from packages.chrome import loader as PackageChrome
from packages.ask import loader as PackageAsk


def main():
    parser = OptionParser(description='Welcome to my butler')
    parser.add_option("-t", "--tts", type=str, default="espeak", help='Text to speech engine to use. espeak, pico')
    parser.add_option("-s", "--stt", type=str, default="cmusphinx", help='Speech to text engine. cmusphinx, google')
    parser.add_option("-p", "--pushtotalk", default=True, help='Push to talk')
    parser.add_option("-e", "--energy", default=700, type=int, help='Energy required to activate talk')
    parser.add_option("-a", "--aggressive", default=False, action="store_true",
                      help='if not aggressive, it will use sphinx for detecting activation')

    args = parser.parse_args()
    options = args[0]

    text = ""
    audio = None
    tts = options.tts
    stt = options.stt
    pushtotalk = options.pushtotalk
    energy = options.energy
    r = sr.Recognizer()

    butler = Butler()
    butler.conservative = not options.aggressive
    butler.load_package(PackageComputer)
    butler.load_package(PackageChrome)
    butler.load_package(PackageAsk)

    # if stdin has data and no audio yet
    if not audio and select.select([sys.stdin, ], [], [], 0.0)[0]:
        with os.fdopen(sys.stdin.fileno(), 'rb') as input_file:
            butler.init(adjust_noise=False, tts=tts, stt=stt,
                        push_to_talk=pushtotalk, energy=energy)
            with sr.AudioFile(input_file) as source:
                audio = r.record(source)
                reply = butler.think(audio)
                butler.talk(reply)
    else:
        butler.init(tts=tts, stt=stt,
                    push_to_talk=pushtotalk, energy=energy)
        stop = butler.listen()
        print("ready to listen")

        while True:
            butler.check_passive()
            time.sleep(1)


if '__main__' == __name__:
    main()
