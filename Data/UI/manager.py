from functools import partial

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow

from Data.UI.ui import UI
from Data.UI.uigame import UiGame
from Data.UI.uihelp import UiHelp
from Data.UI.uiload import UiLoad
from Data.UI.uimain import UiMain
from Data.UI.uinewgame import UiNewGame
from Data.UI.uisettings import UiSettings


class UiManager:
    __focus_window_names = ["game", "main", "new"]

    def __init__(self):
        self._game = UiGame(QMainWindow())
        self._help = UiHelp(QMainWindow())
        self._load = UiLoad(QMainWindow())
        self._main = UiMain(QMainWindow())
        self._new = UiNewGame(QMainWindow())
        self._settings = UiSettings(QMainWindow())

        self._all: dict[str, UI] = {"game": self._game, "help": self._help, "load": self._load, "main": self._main,
                                    "new": self._new, "settings": self._settings}
        self._focus: UI = None

        self._game.connect(show_help=partial(self.show, "help"), show_load=partial(self.show, "load"),
                           show_main=partial(self.show, "main"))
        self._main.connect(goto_load=partial(self.show, "load"), goto_mods=partial(self.show, "settings"))
        self._new.connect(show_main=partial(self.show, "main"))

    def popup(self, title: str, message: str):
        icon = QtWidgets.QMessageBox.Warning
        buttons = QtWidgets.QMessageBox.Ok
        messageBox = QtWidgets.QMessageBox(icon, title, message, buttons, self._focus.window)
        messageBox.accepted.connect(messageBox.close)
        messageBox.exec()

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

    def settingsMenu(self):
        return self._settings
