from Data.Scene.action import Action


class Scene:
    def __init__(self, name: str = "", enterDescription: str = "", exitDescription: str = "", imagePath: str = "",
                 actions: list[Action] = [], id: int = 0):
        self.actions: list[Action] = actions
        self._enterDescription = enterDescription
        self._exitDescription = exitDescription
        self.id = id
        self._imagePath = imagePath
        self._name = name

    def copyActions(self, other):
        if not isinstance(other, Scene):
            return
        if len(self.actions) != len(other.actions):
            return
        for index, action in enumerate(self.actions):
            action.enabled = other.actions[index].enabled
            action.removed = other.actions[index].removed
            action.selected = other.actions[index].selected

    def __eq__(self, other):
        if not isinstance(other, Scene):
            return False
        return self.id == other.id

    def getAction(self, index: int):
        index = abs(index)
        if index < len(self.actions):
            return self.actions[index]
        return None

    def removeAction(self, index: int):
        index = abs(index)
        if index < len(self.actions):
            self.actions.pop(index)

    def setReturnAction(self, description: str):
        if len(self.actions) > 0 and self.actions[-1].id == -1:
            self.actions[-1].description = description
            return

    @property
    def enterDescription(self):
        return self._enterDescription

    @enterDescription.setter
    def enterDescription(self, value: str):
        self._enterDescription = value

    @property
    def exitDescription(self):
        return self._exitDescription

    @exitDescription.setter
    def exitDescription(self, value: str):
        self._exitDescription = value

    @property
    def imagePath(self):
        return self._imagePath

    @imagePath.setter
    def imagePath(self, value: str):
        self._imagePath = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value
