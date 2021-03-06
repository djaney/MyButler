from BaseTask import BaseTask
from datetime import datetime
class Query(BaseTask):
    def getKeyword(self):
        return "(what is|whats|what's) (the time)"

    def execute(self, match):
        q = match.group(2)
        if 'the time'==q:
            return datetime.now().strftime("the time is %l %M %P")
        else:
            return "What is " + q
        return "Okay"
    def getKeySpotting(self):
        return [("what is the time", 1.0),("whats the time", 1.0)]
