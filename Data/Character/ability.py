class Ability:
    def __init__(self, name: str = "", description: str = "", score: float = 1.0):
        self._name: str = name
        self._description: str = description
        self.score: float = score

    def getState(self):
        return {
            "score": self.score
        }

    @property
    def description(self):
        return self._description

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value
