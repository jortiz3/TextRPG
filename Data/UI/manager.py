from functools import partial

from PyQt5.QtWidgets import QMainWindow

from Data.UI.ui import UI
from Data.UI.uigame import UiGame
from Data.UI.uiload import UiLoad
from Data.UI.uimain import UiMain
from Data.UI.uinewgame import UiNewGame


class UiManager:
    __focus_window_names = ["game", "main", "new"]

    def __init__(self):
        self._game = UiGame(QMainWindow())
        self._load = UiLoad(QMainWindow())
        self._main = UiMain(QMainWindow())
        self._new = UiNewGame(QMainWindow())

        self._all: dict[str, UI] = {"game": self._game, "load": self._load, "main": self._main, "new": self._new}
        self._focus: UI = None

        self._game.connect(show_load=partial(self.show, "load"), show_main=partial(self.show, "main"))
        self._main.connect(goto_load=partial(self.show, "load"))
        self._new.connect(show_main=partial(self.show, "main"))

    def show(self, target_window_name="main"):
        """
        Shows the target window. If the target is a focus window, it will hide all others.
        :param target_window_name: The name of the ui window to go to.
        """
        if not self._all.keys().__contains__(target_window_name):
            target_window_name = "main"
        target_window: UI = self._all[target_window_name]

        if UiManager.__focus_window_names.__contains__(target_window_name):
            self._focus = target_window
            for ui in self._all.values():
                if ui:
                    ui.hide()

        target_window.refresh()
        target_window.show()

    # Properties

    def gameMenu(self):
        return self._game

    def loadMenu(self):
        return self._load

    def mainMenu(self):
        return self._main

    def newGameMenu(self):
        return self._new
