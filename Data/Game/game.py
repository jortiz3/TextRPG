import os
import sys
import time
from json import JSONDecodeError
from os.path import exists

import jsonpickle

from PyQt5.QtWidgets import QApplication

from Data.Character.ability import Ability
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
        self._configPath = "game.json"
        self._itemFilePath = "Data/items.json"
        self._sceneFilePath = "Data/scenes.json"
        self._directory = 'Saves'
        self._fileExtension = "json"
        Ability.__getstate__ = Ability.getState
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
        self._ui.settingsMenu().connect(get_item_path=self.getItemFilePath, get_scene_path=self.getSceneFilePath,
                                        set_item_path=self.setItemFilePath, set_scene_path=self.setSceneFilePath)
        self._ui.show("main")
        self._loadConfig()

        sys.exit(self._app.exec())

    def deleteSave(self, save_index: int):
        filepath = self._saveFilepath(save_index)
        if not filepath:
            return
        os.remove(filepath)

    def getItemFilePath(self):
        return self._itemFilePath

    def getSceneFilePath(self):
        return self._sceneFilePath

    def __getstate__(self):
        return {"_player": self._player, "_sceneManager": self._sceneManager}

    def _loadConfig(self):
        if not exists(self._configPath):
            return
        with open(self._configPath, 'r') as file:
            config = file.read()
            if len(config) > 0:
                try:
                    config = jsonpickle.decode(config)
                    self._itemFilePath = config["itemPath"]
                    self._sceneFilePath = config["scenePath"]
                except JSONDecodeError:
                    self._ui.popup("Configuration Error", "Failed to load '{}'. The default values have been "
                                                          "loaded.".format(self._configPath))

    def loadGame(self, save_index: int):
        save_filepath = self._saveFilepath(save_index)
        if not save_filepath:
            return
        if not self._reset():
            return
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
        if not self._reset():
            return
        self._ui.show("new")

    def _reset(self):
        self._player.resetAttributes()
        try:
            ItemDatabase.initialize(self._itemFilePath)
            self._sceneManager.reset(self._sceneFilePath)
            self._saveConfig()
        except ValueError as ve:
            self._ui.popup("Settings Error", str(ve))
            return False
        return True

    def _saveConfig(self):
        config_object = {"itemPath": self._itemFilePath, "scenePath": self._sceneFilePath}
        config = jsonpickle.encode(config_object, indent=4)
        with open(self._configPath, 'w') as file:
            file.write(config)

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

    def setItemFilePath(self, value: str):
        self._itemFilePath = value

    def setSceneFilePath(self, value: str):
        self._sceneFilePath = value

    def __setstate__(self, state):
        self.__dict__.update(state)

    def startGame(self):
        self._ui.show("game")
