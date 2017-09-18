from .BaseTask import BaseTask
import os
import webbrowser
class OpenApps(BaseTask):
    def getKeyword(self):
        return "open (google|chrome)"

    def execute(self, match):
        app = match.group(1)
        if 'google'==app:
            webbrowser.open('https://www.google.com')
        elif 'chrome':
            webbrowser.open('https://www.google.com')
        else:
            return "I can'y open "+app
        return "Okay"

