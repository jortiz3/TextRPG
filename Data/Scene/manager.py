import jsons

from Data.Scene.scene import Scene
from Data.Character.player import Player


class SceneManager:
    __default_path = "Data/scenes.json"

    def __init__(self, player: Player):
        with open(self.__default_path, 'r') as scenes_file:
            self.__scenes: list[Scene] = jsons.loads(scenes_file.read())
        self.__player = player
        self.currentAreaIndex = 0
        self.previousAreaIndexes: list[int] = []  # TODO test this

    def areaDescription(self):
        """
        Retrieves the description text for the current area.
        :return:  The area description.
        """
        description = "{}\n\n".format(self.previous().exitDescription) if self.previous() else ""
        description += self.current().enterDescription if self.current() else ""
        return description

    def copyAttributes(self, other):
        if not isinstance(other, SceneManager):
            self.currentAreaIndex = 0
            self.previousAreaIndexes = 0
            return
        self.currentAreaIndex = other.currentAreaIndex
        self.previousAreaIndexes = other.previousAreaIndexes

    def current(self):
        """Retrieves the current area object."""
        if self.currentAreaIndex not in range(len(self.__scenes)):
            return None
        return self.__scenes[self.currentAreaIndex]

    def goto(self, index: int):
        """
        Jumps to a given area.
        :param index: The area index.
        """
        if index == self.currentAreaIndex:
            return None
        elif index == -1:
            temp_index = self.previousAreaIndexes[-1]
            self.previousAreaIndexes.pop()
            self.currentAreaIndex = temp_index
        elif index < len(self.__scenes):
            self.previousAreaIndexes.append(self.currentAreaIndex)
            self.currentAreaIndex = index

        if self.previous():
            self.current().setReturnAction("Return to {}".format(self.previous().name))
        return None

    def previous(self):
        """Retrieves the previous area."""
        if len(self.previousAreaIndexes) <= 0:
            return None
        if self.previousAreaIndexes[-1] not in range(
                len(self.__scenes)) or self.previousAreaIndexes[-1] == self.currentAreaIndex:
            return None
        return self.__scenes[self.previousAreaIndexes[-1]]

    def selectAction(self, index: int):
        """
        Selects a currently displayed action.
        :param index: The index of the action in the list.
        """
        if self.current():
            action = self.current().getAction(index)
            if action.requirementMet(self.__player) and action.select(self.__player):
                return self.goto(action.id)
        return None
