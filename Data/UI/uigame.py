from functools import partial

from PyQt5 import QtCore, QtGui, QtWidgets

from Data.UI.inventory_model import InventoryModel
from Data.UI.ui import UI


class UiGame(UI):
    def __init__(self, window: QtWidgets.QMainWindow):
        super().__init__(window, window_name="GameWindow", window_show_size=QtCore.QSize(800, 600),
                         window_title="Text RPG - Exploring the World")
        self._centralWidget = QtWidgets.QWidget(self._window)
        self._centralWidget.setObjectName("centralWidget")

        self._sceneGroupBox = QtWidgets.QGroupBox(self._centralWidget)
        self._sceneGroupBox.setMinimumSize(QtCore.QSize(400, 200))
        self._sceneGroupBox.setObjectName("sceneGroupBox")
        self._sceneDescriptionLabel = QtWidgets.QLabel(self._sceneGroupBox)
        self._sceneDescriptionLabel.setObjectName("sceneDescriptionLabel")
        self._sceneDescriptionLabel.setWordWrap(True)
        self._sceneImage = QtWidgets.QLabel(self._sceneGroupBox)
        self._sceneImage.setFixedSize(self._defaultIconSize)
        self._sceneImage.setScaledContents(True)
        self._sceneImage.setFrameStyle(QtWidgets.QFrame.Panel | QtWidgets.QFrame.Raised)

        self._sceneGroupBoxLayout = QtWidgets.QGridLayout(self._sceneGroupBox)
        self._sceneGroupBoxLayout.addWidget(self._sceneDescriptionLabel, 0, 0, 1, 1)
        self._sceneGroupBoxLayout.addWidget(self._sceneImage, 0, 1, 1, 1)
        self._sceneGroupBox.setLayout(self._sceneGroupBoxLayout)

        self._sceneActionsGroupBox = QtWidgets.QGroupBox(self._centralWidget)
        self._sceneActionsGroupBox.setObjectName("sceneActionsGroupBox")
        self._sceneActionsScrollArea = QtWidgets.QScrollArea(self._sceneActionsGroupBox)
        self._sceneActionsScrollArea.setFrameShape(QtWidgets.QFrame.NoFrame)
        self._sceneActionsScrollArea.setWidgetResizable(True)
        self._sceneActionsScrollArea.setObjectName("sceneActionsScrollArea")
        self._sceneActionsScrollAreaContent = QtWidgets.QWidget()
        self._sceneActionsScrollAreaContent.setObjectName("sceneActionsScrollAreaContent")
        self._sceneActionsScrollAreaLayout = QtWidgets.QGridLayout(self._sceneActionsScrollAreaContent)
        self._sceneActionsScrollAreaLayout.setObjectName("scrollAreaLayout")
        self._sceneActionButtons: list[QtWidgets.QPushButton] = []
        for index in range(15):
            button = QtWidgets.QPushButton(self._sceneActionsScrollAreaContent)
            button.setObjectName("sceneActionButton{}".format(index))
            button.setMinimumSize(self._defaultButtonSize)
            self._sceneActionsScrollAreaLayout.addWidget(button, index, 0, 1, 1)
            self._sceneActionButtons.append(button)
        self._sceneActionsScrollArea.setWidget(self._sceneActionsScrollAreaContent)
        self._sceneActionsLayout = QtWidgets.QGridLayout(self._sceneActionsGroupBox)
        self._sceneActionsLayout.setObjectName("sceneActionsHorizontalLayout")
        self._sceneActionsLayout.addWidget(self._sceneActionsScrollArea, 0, 0)

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
        self._mainGridLayout.addWidget(self._sceneGroupBox, 0, 0, 1, 2)
        self._mainGridLayout.addWidget(self._sceneActionsGroupBox, 1, 0, 1, 1)
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
        self._menuHelp = QtWidgets.QAction(self._menubar)
        self._menuHelp.setObjectName("menuHelp")
        self._window.setMenuBar(self._menubar)
        self._action_topLeft = QtWidgets.QAction(self._window)
        self._action_topLeft.setShortcutVisibleInContextMenu(False)
        self._action_topLeft.setObjectName("action_0_0")
        self._action_recenter = QtWidgets.QAction(self._window)
        self._action_recenter.setShortcutVisibleInContextMenu(False)
        self._action_recenter.setObjectName("action_recenter")
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
        self._menuPosition.addAction(self._action_topLeft)
        self._menuPosition.addAction(self._action_recenter)
        self._menuResize.addAction(self._action_800x600)
        self._menuResize.addAction(self._action_1280x900)
        self._menuResize.addAction(self._action_1920x1080)
        self._menuResize.addAction(self._action_2560x1440)
        self._menuWindow.addAction(self._menuResize.menuAction())
        self._menuWindow.addAction(self._menuPosition.menuAction())
        self._menubar.addAction(self._menuFile.menuAction())
        self._menubar.addAction(self._menuWindow.menuAction())
        self._menubar.addAction(self._menuHelp)

        self._getScene = None
        self._getSceneDescription = None
        self._player = None
        self._action_topLeft.triggered.connect(partial(self.reposition_window, 0, 0))
        self._action_recenter.triggered.connect(self._recenter)
        self._action_800x600.triggered.connect(partial(self.resize_window, 800, 600))
        self._action_1280x900.triggered.connect(partial(self.resize_window, 1280, 900))
        self._action_1920x1080.triggered.connect(partial(self.resize_window, 1920, 1080))
        self._action_2560x1440.triggered.connect(partial(self.resize_window, 2560, 1440))
        QtCore.QMetaObject.connectSlotsByName(self._window)

    def connect(self, get_scene=None, get_scene_description=None, player=None, save_game=None, select_action=None,
                show_help=None, show_load=None, show_main=None):
        if get_scene:
            self._getScene = get_scene
        if get_scene_description:
            self._getSceneDescription = get_scene_description
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
            for index in range(len(self._sceneActionButtons)):
                scene_action_button = self._sceneActionButtons[index]
                scene_action_button.clicked.connect(partial(select_action, index))
                scene_action_button.clicked.connect(self.refresh)
        if show_help:
            self._menuHelp.triggered.connect(show_help)
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
            self._sceneImage.setPixmap(QtGui.QPixmap(scene.imagePath))
        self._sceneGroupBox.setTitle(self._translate(self._window_name, scene_name))

        scene_description = ""
        if self._getSceneDescription:
            scene_description = self._getSceneDescription()
        self._sceneDescriptionLabel.setText(self._translate(self._window_name, scene_description))
        self._sceneActionsGroupBox.setTitle(self._translate(self._window_name, "Actions"))

        for index, action_button in enumerate(self._sceneActionButtons):
            if scene:
                action = scene.getAction(index)
                if action:
                    requirementMet = action.requirementMet(self._player)
                    if not action.removed and (not action.secret or action.selected or requirementMet):
                        icon = QtGui.QIcon()
                        if action.selected:
                            icon = self._checkIcon
                        elif not requirementMet:
                            icon = self._requirementIcon
                        action_button.setIcon(icon)
                        action_button.setEnabled(action.enabled)
                        action_button.setText(self._translate(self._window_name, action.description))
                        action_button.setToolTip(self._translate(self._window_name, action.requirement.description()))
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
        if self._player:
            levelText = levelText.format(self._player.level)
            expText = expText.format(self._player.experience, self._player.requiredExperience())
            powerText = powerText.format(self._player.powerLevel())
            craftBonusText = craftBonusText.format(self._player.craftingBonus())
            enchantBonusText = enchantBonusText.format(self._player.enchantingBonus())
        self._levelLabel.setText(self._translate(self._window_name, levelText))
        self._expLabel.setText(self._translate(self._window_name, expText))
        self._powerLabel.setText(self._translate(self._window_name, powerText))
        self._craftBonusLabel.setText(self._translate(self._window_name, craftBonusText))
        self._enchantBonusLabel.setText(self._translate(self._window_name, enchantBonusText))

        ap = -1
        if self._player:
            ap = self._player.ability_points
        self._abilityPointsLabel.setText(self._translate(self._window_name, "AP: {}".format(ap)))
        self._abilityPointsLabel.setToolTip(self._translate(self._window_name, "Ability Points"))
        labelText = "{}:"
        scoreText = "{}"
        incrementText = "+"
        incrementTooltip = "Increase {}"
        for abilityName in self._abilityNames:
            abilityAbbreviation = abilityName[0:3].upper()
            abilityDescription = ""
            abilityScore = -1
            if self._player:
                abilityDescription = self._player.ability(abilityName, "description")
                abilityScore = self._player.ability(abilityName)
            abilityLabel = self._abilityWidgets[self._labelFormat.format(abilityName)]
            abilityLabel.setText(self._translate(self._window_name, labelText.format(abilityAbbreviation)))
            abilityLabel.setToolTip(self._translate(self._window_name, abilityDescription))
            abilityScoreLabel = self._abilityWidgets[self._scoreFormat.format(abilityName)]
            abilityScoreLabel.setText(self._translate(self._window_name, scoreText.format(abilityScore)))
            abilityScoreLabel.setToolTip(self._translate(self._window_name, abilityDescription))
            if abilityScore >= self._player.maxAbilityScore():
                abilityScoreLabel.setStyleSheet(self._greenStyleSheet)
            incrementButton = self._abilityWidgets[self._incrementFormat.format(abilityName)]
            incrementButton.setText(self._translate(self._window_name, incrementText))
            incrementButton.setEnabled(ap > 0)
            incrementButton.setToolTip(self._translate(self._window_name, incrementTooltip.format(abilityAbbreviation)))

        self._inventoryTable.update()

        self._menuFile.setTitle(self._translate(self._window_name, "File"))
        self._menuWindow.setTitle(self._translate(self._window_name, "Window"))
        self._menuPosition.setTitle(self._translate(self._window_name, "Position"))
        self._menuResize.setTitle(self._translate(self._window_name, "Resize"))
        self._menuHelp.setText(self._translate(self._window_name, "Help"))

        self._action_topLeft.setText(self._translate(self._window_name, "Top-Left Corner"))
        self._action_topLeft.setToolTip(self._translate(self._window_name, "Set the window position"))
        self._action_recenter.setText(self._translate(self._window_name, "Center"))
        self._action_recenter.setToolTip(self._translate(self._window_name, "Set the window position"))

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
