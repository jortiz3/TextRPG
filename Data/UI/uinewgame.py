from functools import partial

from PyQt5 import QtCore, QtGui, QtWidgets

from Data.UI.ui import UI


class UiNewGame(UI):
    _introductionText = "You begin to feel a swaying motion transition into abrupt shakes as a blinding light " \
                        "swallows you. As you rub your eyes, you find yourself in the woods. Before long you notice " \
                        "the muffled voice of the burly man before you, \"Are you okay? Do you remember who you are?\""

    def __init__(self, window: QtWidgets.QMainWindow):
        super().__init__(window, window_name="NewGameWindow", window_show_size=QtCore.QSize(800, 600),
                         window_title="Text RPG - New Game")
        self._centralWidget = QtWidgets.QWidget(self._window)
        self._centralWidget.setObjectName("centralWidget")

        self._introductionLabel = QtWidgets.QLabel(self._centralWidget)
        self._introductionLabel.setAlignment(QtCore.Qt.AlignVCenter)
        self._introductionLabel.setWordWrap(True)
        self._introductionLabel.setObjectName("introductionLabel")

        self._nameLabel = QtWidgets.QLabel(self._centralWidget)
        self._nameLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self._nameLabel.setObjectName("nameLabel")
        self._nameInput = QtWidgets.QLineEdit(self._centralWidget)
        self._nameInput.setValidator(QtGui.QRegularExpressionValidator(QtCore.QRegularExpression('^[A-Za-z0-9]+$')))
        self._nameInput.setObjectName("nameInput")
        self._abilityPointsLabel = QtWidgets.QLabel(self._centralWidget)
        self._abilityPointsLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self._abilityPointsLabel.setMaximumWidth(self._largeButtonSize.width())
        self._abilityPointsLabel.setObjectName("abilityPointsLabel")
        self._abilityPointsRemainingLabel = QtWidgets.QLabel(self._centralWidget)
        self._abilityPointsRemainingLabel.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self._abilityPointsRemainingLabel.setMaximumWidth(self._largeButtonSize.width())
        self._abilityPointsRemainingLabel.setObjectName("abilityPointsRemainingLabel")

        self._centralWidgetLayout = QtWidgets.QGridLayout(self._centralWidget)
        self._centralWidgetLayout.setObjectName("centralWidgetLayout")

        self._centralWidgetLayout.addWidget(self._introductionLabel, 0, 0, 2, 4)
        self._centralWidgetLayout.addWidget(self._nameLabel, 2, 1, 1, 1)
        self._centralWidgetLayout.addWidget(self._nameInput, 2, 2, 1, 2)
        self._centralWidgetLayout.addWidget(self._abilityPointsLabel, 3, 1, 1, 1)
        self._centralWidgetLayout.addWidget(self._abilityPointsRemainingLabel, 3, 2, 1, 1)

        self._labelFormat = "{}Label"
        self._layoutFormat = "{}Layout"
        self._decrementFormat = "{}DecrementButton"
        self._scoreFormat = "{}ScoreLabel"
        self._incrementFormat = "{}IncrementButton"
        self._abilityWidgets: dict[str, QtWidgets.QWidget] = {}
        for abilityIndex in range(len(self._abilityNames)):
            abilityName = self._abilityNames[abilityIndex]
            row = abilityIndex + 4

            abilityLabel = QtWidgets.QLabel(self._centralWidget)
            abilityLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            abilityLabelKey = self._labelFormat.format(abilityName)
            abilityLabel.setObjectName(abilityLabelKey)
            self._abilityWidgets[abilityLabelKey] = abilityLabel

            decrementButton = QtWidgets.QPushButton(self._centralWidget)
            decrementButton.setFixedSize(self._tinyButtonSize)
            decrementButton.setStyleSheet(self._boldStyleSheet)
            decrementButtonKey = self._decrementFormat.format(abilityName)
            decrementButton.setObjectName(decrementButtonKey)
            self._abilityWidgets[decrementButtonKey] = decrementButton

            scoreLabel = QtWidgets.QLabel(self._centralWidget)
            scoreLabel.setStyleSheet(self._boldStyleSheet)
            scoreLabel.setAlignment(QtCore.Qt.AlignCenter)
            scoreLabelKey = self._scoreFormat.format(abilityName)
            scoreLabel.setObjectName(scoreLabelKey)
            self._abilityWidgets[scoreLabelKey] = scoreLabel

            incrementButton = QtWidgets.QPushButton(self._centralWidget)
            incrementButton.setFixedSize(self._tinyButtonSize)
            incrementButton.setStyleSheet(self._boldStyleSheet)
            incrementButtonKey = self._incrementFormat.format(abilityName)
            incrementButton.setObjectName(incrementButtonKey)
            self._abilityWidgets[incrementButtonKey] = incrementButton

            spacer = QtWidgets.QSpacerItem(self._defaultButtonSize.width(), self._defaultButtonSize.height(),
                                           QtWidgets.QSizePolicy.Expanding)

            abilityModLayout = QtWidgets.QHBoxLayout(self._centralWidget)
            abilityModLayout.addWidget(decrementButton)
            abilityModLayout.addWidget(scoreLabel)
            abilityModLayout.addWidget(incrementButton)
            abilityModLayout.addSpacerItem(spacer)

            self._centralWidgetLayout.addWidget(abilityLabel, row, 1, 1, 1)
            self._centralWidgetLayout.addLayout(abilityModLayout, row, 2, 1, 2)

        self._cancelButton = QtWidgets.QPushButton(self._centralWidget)
        self._cancelButton.setFixedSize(self._largeButtonSize)
        self._cancelButton.setObjectName("returnButton")
        self._startGameButton = QtWidgets.QPushButton(self._centralWidget)
        self._startGameButton.setFixedSize(self._largeButtonSize)
        self._startGameButton.setObjectName("startGameButton")

        self._centralWidgetLayout.addWidget(self._cancelButton, 12, 1, 1, 1)
        self._centralWidgetLayout.addWidget(self._startGameButton, 12, 2, 1, 1)
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
        self._abilityPointsLabel.setText(self._translate(self._window_name, "Ability Points (AP):"))
        self._abilityPointsRemainingLabel.setText(self._translate(self._window_name, str(ap)))
        self._introductionLabel.setText(self._translate(self._window_name, self._introductionText))
        self._startGameButton.setText(self._translate(self._window_name, "Begin Journey"))
        self._cancelButton.setText(self._translate(self._window_name, "Cancel"))

    def _set_name(self, name: str):
        if not self.player:
            return
        self.player.name = name
