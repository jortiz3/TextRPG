from functools import partial

from Data.UI.ui import UI

from PyQt5 import QtCore, QtGui, QtWidgets


class UiHelp(UI):
    __abilityDescription = "Abilities define a character's skill or means to overcome obstacles within the game."
    __inventoryDescription = "The inventory tracks all of the items within a character's possession."
    __itemDescription = "Items can be used to overcome obstacles on a character's journey."
    __sceneDescription = "Scenes are the opportunities and obstacles presented to a character."
    __actionDescription = "Actions are events a character can perform to progress through the game."
    __requirementDescription = "Requirements are abilities or items needed to use a given action."
    __rewardDescription = "Rewards are either experience or items awarded to a character for using an action."

    __sceneIconPath = "Data/Images/Scene/cave.png"

    def __init__(self, window: QtWidgets.QMainWindow):
        super().__init__(window, window_name="HelpWindow", window_show_size=QtCore.QSize(400, 600),
                         window_title="TextRPG - Help")
        groupBoxSize = QtCore.QSize(400, 200)
        iconSize = QtCore.QSize(64, 64)
        labelSize = QtCore.QSize(100, 100)

        self._centralWidget = QtWidgets.QWidget(self._window)
        self._scrollArea = QtWidgets.QScrollArea(self._centralWidget)
        self._scrollArea.setWidgetResizable(True)
        self._scrollContent = QtWidgets.QWidget(self._scrollArea)
        self._characterGroupBox = QtWidgets.QGroupBox(self._scrollContent)
        self._characterGroupBox.setMinimumSize(groupBoxSize)
        self._characterGroupBox.setFlat(True)
        self._abilityGroupBox = QtWidgets.QGroupBox(self._characterGroupBox)
        self._abilityGroupBox.setMinimumSize(groupBoxSize)
        self._abilityGroupBox.setFlat(True)
        self._abilityLabel = QtWidgets.QLabel(self._abilityGroupBox)
        self._abilityLabel.setMinimumSize(labelSize)
        self._abilityLabel.setWordWrap(True)
        self._inventoryGroupBox = QtWidgets.QGroupBox(self._characterGroupBox)
        self._inventoryGroupBox.setMinimumSize(groupBoxSize)
        self._inventoryGroupBox.setFlat(True)
        self._inventoryLabel = QtWidgets.QLabel(self._inventoryGroupBox)
        self._inventoryLabel.setMinimumSize(labelSize)
        self._inventoryLabel.setWordWrap(True)
        self._itemLabel = QtWidgets.QLabel(self._inventoryGroupBox)
        self._itemLabel.setMinimumSize(labelSize)
        self._itemLabel.setWordWrap(True)
        self._sceneGroupBox = QtWidgets.QGroupBox(self._scrollContent)
        self._sceneGroupBox.setMinimumSize(groupBoxSize)
        self._sceneGroupBox.setFlat(True)
        sceneIcon = QtWidgets.QLabel(self._sceneGroupBox)
        sceneIcon.setPixmap(QtGui.QPixmap(self.__sceneIconPath))
        sceneIcon.setFrameStyle(QtWidgets.QFrame.Panel | QtWidgets.QFrame.Raised)
        sceneIcon.setScaledContents(True)
        sceneIcon.setFixedSize(iconSize)
        self._sceneLabel = QtWidgets.QLabel(self._sceneGroupBox)
        self._sceneLabel.setMinimumSize(labelSize)
        self._sceneLabel.setWordWrap(True)
        self._actionGroupBox = QtWidgets.QGroupBox(self._sceneGroupBox)
        self._actionGroupBox.setMinimumSize(groupBoxSize)
        self._actionGroupBox.setFlat(True)
        self._actionButton = QtWidgets.QPushButton(self._actionGroupBox)
        self._actionLabel = QtWidgets.QLabel(self._actionGroupBox)
        self._actionLabel.setMinimumSize(labelSize)
        self._actionLabel.setWordWrap(True)
        self._requirementGroupBox = QtWidgets.QGroupBox(self._actionGroupBox)
        self._requirementGroupBox.setMinimumSize(groupBoxSize)
        self._requirementGroupBox.setFlat(True)
        requirementIcon = QtWidgets.QLabel(self._requirementGroupBox)
        requirementIcon.setPixmap(self._requirementIcon.pixmap(iconSize))
        self._requirementLabel = QtWidgets.QLabel(self._requirementGroupBox)
        self._requirementLabel.setMinimumSize(labelSize)
        self._requirementLabel.setWordWrap(True)
        self._rewardGroupBox = QtWidgets.QGroupBox(self._actionGroupBox)
        self._rewardGroupBox.setMinimumSize(groupBoxSize)
        self._rewardGroupBox.setFlat(True)
        rewardIcon = QtWidgets.QLabel(self._rewardGroupBox)
        rewardIcon.setPixmap(self._checkIcon.pixmap(iconSize))
        self._rewardLabel = QtWidgets.QLabel(self._rewardGroupBox)
        self._rewardLabel.setMinimumSize(labelSize)
        self._rewardLabel.setWordWrap(True)
        self._closeButton = QtWidgets.QPushButton(self._scrollArea)

        abilityLayout = QtWidgets.QHBoxLayout()
        abilityLayout.addWidget(self._abilityLabel)
        self._abilityGroupBox.setLayout(abilityLayout)

        inventoryLayout = QtWidgets.QGridLayout()
        inventoryLayout.addWidget(self._inventoryLabel, 0, 1, 1, 2)
        inventoryLayout.addWidget(self._itemLabel, 1, 1, 1, 2)
        self._inventoryGroupBox.setLayout(inventoryLayout)

        characterLayout = QtWidgets.QVBoxLayout()
        characterLayout.addWidget(self._abilityGroupBox)
        characterLayout.addWidget(self._inventoryGroupBox)
        self._characterGroupBox.setLayout(characterLayout)

        requirementLayout = QtWidgets.QHBoxLayout()
        requirementLayout.setAlignment(QtCore.Qt.AlignLeft)
        requirementLayout.addWidget(requirementIcon)
        requirementLayout.addWidget(self._requirementLabel, 1)
        self._requirementGroupBox.setLayout(requirementLayout)

        rewardLayout = QtWidgets.QHBoxLayout()
        rewardLayout.addWidget(rewardIcon)
        rewardLayout.addWidget(self._rewardLabel, 1)
        self._rewardGroupBox.setLayout(rewardLayout)

        actionLayout = QtWidgets.QGridLayout()
        actionLayout.addWidget(self._actionButton, 0, 0, 1, 1)
        actionLayout.addWidget(self._actionLabel, 0, 1, 1, 2)
        actionLayout.addWidget(self._requirementGroupBox, 1, 0, 2, 3)
        actionLayout.addWidget(self._rewardGroupBox, 3, 0, 2, 3)
        self._actionGroupBox.setLayout(actionLayout)

        sceneLayout = QtWidgets.QGridLayout()
        sceneLayout.addWidget(sceneIcon, 0, 0, 1, 1)
        sceneLayout.addWidget(self._sceneLabel, 0, 1, 1, 2)
        sceneLayout.addWidget(self._actionGroupBox, 1, 0, 2, 3)
        self._sceneGroupBox.setLayout(sceneLayout)

        scrollContentLayout = QtWidgets.QVBoxLayout()
        scrollContentLayout.setAlignment(QtCore.Qt.AlignCenter)
        scrollContentLayout.addWidget(self._characterGroupBox)
        scrollContentLayout.addWidget(self._sceneGroupBox)
        self._scrollContent.setLayout(scrollContentLayout)
        self._scrollArea.setWidget(self._scrollContent)

        centralLayout = QtWidgets.QVBoxLayout()
        centralLayout.addWidget(self._scrollArea)
        centralLayout.addWidget(self._closeButton)
        self._centralWidget.setLayout(centralLayout)
        self._window.setCentralWidget(self._centralWidget)

        self._actionButton.clicked.connect(partial(self._actionButton.setIcon, self._checkIcon))
        self._closeButton.clicked.connect(self._window.hide)
        self._closeButton.clicked.connect(partial(self._actionButton.setIcon, QtGui.QIcon()))
        QtCore.QMetaObject.connectSlotsByName(self._window)

    def refresh(self):
        self._characterGroupBox.setTitle(self._translate(self._window_name, "Character"))
        self._abilityGroupBox.setTitle(self._translate(self._window_name, "Abilities"))
        self._abilityLabel.setText(self._translate(self._window_name, self.__abilityDescription))

        self._inventoryGroupBox.setTitle(self._translate(self._window_name, "Inventory"))
        self._inventoryLabel.setText(self._translate(self._window_name, self.__inventoryDescription))
        self._itemLabel.setText(self._translate(self._window_name, self.__itemDescription))

        self._sceneGroupBox.setTitle(self._translate(self._window_name, "Scenes"))
        self._sceneLabel.setText(self._translate(self._window_name, self.__sceneDescription))

        self._actionGroupBox.setTitle(self._translate(self._window_name, "Actions"))
        self._actionButton.setText(self._translate(self._window_name, "Action"))
        self._actionLabel.setText(self._translate(self._window_name, self.__actionDescription))

        self._requirementGroupBox.setTitle(self._translate(self._window_name, "Requirements"))
        self._requirementLabel.setText(self._translate(self._window_name, self.__requirementDescription))

        self._rewardGroupBox.setTitle(self._translate(self._window_name, "Rewards"))
        self._rewardLabel.setText(self._translate(self._window_name, self.__rewardDescription))

        self._closeButton.setText(self._translate(self._window_name, "Close"))
