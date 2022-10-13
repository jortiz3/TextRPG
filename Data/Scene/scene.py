from Data.Scene.action import Action


class Scene:
    def __init__(self, name: str = "", enterDescription: str = "", exitDescription: str = "", imagePath: str = "",
                 actions: list[Action] = []):
        self.actions: list[Action] = actions
        self.enterDescription = enterDescription
        self.exitDescription = exitDescription
        self.imagePath = imagePath
        self.name = name

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
