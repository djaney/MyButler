from .BaseTask import BaseTask
class Ifttt(BaseTask):
    def getKeyword(self):
        return "turn on lights"

    def execute(self, match):
        app = match.group(1)
        if 'google'==app:
            pass
        elif 'chrome':
            pass
        else:
            pass
        return "Okay"

