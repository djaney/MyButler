from .BaseTask import BaseTask
class Ping(BaseTask):
    def getKeyword(self):
        return "hello"

    def execute(self, match):
        return "hi!"

    def getKeySpotting(self):
        return [("hello",1.0)]

