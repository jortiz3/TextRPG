import os
import sys
import time

import jsons

from PyQt5.QtWidgets import QApplication

from Data.Scene.manager import SceneManager
from Data.Character.player import Player
from Data.Item.item_database import ItemDatabase
from Data.UI.manager import UiManager


class Game:
    __save_delimiter = "\n\n\n"
    __json_args = {"indent": 4, "sort_keys": True}

    def __init__(self):
        self._player: Player = Player()
        self._sceneManager = SceneManager(self._player)
        self._directory = 'Saves'
        self._fileExtension = "json"

        self._app = QApplication(sys.argv)
        self._ui = UiManager()
        self._ui.gameMenu().connect(get_area=self._sceneManager.current, get_area_description=self._sceneManager.areaDescription,
                                    player=self._player, save_game=self.saveGame, select_action=self.selectAction)
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

    def loadGame(self, save_index: int):
        save_filepath = self._saveFilepath(save_index)
        if not save_filepath:
            return

        with open(save_filepath, 'r') as save_file:
            save_data = save_file.read().split(Game.__save_delimiter)
            self._player.copyAttributes(jsons.loads(save_data[0], strip_privates=True, strip_properties=True))
            self._sceneManager.copyAttributes(jsons.loads(save_data[1], strip_privates=True, strip_properties=True))
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
        save_data = jsons.dumps(self._player, jdkwargs=Game.__json_args, strip_privates=True, strip_properties=True,
                                verbose=jsons.Verbosity.WITH_CLASS_INFO)
        save_data += Game.__save_delimiter
        save_data += jsons.dumps(self._sceneManager, jdkwargs=Game.__json_args, strip_privates=True, strip_properties=True,
                                 verbose=jsons.Verbosity.WITH_CLASS_INFO)
        with open(save_filepath, 'w') as save_file:
            save_file.write(save_data)

    def selectAction(self, index: int):
        nextMenu = self._sceneManager.selectAction(index)
        if nextMenu:
            self._ui.show(nextMenu)

    def startGame(self):
        self._ui.show("game")
