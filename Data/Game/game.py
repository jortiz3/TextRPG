import os
import sys
import time

import jsonpickle

from PyQt5.QtWidgets import QApplication

from Data.Scene.action import Action
from Data.Scene.manager import SceneManager
from Data.Character.player import Player
from Data.Item.item_database import ItemDatabase
from Data.Scene.scene import Scene
from Data.UI.manager import UiManager


class Game:
    def __init__(self):
        self._player: Player = Player()
        self._sceneManager = SceneManager(self._player)
        self._directory = 'Saves'
        self._fileExtension = "json"
        Action.__getstate__ = Action.getState
        Scene.__getstate__ = Scene.getState

        self._app = QApplication(sys.argv)
        self._ui = UiManager()
        self._ui.gameMenu().connect(get_scene=self._sceneManager.current,
                                    get_scene_description=self._sceneManager.sceneDescription, player=self._player,
                                    save_game=self.saveGame, select_action=self.selectAction)
        self._ui.loadMenu().connect(delete_save=self.deleteSave, load_save=self.loadGame, load_info=self.loadInfo)
        self._ui.mainMenu().connect(goto_new=self.newGame)
        self._ui.newGameMenu().connect(player=self._player, start_game=self.startGame)
        self._ui.show("main")

        ItemDatabase.initialize()

        sys.exit(self._app.exec())

    def deleteSave(self, save_index: int):
        filepath = self._saveFilepath(save_index)
        if not filepath:
            return
        os.remove(filepath)

    def __getstate__(self):
        return {
            "_player": self._player,
            "_sceneManager": self._sceneManager
        }

    def loadGame(self, save_index: int):
        save_filepath = self._saveFilepath(save_index)
        if not save_filepath:
            return
        self._sceneManager.reset()
        with open(save_filepath, 'r') as save_file:
            save_data = jsonpickle.decode(save_file.read())
            self._player.copyAttributes(save_data._player)
            self._sceneManager.copyAttributes(save_data._sceneManager)
        self._ui.show("game")

    def loadInfo(self):
        info = None
        files = os.listdir(self._directory)
        if files:
            info: list[str] = []
            for filename in files:
                filepath = "{}/{}".format(self._directory, filename)
                mod_time = time.strftime('%I:%M%p %m/%d/%Y', time.localtime(os.path.getmtime(filepath)))
                info.append("{}\n{}".format(filename, mod_time))
        return info

    def newGame(self):
        self._player.resetAttributes()
        self._sceneManager.reset()
        self._ui.show("new")

    def _saveFilepath(self, file_index: int):
        files = os.listdir(self._directory)
        if not files or file_index >= len(files):
            return None
        filename = files[file_index]
        return "{}/{}".format(self._directory, filename)

    def saveGame(self):
        if not self._player:
            return

        save_filepath = "{}/{}.{}".format(self._directory, self._player.name, self._fileExtension)
        with open(save_filepath, 'w') as save_file:
            save_file.write(jsonpickle.encode(self, indent=4))

    def selectAction(self, index: int):
        nextMenu = self._sceneManager.selectAction(index)
        if nextMenu:
            self._ui.show(nextMenu)

    def __setstate__(self, state):
        self.__dict__.update(state)

    def startGame(self):
        self._ui.show("game")
