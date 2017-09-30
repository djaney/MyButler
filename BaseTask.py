class BaseTask(object):
    def isConversation(self):
        return False
    def getKeyword(self):
        raise NotImplementedError("required")
    def execute(self):
        raise NotImplementedError("required")

    def getKeySpotting(self):
        return []
    
