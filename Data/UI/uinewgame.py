from functools import partial

from PyQt5 import QtCore, QtGui, QtWidgets

from Data.UI.ui import UI


class UiNewGame(UI):
    _introductionText = "Welcome to TextRPG! Please edit your character's name and abilities below."

    def __init__(self, window: QtWidgets.QMainWindow):
        super().__init__(window, window_name="NewGameWindow", window_show_size=QtCore.QSize(800, 600),
                         window_title="Text RPG - New Game")
        self._centralWidget = QtWidgets.QWidget(self._window)
        self._centralWidget.setObjectName("centralWidget")

        self._introductionLabel = QtWidgets.QLabel(self._centralWidget)
        self._introductionLabel.setAlignment(QtCore.Qt.AlignCenter)
        self._introductionLabel.setWordWrap(True)
        self._introductionLabel.setObjectName("introductionLabel")

        self._nameLabel = QtWidgets.QLabel(self._centralWidget)
        self._nameLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self._nameLabel.setObjectName("nameLabel")
        self._nameInput = QtWidgets.QLineEdit(self._centralWidget)
        self._nameInput.setValidator(QtGui.QRegularExpressionValidator(QtCore.QRegularExpression('^[A-Za-z0-9]+$')))
        self._abilityPointsIcon = QtWidgets.QLabel(self._centralWidget)
        self._abilityPointsIcon.setPixmap(self._abilityIcons["points"].pixmap(self._smallIconSize))
        self._abilityPointsIcon.setAlignment(QtCore.Qt.AlignCenter)
        self._abilityPointsLabel = QtWidgets.QLabel(self._centralWidget)
        self._abilityPointsLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self._abilityPointsLabel.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self._abilityPointsRemainingLabel = QtWidgets.QLabel(self._centralWidget)
        self._abilityPointsRemainingLabel.setAlignment(QtCore.Qt.AlignCenter)
        self._abilityPointsRemainingLabel.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)

        self._centralWidgetLayout = QtWidgets.QGridLayout(self._centralWidget)
        self._centralWidgetLayout.addWidget(self._introductionLabel, 0, 0, 2, 5)
        self._centralWidgetLayout.addWidget(self._nameLabel, 2, 1, 1, 1)
        self._centralWidgetLayout.addWidget(self._nameInput, 2, 2, 1, 2)
        self._centralWidgetLayout.addWidget(self._abilityPointsIcon, 3, 1, 1, 1)
        self._centralWidgetLayout.addWidget(self._abilityPointsLabel, 3, 2, 1, 1)
        self._centralWidgetLayout.addWidget(self._abilityPointsRemainingLabel, 3, 3, 1, 1)

        self._iconFormat = "{}Icon"
        self._labelFormat = "{}Label"
        self._layoutFormat = "{}Layout"
        self._decrementFormat = "{}DecrementButton"
        self._scoreFormat = "{}ScoreLabel"
        self._incrementFormat = "{}IncrementButton"
        self._abilityWidgets: dict[str, QtWidgets.QWidget] = {}
        for abilityIndex, abilityName in enumerate(self._abilityNames):
            row = abilityIndex + 4

            abilityIcon = QtWidgets.QLabel(self._centralWidget)
            abilityIcon.setAlignment(QtCore.Qt.AlignCenter)
            abilityIcon.setPixmap(self._abilityIcons[abilityName.lower()].pixmap(self._smallIconSize))
            iconKey = self._iconFormat.format(abilityName)
            self._abilityWidgets[iconKey] = abilityIcon

            abilityLabel = QtWidgets.QLabel(self._centralWidget)
            abilityLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            abilityLabel.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
            abilityLabelKey = self._labelFormat.format(abilityName)
            self._abilityWidgets[abilityLabelKey] = abilityLabel

            decrementButton = QtWidgets.QPushButton(self._centralWidget)
            decrementButton.setFixedSize(self._tinyButtonSize)
            decrementButton.setStyleSheet(self._boldStyleSheet)
            decrementButtonKey = self._decrementFormat.format(abilityName)
            self._abilityWidgets[decrementButtonKey] = decrementButton

            scoreLabel = QtWidgets.QLabel(self._centralWidget)
            scoreLabel.setStyleSheet(self._boldStyleSheet)
            scoreLabel.setAlignment(QtCore.Qt.AlignCenter)
            scoreLabelKey = self._scoreFormat.format(abilityName)
            self._abilityWidgets[scoreLabelKey] = scoreLabel

            incrementButton = QtWidgets.QPushButton(self._centralWidget)
            incrementButton.setFixedSize(self._tinyButtonSize)
            incrementButton.setStyleSheet(self._boldStyleSheet)
            incrementButtonKey = self._incrementFormat.format(abilityName)
            self._abilityWidgets[incrementButtonKey] = incrementButton

            abilityModLayout = QtWidgets.QHBoxLayout(self._centralWidget)
            abilityModLayout.setAlignment(QtCore.Qt.AlignCenter)
            abilityModLayout.addWidget(decrementButton)
            abilityModLayout.addWidget(scoreLabel)
            abilityModLayout.addWidget(incrementButton)

            self._centralWidgetLayout.addWidget(abilityIcon, row, 1, 1, 1)
            self._centralWidgetLayout.addWidget(abilityLabel, row, 2, 1, 1)
            self._centralWidgetLayout.addLayout(abilityModLayout, row, 3, 1, 1)

        self._cancelButton = QtWidgets.QPushButton(self._centralWidget)
        self._cancelButton.setFixedSize(self._largeButtonSize)
        self._cancelButton.setObjectName("returnButton")
        self._startGameButton = QtWidgets.QPushButton(self._centralWidget)
        self._startGameButton.setFixedSize(self._largeButtonSize)
        self._startGameButton.setObjectName("startGameButton")

        self._centralWidgetLayout.addWidget(self._cancelButton, 12, 1, 1, 1)
        self._centralWidgetLayout.addWidget(self._startGameButton, 12, 3, 1, 1)
        self._centralWidget.setLayout(self._centralWidgetLayout)
        self._window.setCentralWidget(self._centralWidget)

        self.player = None
        QtCore.QMetaObject.connectSlotsByName(self._window)

    def connect(self, player=None, show_main=None, start_game=None):
        if player:
            self.player = player
            self._nameInput.textEdited.connect(self._set_name)

            for abilityName in self._abilityNames:
                decrementButton = self._abilityWidgets[self._decrementFormat.format(abilityName)]
                decrementButton.clicked.connect(partial(player.modifyAbilityScore, abilityName, -1, True))
                decrementButton.clicked.connect(self.refresh)
                incrementButton = self._abilityWidgets[self._incrementFormat.format(abilityName)]
                incrementButton.clicked.connect(partial(player.modifyAbilityScore, abilityName, 1))
                incrementButton.clicked.connect(self.refresh)
        if show_main:
            self._cancelButton.clicked.connect(show_main)
        if start_game:
            self._startGameButton.clicked.connect(start_game)

    def refresh(self):
        self._window.setWindowTitle(self._translate(self._window_name, "Text RPG - New Game"))
        self._nameLabel.setText(self._translate(self._window_name, "Name:"))
        name = ""
        if self.player:
            name = self.player.name
        self._nameInput.setText(self._translate(self._window_name, name))

        labelText = "{} ({}):"
        decrementText = "-"
        scoreText = "{}"
        incrementText = "+"
        for abilityName in self._abilityNames:
            abilityIcon = self._abilityWidgets[self._iconFormat.format(abilityName)]
            abilityIcon.setToolTip(self._translate(self._window_name, abilityName))

            abilityDescription = ""
            abilityScore = -1
            if self.player:
                abilityDescription = self.player.ability(abilityName, "description")
                abilityScore = self.player.ability(abilityName)
            abilityLabel = self._abilityWidgets[self._labelFormat.format(abilityName)]
            abilityLabel.setText(
                self._translate(self._window_name, labelText.format(abilityName, abilityName[0:3].upper())))
            abilityLabel.setToolTip(self._translate(self._window_name, abilityDescription))
            decrementButton = self._abilityWidgets[self._decrementFormat.format(abilityName)]
            decrementButton.setText(self._translate(self._window_name, decrementText))
            abilityScoreLabel = self._abilityWidgets[self._scoreFormat.format(abilityName)]
            abilityScoreLabel.setText(self._translate(self._window_name, scoreText.format(abilityScore)))
            abilityScoreLabel.setToolTip(abilityDescription)
            incrementButton = self._abilityWidgets[self._incrementFormat.format(abilityName)]
            incrementButton.setText(self._translate(self._window_name, incrementText))

        ap = -1
        if self.player:
            ap = self.player.ability_points
        self._abilityPointsIcon.setToolTip(self._translate(self._window_name, "Ability Points"))
        abilityPointsTooltip = self._translate(self._window_name, "Spend ability points now or later to increase your "
                                                                  "character's abilities.")
        self._abilityPointsLabel.setText(self._translate(self._window_name, "Ability Points (AP):"))
        self._abilityPointsLabel.setToolTip(abilityPointsTooltip)
        self._abilityPointsRemainingLabel.setText(self._translate(self._window_name, str(ap)))
        self._abilityPointsRemainingLabel.setToolTip(abilityPointsTooltip)
        self._introductionLabel.setText(self._translate(self._window_name, self._introductionText))
        self._startGameButton.setText(self._translate(self._window_name, "Begin Journey"))
        self._cancelButton.setText(self._translate(self._window_name, "Cancel"))

    def _set_name(self, name: str):
        if not self.player:
            return
        self.player.name = name
