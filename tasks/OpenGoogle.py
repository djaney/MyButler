from .BaseTask import BaseTask
import os
import webbrowser
class OpenGoogle(BaseTask):
    def getKeyword(self):
        return "google"

    def execute(self):
        webbrowser.open('https://www.google.com')
        return "Opening google for you"

