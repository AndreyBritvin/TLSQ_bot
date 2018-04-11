import json

class Read:
    def __init__(self,place):
        self.place = place
        self._name_variable = None

    def getVars(self,name):
        with open('config.json','r') as f:
            config = json.loads(f.read())
        self._name_variable = config.get(name)
        return self._name_variable

