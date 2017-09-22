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
            return "I can't open "+app
        return "Okay"
    def getKeySpotting(self):
        return [("open google",1.0), ("open chrome", 1.0)]
