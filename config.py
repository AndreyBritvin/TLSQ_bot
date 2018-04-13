import json


class Read:
    def __init__(self, place):
        self.place = place
        self._name_variable = None
        with open(self.place, 'r') as f:
            self.config = json.loads(f.read())

    def getVars(self, name):
        self._name_variable = self.config.get(name)
        return self._name_variable

