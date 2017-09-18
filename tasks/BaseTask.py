class BaseTask(object):
    
    def getKeyword(self):
        raise NotImplementedError("required")
    def execute(self):
        raise NotImplementedError("required")
    
