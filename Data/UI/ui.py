from abc import ABC, abstractmethod

from PyQt5 import QtCore, QtGui, QtWidgets


class UI(ABC):
    """
    Base class for all qt ui objects.
    """

    _defaultButtonSize = QtCore.QSize(100, 50)
    _defaultIconSize = QtCore.QSize(128, 128)
    _largeButtonSize = QtCore.QSize(200, 75)
    _largeIconSize = QtCore.QSize(256, 256)
    _smallButtonSize = QtCore.QSize(50, 25)
    _smallIconSize = QtCore.QSize(64, 64)
    _tinyButtonSize = QtCore.QSize(25, 25)

    _boldStyleSheet = "font: bold; font-size: 14pt;"
    _defaultStyleSheet = "font-size: 14pt;"
    _greenStyleSheet = "color: green; font: bold; font-size: 14pt;"

    def __init__(self, window: QtWidgets.QMainWindow, window_max_size=QtCore.QSize(2560, 1440),
                 window_min_size=QtCore.QSize(700, 500), window_name="MainWindow",
                 window_show_size: QtCore.QSize = None, window_title="Text RPG - Game"):
        self._checkIcon = QtGui.QIcon("Data/Images/UI/check.png")
        self._gearIcon = QtGui.QIcon("Data/Images/UI/gear.png")
        self._xIcon = QtGui.QIcon("Data/Images/UI/x.png")

        self._window: QtWidgets.QMainWindow = window
        self._window.setMaximumSize(window_max_size)
        self._window.setMinimumSize(window_min_size)
        self._window_name = window_name
        self._window_title = window_title
        self._window_show_size: QtCore.QSize = window_show_size

        self._window.setStyleSheet(self._defaultStyleSheet)
        self._window.setObjectName(self._window_name)

        self._translate = QtCore.QCoreApplication.translate
        self._window.setWindowTitle(self._translate(self._window_name, self._window_title))

        self._abilityNames = ["Dexterity", "Intelligence", "Strength", "Will", "Wisdom"]

    def hide(self):
        """ Hides the window. """
        self._window.hide()

    def _recenter(self):
        """ Moves the window to the center of the active screen. """
        frame = self._window.frameGeometry()
        screen = QtWidgets.QApplication.desktop().screenNumber(QtWidgets.QApplication.desktop().cursor().pos())
        center = QtWidgets.QApplication.desktop().screenGeometry(screen).center()
        frame.moveCenter(center)
        self._window.move(frame.topLeft())

    @abstractmethod
    def refresh(self) -> None:
        pass

    def reposition_window(self, x: int, y: int):
        """
        Repositions the window to the given screen coordinates.
        :param x: The screen horizontal coordinate.
        :param y: The screen vertical coordinate.
        """
        self._window.move(x, y)

    def resize_window(self, width: int, height: int):
        """
        Resizes the window to the given width and height.
        :param width: The horizontal size of the window in pixels.
        :param height: The vertical size of the window in pixels.
        """
        self._window.resize(width, height)

    def show(self):
        """ Shows the window. """
        if self._window_show_size:
            self._window.resize(self._window_show_size)
            self._recenter()
        self._window.show()
        self._window.raise_()
        self._window.activateWindow()

    def snapTo(self, other: QtWidgets.QMainWindow, side: str = "right"):
        """"""
        x = other.x()
        y = other.y()
        if side == "left":
            x -= self._window.width()
        elif side == "right":
            x += other.width()
        elif side == "top":
            y -= self._window.height()
        else:
            y += other.height()
        self.reposition_window(x, y)

    @property
    def window(self):
        """ Returns the window object. """
        return self._window
