from .BaseTask import BaseTask
import os
import webbrowser
import urllib
class Search(BaseTask):
    def getKeyword(self):
        return "(looking for|look for|what is|whats|search for|search) (a |an ){0,1}(.*)"

    def execute(self, match):
        q = match.group(3).strip()
        print("searing for: "+q)
        webbrowser.open('https://www.google.com/search?'+urllib.parse.urlencode({'q':q}))
        return "Searching for "+q
    def getKeySpotting(self):
        return []
