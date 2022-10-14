import jsons

from Data.Scene.scene import Scene
from Data.Character.player import Player


class SceneManager:
    __default_path = "Data/scenes.json"

    def __init__(self, player: Player):
        with open(self.__default_path, 'r') as scenes_file:
            self.__scenes: list[Scene] = jsons.loads(scenes_file.read())
        self.__player = player
        self.currentSceneIndex = 0
        self.previousSceneIndexes: list[int] = []

    def sceneDescription(self):
        """
        Retrieves the description text for the current scene.
        :return:  The scene description.
        """
        description = "{}\n\n".format(self.previous().exitDescription) if self.previous() else ""
        description += self.current().enterDescription if self.current() else ""
        return description

    def copyAttributes(self, other):
        if not isinstance(other, SceneManager):
            self.currentSceneIndex = 0
            self.previousSceneIndexes = 0
            return
        self.currentSceneIndex = other.currentSceneIndex
        self.previousSceneIndexes = other.previousSceneIndexes

    def current(self):
        """Retrieves the current scene object."""
        if self.currentSceneIndex not in range(len(self.__scenes)):
            return None
        return self.__scenes[self.currentSceneIndex]

    def goto(self, index: int):
        """
        Jumps to a given scene.
        :param index: The scene index.
        """
        if index == self.currentSceneIndex:
            return None
        elif index == -1:
            temp_index = self.previousSceneIndexes[-1]
            self.previousSceneIndexes.pop()
            self.currentSceneIndex = temp_index
        elif index < len(self.__scenes):
            self.previousSceneIndexes.append(self.currentSceneIndex)
            self.currentSceneIndex = index

        if self.previous():
            self.current().setReturnAction("Return to {}".format(self.previous().name))
        return None

    def previous(self):
        """Retrieves the previous scene."""
        if len(self.previousSceneIndexes) <= 0:
            return None
        if self.previousSceneIndexes[-1] not in range(
                len(self.__scenes)) or self.previousSceneIndexes[-1] == self.currentSceneIndex:
            return None
        return self.__scenes[self.previousSceneIndexes[-1]]

    def reset(self):
        self.currentSceneIndex = 0
        self.previousSceneIndexes = []

    def selectAction(self, index: int):
        """
        Selects a currently displayed action.
        :param index: The index of the action in the list.
        """
        if self.current():
            action = self.current().getAction(index)
            if action.requirementMet(self.__player) and action.select(self.__player):
                return self.goto(action.id())
        return None
