import jsonpickle

from Data.Scene.scene import Scene
from Data.Character.player import Player


class SceneManager:
    __default_path = "Data/scenes.json"

    def __init__(self, player: Player = Player()):
        self.scenes = self._loadScenes()
        self.__player = player
        self.currentSceneIndex = 0
        self.previousSceneIndexes: list[int] = []
        self.currentConsequence = ""

    def copyAttributes(self, other):
        if not isinstance(other, SceneManager):
            self.currentSceneIndex = 0
            self.previousSceneIndexes = 0
            self.currentConsequence = ""
            return
        self.currentSceneIndex = other.currentSceneIndex
        self.previousSceneIndexes = other.previousSceneIndexes
        self.currentConsequence = other.currentConsequence
        if len(self.scenes) != len(other.scenes):
            return
        for index, scene in enumerate(self.scenes):
            scene.copyActions(other.scenes[index])

    def current(self):
        """Retrieves the current scene object."""
        if self.currentSceneIndex not in range(len(self.scenes)):
            return None
        return self.scenes[self.currentSceneIndex]

    def __getstate__(self):
        return {
            "scenes": self.scenes,
            "currentConsequence": self.currentConsequence,
            "currentSceneIndex": self.currentSceneIndex,
            "previousSceneIndexes": self.previousSceneIndexes
        }

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
        elif index < len(self.scenes):
            self.previousSceneIndexes.append(self.currentSceneIndex)
            self.currentSceneIndex = index
        return None

    def _loadScenes(self):
        with open(self.__default_path, 'r') as scenes_file:
            return jsonpickle.decode(scenes_file.read())

    def previous(self):
        """Retrieves the previous scene."""
        if len(self.previousSceneIndexes) <= 0:
            return None
        if self.previousSceneIndexes[-1] not in range(
                len(self.scenes)) or self.previousSceneIndexes[-1] == self.currentSceneIndex:
            return None
        return self.scenes[self.previousSceneIndexes[-1]]

    def reset(self):
        self.currentSceneIndex = 0
        self.previousSceneIndexes = []
        self.scenes = self._loadScenes()

    def sceneDescription(self):
        """
        Retrieves the description text for the current scene.
        :return:  The scene description.
        """
        description = ""
        if len(self.currentConsequence) > 0:
            description += "{}\n\n".format(self.currentConsequence)
        description += self.current().enterDescription if self.current() else ""
        return description

    def __setstate__(self, state):
        self.__dict__.update(state)

    def selectAction(self, index: int):
        """
        Selects a currently displayed action.
        :param index: The index of the action in the list.
        """
        if self.current():
            action = self.current().getAction(index)
            if action.requirementMet(self.__player) and action.select(self.__player):
                self.currentConsequence = action.consequence
                return self.goto(action.id)
        return None
