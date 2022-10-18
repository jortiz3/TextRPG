class Ability:
    def __init__(self, name: str, description: str = "", score: float = 1.0):
        self.name: str = name
        self.description: str = description
        self.score: float = score
