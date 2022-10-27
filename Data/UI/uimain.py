import os
import random

from PyQt5 import QtCore, QtGui, QtWidgets

from Data.UI.ui import UI


class UiMain(UI):
    __splash_dir = "Data/Images/Scene/"

    def __init__(self, window: QtWidgets.QMainWindow):
        super().__init__(window, window_name="MainWindow", window_show_size=QtCore.QSize(800, 600),
                         window_title="Text RPG - Main Menu")
        self._window.setFixedSize(QtCore.QSize(800, 600))
        self._centralWidget = QtWidgets.QWidget(window)
        self._mainSplash = QtWidgets.QLabel(self._centralWidget)
        self._mainSplash.setFrameStyle(QtWidgets.QFrame.Panel | QtWidgets.QFrame.Raised)
        self._mainSplash.setScaledContents(True)
        self._newGameButton = QtWidgets.QPushButton(self._centralWidget)
        self._newGameButton.setFixedSize(self._largeButtonSize)
        self._loadGameButton = QtWidgets.QPushButton(self._centralWidget)
        self._loadGameButton.setFixedSize(self._largeButtonSize)
        self._settingsButton = QtWidgets.QPushButton(self._centralWidget)
        self._settingsButton.setFixedSize(self._largeButtonSize)
        self._exitGameButton = QtWidgets.QPushButton(self._centralWidget)
        self._exitGameButton.setFixedSize(self._largeButtonSize)

        self._centralWidgetLayout = QtWidgets.QGridLayout(self._centralWidget)
        self._centralWidgetLayout.addWidget(self._mainSplash, 0, 0, 1, 3)
        self._centralWidgetLayout.addWidget(self._newGameButton, 2, 1, 1, 1)
        self._centralWidgetLayout.addWidget(self._loadGameButton, 3, 1, 1, 1)
        self._centralWidgetLayout.addWidget(self._settingsButton, 4, 1, 1, 1)
        self._centralWidgetLayout.addWidget(self._exitGameButton, 5, 1, 1, 1)
        self._centralWidget.setLayout(self._centralWidgetLayout)
        self._window.setCentralWidget(self._centralWidget)

        self._exitGameButton.clicked.connect(self._window.close)
        QtCore.QMetaObject.connectSlotsByName(self._window)

    def connect(self, goto_load=None, goto_mods=None, goto_new=None):
        if goto_load:
            self._loadGameButton.clicked.connect(goto_load)
        if goto_mods:
            self._settingsButton.clicked.connect(goto_mods)
        if goto_new:
            self._newGameButton.clicked.connect(goto_new)

    def randomSplash(self):
        files = os.listdir(self.__splash_dir)
        fileName = ""
        if files:
            fileName = files[random.randint(0, len(files) - 1)]
        path = "{}/{}".format(self.__splash_dir, fileName)
        return path

    def refresh(self):
        self._mainSplash.setPixmap(QtGui.QPixmap(self.randomSplash()))
        self._newGameButton.setText(self._translate(self._window_name, "New Game"))
        self._loadGameButton.setText(self._translate(self._window_name, "Load Game"))
        self._settingsButton.setText(self._translate(self._window_name, "Settings"))
        self._exitGameButton.setText(self._translate(self._window_name, "Exit Game"))
