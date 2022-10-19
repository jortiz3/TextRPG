class Ability:
    def __init__(self, name: str = "", description: str = "", score: float = 1.0):
        self._name: str = name
        self._description: str = description
        self.score: float = score

    def __getstate__(self):
        return {"score": self.score}

    def __setstate__(self, state):
        self.__dict__.update(state)

    @property
    def description(self):
        return self._description

    @property
    def name(self):
        return self._name
