from functools import partial

from PyQt5 import QtCore, QtGui, QtWidgets

from Data.UI.inventory_model import InventoryModel
from Data.UI.ui import UI


class UiGame(UI):  # TODO scroll area for area description
    def __init__(self, window: QtWidgets.QMainWindow):
        super().__init__(window, window_name="GameWindow", window_show_size=QtCore.QSize(800, 600),
                         window_title="Text RPG - Exploring the World")
        self._centralWidget = QtWidgets.QWidget(self._window)
        self._centralWidget.setObjectName("centralWidget")

        self._areaGroupBox = QtWidgets.QGroupBox(self._centralWidget)
        self._areaGroupBox.setMinimumSize(QtCore.QSize(400, 200))
        self._areaGroupBox.setObjectName("areaGroupBox")
        self._areaDescriptionLabel = QtWidgets.QLabel(self._areaGroupBox)
        self._areaDescriptionLabel.setObjectName("areaDescriptionLabel")
        self._areaDescriptionLabel.setWordWrap(True)
        self._areaImage = QtWidgets.QLabel(self._areaGroupBox)
        self._areaImage.setFixedSize(self._defaultIconSize)
        self._areaImage.setScaledContents(True)
        self._areaImage.setFrameStyle(QtWidgets.QFrame.Panel | QtWidgets.QFrame.Raised)

        self._areaGroupBoxLayout = QtWidgets.QGridLayout(self._areaGroupBox)
        self._areaGroupBoxLayout.addWidget(self._areaDescriptionLabel, 0, 0, 1, 1)
        self._areaGroupBoxLayout.addWidget(self._areaImage, 0, 1, 1, 1)
        self._areaGroupBox.setLayout(self._areaGroupBoxLayout)

        self._areaActionsGroupBox = QtWidgets.QGroupBox(self._centralWidget)
        self._areaActionsGroupBox.setObjectName("areaActionsGroupBox")
        self._areaActionsScrollArea = QtWidgets.QScrollArea(self._areaActionsGroupBox)
        self._areaActionsScrollArea.setFrameShape(QtWidgets.QFrame.NoFrame)
        self._areaActionsScrollArea.setWidgetResizable(True)
        self._areaActionsScrollArea.setObjectName("areaActionsScrollArea")
        self._areaActionsScrollAreaContent = QtWidgets.QWidget()
        self._areaActionsScrollAreaContent.setObjectName("areaActionsScrollAreaContent")
        self._areaActionsScrollAreaLayout = QtWidgets.QGridLayout(self._areaActionsScrollAreaContent)
        self._areaActionsScrollAreaLayout.setObjectName("scrollAreaLayout")
        self._areaActionButtons: list[QtWidgets.QPushButton] = []
        for index in range(15):
            button = QtWidgets.QPushButton(self._areaActionsScrollAreaContent)
            button.setObjectName("areaActionButton{}".format(index))
            button.setMinimumSize(self._defaultButtonSize)
            self._areaActionsScrollAreaLayout.addWidget(button, index, 0, 1, 1)
            self._areaActionButtons.append(button)
        self._areaActionsScrollArea.setWidget(self._areaActionsScrollAreaContent)
        self._areaActionsLayout = QtWidgets.QGridLayout(self._areaActionsGroupBox)
        self._areaActionsLayout.setObjectName("areaActionsHorizontalLayout")
        self._areaActionsLayout.addWidget(self._areaActionsScrollArea, 0, 0)

        self._playerInfoGroupBox = QtWidgets.QGroupBox(self._centralWidget)
        self._playerInfoGroupBox.setMinimumSize(QtCore.QSize(200, 200))
        self._playerInfoGroupBox.setObjectName("playerInfoGroupBox")
        self._playerInfoTabs = QtWidgets.QTabWidget(self._playerInfoGroupBox)

        characterTab = QtWidgets.QWidget(self._playerInfoTabs)
        self._levelLabel = QtWidgets.QLabel(characterTab)
        self._expLabel = QtWidgets.QLabel(characterTab)
        self._powerLabel = QtWidgets.QLabel(characterTab)
        self._craftBonusLabel = QtWidgets.QLabel(characterTab)
        self._enchantBonusLabel = QtWidgets.QLabel(characterTab)
        self._dodgeLabel = QtWidgets.QLabel(characterTab)
        self._runLabel = QtWidgets.QLabel(characterTab)
        self._abilityPointsLabel = QtWidgets.QLabel(characterTab)
        characterTabLayout = QtWidgets.QGridLayout(self._playerInfoTabs)
        characterTabLayout.addWidget(self._levelLabel, 0, 0, 1, 1)
        characterTabLayout.addWidget(self._expLabel, 0, 1, 1, 1)
        characterTabLayout.addWidget(self._powerLabel, 1, 1, 1, 1)
        characterTabLayout.addWidget(self._abilityPointsLabel, 1, 0, 1, 1)
        self._labelFormat = "{}Label"
        self._scoreFormat = "{}ScoreLabel"
        self._incrementFormat = "{}IncrementButton"
        self._abilityWidgets: dict[str, QtWidgets.QWidget] = {}
        for abilityIndex, abilityName in enumerate(self._abilityNames):
            row = abilityIndex + 3
            abilityLabel = QtWidgets.QLabel(characterTab)
            abilityLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)
            abilityLabelKey = self._labelFormat.format(abilityName)
            abilityLabel.setObjectName(abilityLabelKey)
            self._abilityWidgets[abilityLabelKey] = abilityLabel

            abilityScoreLabel = QtWidgets.QLabel(characterTab)
            abilityScoreLabel.setAlignment(QtCore.Qt.AlignVCenter)
            abilityScoreLabel.setStyleSheet(self._boldStyleSheet)
            abilityScoreLabelKey = self._scoreFormat.format(abilityName)
            abilityScoreLabel.setObjectName(abilityScoreLabelKey)
            self._abilityWidgets[abilityScoreLabelKey] = abilityScoreLabel

            incrementButton = QtWidgets.QPushButton(characterTab)
            incrementButtonKey = self._incrementFormat.format(abilityName)
            incrementButton.setObjectName(incrementButtonKey)
            incrementButton.setFixedSize(self._tinyButtonSize)
            self._abilityWidgets[incrementButtonKey] = incrementButton

            characterTabLayout.addWidget(abilityLabel, row, 0, 1, 1)
            characterTabLayout.addWidget(abilityScoreLabel, row, 1, 1, 1)
            characterTabLayout.addWidget(incrementButton, row, 2, 1, 1)

        characterTabLayout.addWidget(self._craftBonusLabel, 9, 0, 1, 1)
        characterTabLayout.addWidget(self._enchantBonusLabel, 9, 1, 1, 1)
        characterTabLayout.addWidget(self._dodgeLabel, 10, 0, 1, 1)
        characterTabLayout.addWidget(self._runLabel, 10, 1, 1, 1)
        characterTab.setLayout(characterTabLayout)

        self._inventoryTable = QtWidgets.QTableView(self._playerInfoTabs)
        self._inventoryTable.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self._inventoryTable.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        self._playerInfoTabs.addTab(characterTab, "Stats")
        self._playerInfoTabs.addTab(self._inventoryTable, "Inventory")
        playerInfoLayout = QtWidgets.QVBoxLayout(self._playerInfoGroupBox)
        playerInfoLayout.addWidget(self._playerInfoTabs)
        self._playerInfoGroupBox.setLayout(playerInfoLayout)

        self._mainGridLayout = QtWidgets.QGridLayout(self._centralWidget)
        self._mainGridLayout.setObjectName("gridLayout")
        self._mainGridLayout.addWidget(self._areaGroupBox, 0, 0, 1, 2)
        self._mainGridLayout.addWidget(self._areaActionsGroupBox, 1, 0, 1, 1)
        self._mainGridLayout.addWidget(self._playerInfoGroupBox, 1, 1, 1, 1)
        self._centralWidget.setLayout(self._mainGridLayout)
        self._window.setCentralWidget(self._centralWidget)

        self._menubar = QtWidgets.QMenuBar(self._window)
        self._menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self._menubar.setObjectName("menubar")
        self._menuFile = QtWidgets.QMenu(self._menubar)
        self._menuFile.setObjectName("menuFile")
        self._menuWindow = QtWidgets.QMenu(self._menubar)
        self._menuWindow.setObjectName("menuWindow")
        self._menuPosition = QtWidgets.QMenu(self._menuWindow)
        self._menuPosition.setObjectName("menuPosition")
        self._menuResize = QtWidgets.QMenu(self._menuWindow)
        self._menuResize.setObjectName("menuResize")
        self._window.setMenuBar(self._menubar)
        self._action_0_0 = QtWidgets.QAction(self._window)
        self._action_0_0.setShortcutVisibleInContextMenu(False)
        self._action_0_0.setObjectName("action_0_0")
        self._action_100_100 = QtWidgets.QAction(self._window)
        self._action_100_100.setShortcutVisibleInContextMenu(False)
        self._action_100_100.setObjectName("action_100_100")
        self._action_500_500 = QtWidgets.QAction(self._window)
        self._action_500_500.setShortcutVisibleInContextMenu(False)
        self._action_500_500.setObjectName("action_500_500")
        self._action_800x600 = QtWidgets.QAction(self._window)
        self._action_800x600.setShortcutVisibleInContextMenu(False)
        self._action_800x600.setObjectName("action_800x600")
        self._action_1280x900 = QtWidgets.QAction(self._window)
        self._action_1280x900.setShortcutVisibleInContextMenu(False)
        self._action_1280x900.setObjectName("action_1280x900")
        self._action_1920x1080 = QtWidgets.QAction(self._window)
        self._action_1920x1080.setShortcutVisibleInContextMenu(False)
        self._action_1920x1080.setObjectName("action_1920x1080")
        self._action_2560x1440 = QtWidgets.QAction(self._window)
        self._action_2560x1440.setShortcutVisibleInContextMenu(False)
        self._action_2560x1440.setObjectName("action_2560x1440")
        self._actionLoad = QtWidgets.QAction(self._window)
        self._actionLoad.setObjectName("actionLoad")
        self._actionSave = QtWidgets.QAction(self._window)
        self._actionSave.setObjectName("actionSave")
        self._actionQuit = QtWidgets.QAction(self._window)
        self._actionQuit.setObjectName("actionQuit")

        self._menuFile.addAction(self._actionSave)
        self._menuFile.addAction(self._actionLoad)
        self._menuFile.addAction(self._actionQuit)
        self._menuPosition.addAction(self._action_0_0)
        self._menuPosition.addAction(self._action_100_100)
        self._menuPosition.addAction(self._action_500_500)
        self._menuResize.addAction(self._action_800x600)
        self._menuResize.addAction(self._action_1280x900)
        self._menuResize.addAction(self._action_1920x1080)
        self._menuResize.addAction(self._action_2560x1440)
        self._menuWindow.addAction(self._menuResize.menuAction())
        self._menuWindow.addAction(self._menuPosition.menuAction())
        self._menubar.addAction(self._menuFile.menuAction())
        self._menubar.addAction(self._menuWindow.menuAction())

        self._getScene = None
        self._getAreaDescription = None
        self._player = None
        self._action_0_0.triggered.connect(partial(self.reposition_window, 0, 0))
        self._action_100_100.triggered.connect(partial(self.reposition_window, 100, 100))  # TODO 100 & 500 -> recenter
        self._action_500_500.triggered.connect(partial(self.reposition_window, 500, 500))
        self._action_800x600.triggered.connect(partial(self.resize_window, 800, 600))
        self._action_1280x900.triggered.connect(partial(self.resize_window, 1280, 900))
        self._action_1920x1080.triggered.connect(partial(self.resize_window, 1920, 1080))
        self._action_2560x1440.triggered.connect(partial(self.resize_window, 2560, 1440))
        QtCore.QMetaObject.connectSlotsByName(self._window)

    def connect(self, get_area=None, get_area_description=None, player=None, save_game=None, select_action=None,
                show_load=None, show_main=None):
        if get_area:
            self._getScene = get_area
        if get_area_description:
            self._getAreaDescription = get_area_description
        if player:
            self._player = player
            self._inventoryTable.setModel(InventoryModel(player))
            for abilityName in self._abilityNames:
                incrementButton = self._abilityWidgets[self._incrementFormat.format(abilityName)]
                incrementButton.clicked.connect(partial(player.modifyAbilityScore, abilityName, 1))
                incrementButton.clicked.connect(self.refresh)
        if save_game:
            self._actionSave.triggered.connect(save_game)
        if select_action:
            for index in range(len(self._areaActionButtons)):
                area_action_button = self._areaActionButtons[index]
                area_action_button.clicked.connect(partial(select_action, index))
                area_action_button.clicked.connect(self.refresh)
        if show_load:
            self._actionLoad.triggered.connect(show_load)
        if show_main:
            self._actionQuit.triggered.connect(show_main)

    def refresh(self):
        self._window.setWindowTitle(self._translate(self._window_name, self._window_title))

        scene = None
        scene_name = ""
        if self._getScene:
            scene = self._getScene()
            scene_name = scene.name
            self._areaImage.setPixmap(QtGui.QPixmap(scene.imagePath))
        self._areaGroupBox.setTitle(self._translate(self._window_name, scene_name))

        area_description = ""
        if self._getAreaDescription:
            area_description = self._getAreaDescription()
        self._areaDescriptionLabel.setText(self._translate(self._window_name, area_description))
        self._areaActionsGroupBox.setTitle(self._translate(self._window_name, "Scene Actions"))

        for index, action_button in enumerate(self._areaActionButtons):
            if scene:
                action = scene.getAction(index)
                if action:
                    if not action.removed:
                        icon = QtGui.QIcon()
                        if action.selected:
                            icon = self._checkIcon
                        elif not action.requirementMet(self._player):
                            icon = self._xIcon
                        action_button.setIcon(icon)
                        action_button.setEnabled(action.enabled)
                        action_button.setText(self._translate(self._window_name, action.description))
                        action_button.show()
                        continue
            action_button.hide()

        playerInfoGroupBoxTitle = "Player Info"
        if self._player:
            playerInfoGroupBoxTitle = self._player.name
        self._playerInfoGroupBox.setTitle(self._translate(self._window_name, playerInfoGroupBoxTitle))

        levelText = "LVL: {}"
        expText = "EXP: {} / {}"
        powerText = "POWER: {}"
        craftBonusText = "CRAFT: {}"
        enchantBonusText = "ENCH: {}"
        dodgeText = "DODGE: {}"
        runText = "RUN: {}"
        if self._player:
            levelText = levelText.format(self._player.level)
            expText = expText.format(self._player.experience, self._player.requiredExperience())
            dodgeText = dodgeText.format(self._player.dodgeBonus())
            runText = runText.format(self._player.runBonus())
            powerText = powerText.format(self._player.powerLevel())
            craftBonusText = craftBonusText.format(self._player.craftingBonus())
            enchantBonusText = enchantBonusText.format(self._player.enchantingBonus())
        self._levelLabel.setText(self._translate(self._window_name, levelText))
        self._expLabel.setText(self._translate(self._window_name, expText))
        self._powerLabel.setText(self._translate(self._window_name, powerText))
        self._craftBonusLabel.setText(self._translate(self._window_name, craftBonusText))
        self._enchantBonusLabel.setText(self._translate(self._window_name, enchantBonusText))
        self._dodgeLabel.setText(self._translate(self._window_name, dodgeText))
        self._runLabel.setText(self._translate(self._window_name, runText))

        ap = -1
        if self._player:
            ap = self._player.ability_points
        self._abilityPointsLabel.setText(self._translate(self._window_name, "AP: {}".format(ap)))
        labelText = "{}:"
        scoreText = "{}"
        incrementText = "+"
        for abilityName in self._abilityNames:
            abilityDescription = ""
            abilityScore = -1
            if self._player:
                abilityDescription = self._player.ability(abilityName, "description")
                abilityScore = self._player.ability(abilityName)
            abilityLabel = self._abilityWidgets[self._labelFormat.format(abilityName)]
            abilityLabel.setText(self._translate(self._window_name, labelText.format(abilityName[0:3].upper())))
            abilityLabel.setToolTip(self._translate(self._window_name, abilityDescription))
            abilityScoreLabel = self._abilityWidgets[self._scoreFormat.format(abilityName)]
            abilityScoreLabel.setText(self._translate(self._window_name, scoreText.format(abilityScore)))
            if abilityScore >= self._player.maxAbilityScore():
                abilityScoreLabel.setStyleSheet(self._greenStyleSheet)
            incrementButton = self._abilityWidgets[self._incrementFormat.format(abilityName)]
            incrementButton.setText(self._translate(self._window_name, incrementText))
            incrementButton.setEnabled(ap > 0)

        self._inventoryTable.update()

        self._menuFile.setTitle(self._translate(self._window_name, "File"))
        self._menuWindow.setTitle(self._translate(self._window_name, "Window"))
        self._menuPosition.setTitle(self._translate(self._window_name, "Position"))
        self._menuResize.setTitle(self._translate(self._window_name, "Resize"))

        self._action_0_0.setText(self._translate(self._window_name, "(0, 0)"))
        self._action_0_0.setToolTip(self._translate(self._window_name, "Set the window position"))
        self._action_100_100.setText(self._translate(self._window_name, "(0, 100)"))
        self._action_100_100.setToolTip(self._translate(self._window_name, "Set the window position"))
        self._action_500_500.setText(self._translate(self._window_name, "(500, 500)"))
        self._action_500_500.setToolTip(self._translate(self._window_name, "Set the window position"))

        self._action_800x600.setText(self._translate(self._window_name, "800 x 600"))
        self._action_1280x900.setText(self._translate(self._window_name, "1280 x 720"))
        self._action_1920x1080.setText(self._translate(self._window_name, "1920 x 1080"))
        self._action_2560x1440.setText(self._translate(self._window_name, "2560 x 1440"))

        self._actionLoad.setText(self._translate(self._window_name, "Load"))
        self._actionLoad.setShortcut(self._translate(self._window_name, "Ctrl+L"))
        self._actionSave.setText(self._translate(self._window_name, "Save"))
        self._actionSave.setShortcut(self._translate(self._window_name, "Ctrl+S"))
        self._actionQuit.setText(self._translate(self._window_name, "Quit to Menu"))
        self._actionQuit.setShortcut(self._translate(self._window_name, "Ctrl+Q"))
