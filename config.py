import json


class Read:
    def __init__(self, place):
        self.place = place
        self._name_variable = None
        self._name_dict = None
        with open(self.place, 'r') as f:
            self.config = json.loads(f.read())

    def getVars(self, name):
        self._name_variable = self.config.get(name)
        return self._name_variable

    def getDict(self):
        self._name_dict = self.config
        return self._name_dict
