from Data.Scene.action import Action


class Scene:
    def __init__(self, name: str = "New Scene", description: str = "...",
                 imagePath: str = "", actions: list[Action] = []):
        self.actions: list[Action] = actions
        self._description = description
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

    def getAction(self, index: int):
        index = abs(index)
        if index < len(self.actions):
            return self.actions[index]
        return None

    def getState(self):
        """Override to be used conditionally for json pickling."""
        return {
            "actions": self.actions
        }

    def removeAction(self, index: int):
        index = abs(index)
        if index < len(self.actions):
            self.actions.pop(index)

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value: str):
        self._description = value

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
