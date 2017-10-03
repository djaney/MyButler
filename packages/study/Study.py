from BaseTask import BaseTask
import os
import webbrowser
class Study(BaseTask):
    def getKeyword(self):
        return "open (google|chrome)"

    def isConversation(self):
        pass
    def converse(self, butler):
        pass
