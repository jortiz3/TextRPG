import copy
import sys
from functools import partial
from os.path import exists

import jsonpickle

from PyQt5 import Qt, QtCore, QtGui, QtWidgets

from Data.Character.ability import Ability
from Data.Editor.item_model import ItemModel
from Data.Editor.item_view import ItemView
from Data.Editor.undo_delete import UndoDelete
from Data.Editor.undo_new import UndoNew
from Data.Item.item_reference import ItemRef
from Data.Scene.requirement import Requirement
from Data.Scene.reward import Reward
from Data.Scene.scene import Scene
from Data.Scene.action import Action
from Data.Item.item import Item
from Data.UI.uisettings import UiSettings


class Editor(QtCore.QObject):
    __ability_names = ["dexterity", "intelligence", "strength", "will", "wisdom"]
    __numberOfReservedActions = 2

    def __init__(self):
        super().__init__()
        self.configPath = "editor.json"
        self.sceneDatabasePath = "Data/scenes.json"
        self.itemDatabasePath = "Data/items.json"
        self.items: list[Item] = []
        self.scenes: list[Scene] = []
        self.actionIndex: int = 0
        self.sceneIndex: int = 0
        self.requirementAbilityIndex: int = 0
        self.requirementItemIndex: int = 0
        self.rewardItemIndex: int = 0
        self.reset(False)
        app = QtWidgets.QApplication(sys.argv)
        self.__initializeUi()
        self.updateSceneNameComboBoxes()
        self.updateItemNameComboBoxes()
        self.refresh()
        self.window.showMaximized()
        sys.exit(app.exec())

    def __initializeUi(self):
        self.checkIcon = QtGui.QIcon("Data/Images/UI/check.png")
        self.deleteIcon = QtGui.QIcon("Data/Images/UI/delete.png")
        self.editorIcon = QtGui.QIcon("Data/Images/UI/editor.png")
        self.folderIcon = QtGui.QIcon("Data/Images/UI/folder.png")
        self.gearIcon = QtGui.QIcon("Data/Images/UI/gear.png")
        self.newIcon = QtGui.QIcon("Data/Images/UI/plus.png")
        self.newItemIcon = QtGui.QIcon("Data/Images/UI/new.png")
        self.nextIcon = QtGui.QIcon("Data/Images/UI/next.png")
        self.previousIcon = QtGui.QIcon("Data/Images/UI/previous.png")

        buttonSize = Qt.QSize(50, 25)
        indexLabelWidth = buttonSize.width() * 2

        self.window = QtWidgets.QMainWindow()
        self.window.setMinimumSize(800, 400)
        self.window.setStyleSheet("font-size: 14pt")
        self.window.setWindowTitle("Text RPG - Editor")
        self.window.setWindowIcon(self.editorIcon)
        centralWidget = QtWidgets.QWidget(self.window)
        self.centralTabWidget = QtWidgets.QTabWidget(centralWidget)

        self.undoStack = QtWidgets.QUndoStack(self.window)
        self.actionIdValidator = QtGui.QIntValidator(-777, 999999)
        self.positiveNumberValidator = QtGui.QIntValidator(0, 999999)

        sceneTabCentralWidget = QtWidgets.QWidget(self.centralTabWidget)
        sceneTabWidget = QtWidgets.QTabWidget(sceneTabCentralWidget)
        sceneTabWidget.setObjectName("scene")
        infoTab = QtWidgets.QWidget(sceneTabWidget)
        sceneNameLabel = QtWidgets.QLabel(infoTab)
        sceneNameLabel.setText("Name:")
        sceneNameLabel.setToolTip("Name of the scene.")
        sceneNameLabel.setAlignment(QtCore.Qt.AlignRight)
        self.sceneNameInput = QtWidgets.QLineEdit(infoTab)
        imagePathLabel = QtWidgets.QLabel(infoTab)
        imagePathLabel.setText("Image:")
        imagePathLabel.setToolTip("The image to display for this scene.")
        imagePathLabel.setAlignment(QtCore.Qt.AlignRight)
        self.imagePathInput = QtWidgets.QLineEdit(infoTab)
        self.imagePathButton = QtWidgets.QPushButton(infoTab)
        self.imagePathButton.setIcon(self.folderIcon)
        self.imagePathButton.setFixedSize(buttonSize)
        sceneDescriptionLabel = QtWidgets.QLabel(infoTab)
        sceneDescriptionLabel.setText("Description:")
        sceneDescriptionLabel.setToolTip("Text displayed when entering the scene.")
        sceneDescriptionLabel.setAlignment(QtCore.Qt.AlignRight)
        self.sceneDescriptionInput = QtWidgets.QTextEdit(infoTab)
        sceneIndexLabel = QtWidgets.QLabel(sceneTabCentralWidget)
        sceneIndexLabel.setText("Scene:")
        sceneIndexLabel.setAlignment(QtCore.Qt.AlignRight)
        sceneIndexLabel.setFixedWidth(indexLabelWidth)
        self.sceneNameComboBox = QtWidgets.QComboBox(sceneTabCentralWidget)
        self.sceneNameComboBox.setEditable(False)
        self.previousSceneButton = QtWidgets.QPushButton(sceneTabCentralWidget)
        self.previousSceneButton.setToolTip("Previous Scene")
        self.previousSceneButton.setIcon(self.previousIcon)
        self.previousSceneButton.setFixedSize(buttonSize)
        self.deleteSceneButton = QtWidgets.QPushButton(sceneTabCentralWidget)
        self.deleteSceneButton.setToolTip("Delete Scene")
        self.deleteSceneButton.setIcon(self.deleteIcon)
        self.deleteSceneButton.setFixedSize(buttonSize)
        self.newSceneButton = QtWidgets.QPushButton(sceneTabCentralWidget)
        self.newSceneButton.setToolTip("New Scene")
        self.newSceneButton.setIcon(self.newIcon)
        self.newSceneButton.setFixedSize(buttonSize)
        self.nextSceneButton = QtWidgets.QPushButton(sceneTabCentralWidget)
        self.nextSceneButton.setToolTip("Next Scene")
        self.nextSceneButton.setIcon(self.nextIcon)
        self.nextSceneButton.setFixedSize(buttonSize)

        actionTab = QtWidgets.QWidget(sceneTabWidget)
        actionTab.setObjectName("action")
        actionDescriptionLabel = QtWidgets.QLabel(actionTab)
        actionDescriptionLabel.setText("Description:")
        actionDescriptionLabel.setAlignment(QtCore.Qt.AlignRight)
        self.actionDescriptionInput = QtWidgets.QLineEdit(actionTab)
        actionGoToLabel = QtWidgets.QLabel(actionTab)
        actionGoToLabel.setText("Go to:")
        actionGoToLabel.setToolTip("Scene to go to upon action selection.")
        actionGoToLabel.setAlignment(QtCore.Qt.AlignRight)
        self.actionGoToComboBox = QtWidgets.QComboBox(actionTab)
        self.actionGoToComboBox.setEditable(False)
        consequenceTooltip = "Description of what happens after selecting this action."
        actionConsequenceLabel = QtWidgets.QLabel(actionTab)
        actionConsequenceLabel.setText("Consequence:")
        actionConsequenceLabel.setToolTip(consequenceTooltip)
        actionConsequenceLabel.setAlignment(QtCore.Qt.AlignRight)
        self.actionConsequenceInput = QtWidgets.QLineEdit(actionTab)
        self.actionConsequenceInput.setToolTip(consequenceTooltip)
        actionSecretTooltip = "Secret actions are hidden until requirements are met."
        actionSecretLabel = QtWidgets.QLabel(actionTab)
        actionSecretLabel.setText("Secret:")
        actionSecretLabel.setToolTip(actionSecretTooltip)
        actionSecretLabel.setAlignment(QtCore.Qt.AlignRight)
        self.actionSecretCheck = QtWidgets.QCheckBox(actionTab)
        self.actionSecretCheck.setFixedWidth(indexLabelWidth)
        self.actionSecretCheck.setToolTip(actionSecretTooltip)
        disableOnSelectLabel = QtWidgets.QLabel(actionTab)
        disableOnSelectLabel.setText("Disable On Select:")
        disableOnSelectLabel.setAlignment(QtCore.Qt.AlignRight)
        self.disableOnSelectCheck = QtWidgets.QCheckBox(actionTab)
        self.disableOnSelectCheck.setFixedWidth(indexLabelWidth)
        removeOnSelectLabel = QtWidgets.QLabel(actionTab)
        removeOnSelectLabel.setText("Remove On Select:")
        removeOnSelectLabel.setAlignment(QtCore.Qt.AlignRight)
        self.removeOnSelectCheck = QtWidgets.QCheckBox(actionTab)
        self.removeOnSelectCheck.setFixedWidth(indexLabelWidth)
        self.actionIndexLabel = QtWidgets.QLabel(actionTab)
        self.actionIndexLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.actionIndexLabel.setFixedWidth(indexLabelWidth)
        self.actionIndexLabel.setToolTip("Action Index")
        self.previousActionButton = QtWidgets.QPushButton(actionTab)
        self.previousActionButton.setToolTip("Previous Action")
        self.previousActionButton.setIcon(self.previousIcon)
        self.previousActionButton.setFixedSize(buttonSize)
        self.deleteActionButton = QtWidgets.QPushButton(actionTab)
        self.deleteActionButton.setToolTip("Delete Action")
        self.deleteActionButton.setIcon(self.deleteIcon)
        self.deleteActionButton.setFixedSize(buttonSize)
        self.newActionButton = QtWidgets.QPushButton(actionTab)
        self.newActionButton.setToolTip("New Action")
        self.newActionButton.setIcon(self.newIcon)
        self.newActionButton.setFixedSize(buttonSize)
        self.nextActionButton = QtWidgets.QPushButton(actionTab)
        self.nextActionButton.setToolTip("Next Action")
        self.nextActionButton.setIcon(self.nextIcon)
        self.nextActionButton.setFixedSize(buttonSize)

        requirementGroupBox = QtWidgets.QGroupBox(actionTab)
        requirementGroupBox.setTitle("Requirements")
        requirementAbilityLabel = QtWidgets.QLabel(requirementGroupBox)
        requirementAbilityLabel.setText("Ability Name:")
        requirementAbilityLabel.setToolTip("Ability required to take this action.")
        requirementAbilityLabel.setAlignment(QtCore.Qt.AlignRight)
        self.requirementAbilityComboBox = QtWidgets.QComboBox(requirementGroupBox)
        self.requirementAbilityComboBox.setEditable(False)
        self.requirementAbilityComboBox.insertItems(0, self.__ability_names)
        requirementAbilityScoreLabel = QtWidgets.QLabel(requirementGroupBox)
        requirementAbilityScoreLabel.setText("Ability Score:")
        requirementAbilityScoreLabel.setToolTip("Score required to take this action.")
        requirementAbilityScoreLabel.setAlignment(QtCore.Qt.AlignRight)
        self.requirementAbilityScoreInput = QtWidgets.QLineEdit(requirementGroupBox)
        self.requirementAbilityScoreInput.setValidator(self.positiveNumberValidator)
        self.requirementAbilityIndexLabel = QtWidgets.QLabel(requirementGroupBox)
        self.requirementAbilityIndexLabel.setFixedWidth(indexLabelWidth)
        self.requirementAbilityIndexLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.previousRequirementAbilityButton = QtWidgets.QPushButton(requirementGroupBox)
        self.previousRequirementAbilityButton.setToolTip("Previous Ability Requirement")
        self.previousRequirementAbilityButton.setIcon(self.previousIcon)
        self.previousRequirementAbilityButton.setFixedSize(buttonSize)
        self.deleteRequirementAbilityButton = QtWidgets.QPushButton(requirementGroupBox)
        self.deleteRequirementAbilityButton.setToolTip("Delete Ability Requirement")
        self.deleteRequirementAbilityButton.setIcon(self.deleteIcon)
        self.deleteRequirementAbilityButton.setFixedSize(buttonSize)
        self.newRequirementAbilityButton = QtWidgets.QPushButton(requirementGroupBox)
        self.newRequirementAbilityButton.setToolTip("New Ability Requirement")
        self.newRequirementAbilityButton.setIcon(self.newIcon)
        self.newRequirementAbilityButton.setFixedSize(buttonSize)
        self.nextRequirementAbilityButton = QtWidgets.QPushButton(requirementGroupBox)
        self.nextRequirementAbilityButton.setToolTip("Next Ability Requirement")
        self.nextRequirementAbilityButton.setIcon(self.nextIcon)
        self.nextRequirementAbilityButton.setFixedSize(buttonSize)
        itemIdTooltip = "The name of the item in the 'Item' tab."
        requirementItemIdLabel = QtWidgets.QLabel(requirementGroupBox)
        requirementItemIdLabel.setText("Item:")
        requirementItemIdLabel.setToolTip(itemIdTooltip)
        requirementItemIdLabel.setAlignment(QtCore.Qt.AlignRight)
        self.requirementItemNameComboBox = QtWidgets.QComboBox(requirementGroupBox)
        self.requirementItemNameComboBox.setEditable(False)
        requirementItemQtyLabel = QtWidgets.QLabel(requirementGroupBox)
        requirementItemQtyLabel.setText("Item Quantity:")
        requirementItemQtyLabel.setToolTip("Quantity of item required to take this action.")
        requirementItemQtyLabel.setAlignment(QtCore.Qt.AlignRight)
        self.requirementItemQtyInput = QtWidgets.QLineEdit(requirementGroupBox)
        self.requirementItemQtyInput.setValidator(self.positiveNumberValidator)
        self.requirementItemIndexLabel = QtWidgets.QLabel(requirementGroupBox)
        self.requirementItemIndexLabel.setFixedWidth(indexLabelWidth)
        self.requirementItemIndexLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.previousRequirementItemButton = QtWidgets.QPushButton(requirementGroupBox)
        self.previousRequirementItemButton.setToolTip("Previous Item Requirement")
        self.previousRequirementItemButton.setIcon(self.previousIcon)
        self.previousRequirementItemButton.setFixedSize(buttonSize)
        self.deleteRequirementItemButton = QtWidgets.QPushButton(requirementGroupBox)
        self.deleteRequirementItemButton.setToolTip("Delete Item Requirement")
        self.deleteRequirementItemButton.setIcon(self.deleteIcon)
        self.deleteRequirementItemButton.setFixedSize(buttonSize)
        self.newRequirementItemButton = QtWidgets.QPushButton(requirementGroupBox)
        self.newRequirementItemButton.setToolTip("New Item Requirement")
        self.newRequirementItemButton.setIcon(self.newIcon)
        self.newRequirementItemButton.setFixedSize(buttonSize)
        self.nextRequirementItemButton = QtWidgets.QPushButton(requirementGroupBox)
        self.nextRequirementItemButton.setToolTip("Next Item Requirement")
        self.nextRequirementItemButton.setIcon(self.nextIcon)
        self.nextRequirementItemButton.setFixedSize(buttonSize)

        rewardGroupBox = QtWidgets.QGroupBox(infoTab)
        rewardGroupBox.setTitle("Rewards")
        rewardExpTooltip = "Experience points rewarded for taking this action."
        rewardExpLabel = QtWidgets.QLabel(rewardGroupBox)
        rewardExpLabel.setText("Experience:")
        rewardExpLabel.setToolTip(rewardExpTooltip)
        rewardExpLabel.setAlignment(QtCore.Qt.AlignRight)
        self.rewardExpInput = QtWidgets.QLineEdit(rewardGroupBox)
        self.rewardExpInput.setToolTip(rewardExpTooltip)
        self.rewardExpInput.setValidator(self.positiveNumberValidator)
        rewardItemIdLabel = QtWidgets.QLabel(rewardGroupBox)
        rewardItemIdLabel.setText("Item:")
        rewardItemIdLabel.setToolTip(itemIdTooltip)
        rewardItemIdLabel.setAlignment(QtCore.Qt.AlignRight)
        self.rewardItemNameComboBox = QtWidgets.QComboBox(rewardGroupBox)
        self.rewardItemNameComboBox.setEditable(False)
        rewardItemQtyLabel = QtWidgets.QLabel(rewardGroupBox)
        rewardItemQtyLabel.setText("Item Quantity:")
        rewardItemQtyLabel.setToolTip("Quantity of item rewarded for taking this action.")
        rewardItemQtyLabel.setAlignment(QtCore.Qt.AlignRight)
        self.rewardItemQtyInput = QtWidgets.QLineEdit(rewardGroupBox)
        self.rewardItemQtyInput.setValidator(self.positiveNumberValidator)
        self.rewardItemIndexLabel = QtWidgets.QLabel(rewardGroupBox)
        self.rewardItemIndexLabel.setFixedWidth(indexLabelWidth)
        self.rewardItemIndexLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.previousRewardItemButton = QtWidgets.QPushButton(rewardGroupBox)
        self.previousRewardItemButton.setToolTip("Previous Item Reward")
        self.previousRewardItemButton.setIcon(self.previousIcon)
        self.previousRewardItemButton.setFixedSize(buttonSize)
        self.deleteRewardItemButton = QtWidgets.QPushButton(rewardGroupBox)
        self.deleteRewardItemButton.setToolTip("Delete Item Reward")
        self.deleteRewardItemButton.setIcon(self.deleteIcon)
        self.deleteRewardItemButton.setFixedSize(buttonSize)
        self.newRewardItemButton = QtWidgets.QPushButton(rewardGroupBox)
        self.newRewardItemButton.setToolTip("New Item Reward")
        self.newRewardItemButton.setIcon(self.newIcon)
        self.newRewardItemButton.setFixedSize(buttonSize)
        self.nextRewardItemButton = QtWidgets.QPushButton(rewardGroupBox)
        self.nextRewardItemButton.setToolTip("Next Item Reward")
        self.nextRewardItemButton.setIcon(self.nextIcon)
        self.nextRewardItemButton.setFixedSize(buttonSize)

        itemTab = QtWidgets.QWidget()
        itemTab.setObjectName("item")
        self.itemModel = ItemModel(self.items, self.undoStack)
        self.itemView = ItemView(self.newItemIcon, self.deleteIcon, itemTab)
        self.itemView.setModel(self.itemModel)
        self.itemView.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        menuDuplicateScene = QtWidgets.QAction(self.window)
        menuDuplicateScene.setText("Scene")
        menuDuplicateScene.setShortcut("Ctrl+D")
        menuDuplicateAction = QtWidgets.QAction(self.window)
        menuDuplicateAction.setText("Action")
        menuDuplicateAction.setShortcut("Ctrl+Shift+D")
        menuSettings = QtWidgets.QAction(self.window)
        menuSettings.setText("Settings")
        menuReset = QtWidgets.QAction(self.window)
        menuReset.setText("Reset")
        menuReset.setToolTip("Discard all unsaved changes")
        menuReset.setShortcut("Ctrl+Shift+Delete")
        menuSave = QtWidgets.QAction(self.window)
        menuSave.setText("Save")
        menuSave.setShortcut("Ctrl+S")
        self.menuUndo = QtWidgets.QAction(self.window)
        self.menuUndo.setShortcut("Ctrl+Z")
        self.menuRedo = QtWidgets.QAction(self.window)
        self.menuRedo.setShortcut("Ctrl+Shift+Z")

        menuBar = QtWidgets.QMenuBar(self.window)
        menuFile = QtWidgets.QMenu(menuBar)
        menuFile.setTitle("File")
        menuFile.addAction(menuSave)
        menuFile.addAction(menuReset)
        menuEdit = QtWidgets.QMenu(menuBar)
        menuEdit.setTitle("Edit")
        menuEdit.addAction(self.menuUndo)
        menuEdit.addAction(self.menuRedo)
        menuDuplicate = QtWidgets.QMenu(menuEdit)
        menuDuplicate.setTitle("Duplicate")
        menuDuplicate.addAction(menuDuplicateScene)
        menuDuplicate.addAction(menuDuplicateAction)
        menuEdit.addAction(menuDuplicate.menuAction())
        menuEdit.addAction(menuSettings)
        menuBar.addMenu(menuFile)
        menuBar.addMenu(menuEdit)
        self.window.setMenuBar(menuBar)

        sceneNavLayout = QtWidgets.QHBoxLayout()
        sceneNavLayout.setAlignment(QtCore.Qt.AlignLeft)
        sceneNavLayout.addWidget(self.previousSceneButton)
        sceneNavLayout.addWidget(sceneIndexLabel)
        sceneNavLayout.addWidget(self.sceneNameComboBox)
        sceneNavLayout.addWidget(self.nextSceneButton)
        sceneNavLayout.addWidget(self.newSceneButton)
        sceneNavLayout.addWidget(self.deleteSceneButton)

        infoTabLayout = QtWidgets.QGridLayout(infoTab)
        infoTabLayout.addWidget(sceneNameLabel, 1, 0, 1, 1)
        infoTabLayout.addWidget(self.sceneNameInput, 1, 1, 1, 2)
        infoTabLayout.addWidget(imagePathLabel, 2, 0, 1, 1)
        infoTabLayout.addWidget(self.imagePathInput, 2, 1, 1, 1)
        infoTabLayout.addWidget(self.imagePathButton, 2, 2, 1, 1)
        infoTabLayout.addWidget(sceneDescriptionLabel, 3, 0, 1, 1)
        infoTabLayout.addWidget(self.sceneDescriptionInput, 3, 1, 1, 2)
        infoTab.setLayout(infoTabLayout)
        sceneTabWidget.addTab(infoTab, "Info")

        requirementAbilityNavLayout = QtWidgets.QHBoxLayout()
        requirementAbilityNavLayout.setAlignment(QtCore.Qt.AlignLeft)
        requirementAbilityNavLayout.addWidget(self.previousRequirementAbilityButton)
        requirementAbilityNavLayout.addWidget(self.requirementAbilityIndexLabel)
        requirementAbilityNavLayout.addWidget(self.nextRequirementAbilityButton)
        requirementAbilityNavLayout.addWidget(self.newRequirementAbilityButton)
        requirementAbilityNavLayout.addWidget(self.deleteRequirementAbilityButton)

        requirementItemNavLayout = QtWidgets.QHBoxLayout()
        requirementItemNavLayout.setAlignment(QtCore.Qt.AlignLeft)
        requirementItemNavLayout.addWidget(self.previousRequirementItemButton)
        requirementItemNavLayout.addWidget(self.requirementItemIndexLabel)
        requirementItemNavLayout.addWidget(self.nextRequirementItemButton)
        requirementItemNavLayout.addWidget(self.newRequirementItemButton)
        requirementItemNavLayout.addWidget(self.deleteRequirementItemButton)

        requirementGroupBoxLayout = QtWidgets.QGridLayout(requirementGroupBox)
        requirementGroupBoxLayout.addLayout(requirementAbilityNavLayout, 0, 0, 1, 1)
        requirementGroupBoxLayout.addWidget(requirementAbilityLabel, 0, 1, 1, 1)
        requirementGroupBoxLayout.addWidget(self.requirementAbilityComboBox, 0, 2, 1, 1)
        requirementGroupBoxLayout.addWidget(requirementAbilityScoreLabel, 0, 3, 1, 1)
        requirementGroupBoxLayout.addWidget(self.requirementAbilityScoreInput, 0, 4, 1, 1)
        requirementGroupBoxLayout.addLayout(requirementItemNavLayout, 1, 0, 1, 1)
        requirementGroupBoxLayout.addWidget(requirementItemIdLabel, 1, 1, 1, 1)
        requirementGroupBoxLayout.addWidget(self.requirementItemNameComboBox, 1, 2, 1, 1)
        requirementGroupBoxLayout.addWidget(requirementItemQtyLabel, 1, 3, 1, 1)
        requirementGroupBoxLayout.addWidget(self.requirementItemQtyInput, 1, 4, 1, 1)
        requirementGroupBox.setLayout(requirementGroupBoxLayout)

        rewardItemNavLayout = QtWidgets.QHBoxLayout()
        rewardItemNavLayout.setAlignment(QtCore.Qt.AlignLeft)
        rewardItemNavLayout.addWidget(self.previousRewardItemButton)
        rewardItemNavLayout.addWidget(self.rewardItemIndexLabel)
        rewardItemNavLayout.addWidget(self.nextRewardItemButton)
        rewardItemNavLayout.addWidget(self.newRewardItemButton)
        rewardItemNavLayout.addWidget(self.deleteRewardItemButton)

        rewardGroupBoxLayout = QtWidgets.QGridLayout(rewardGroupBox)
        rewardGroupBoxLayout.addWidget(rewardExpLabel, 0, 1, 1, 1)
        rewardGroupBoxLayout.addWidget(self.rewardExpInput, 0, 2, 1, 1)
        rewardGroupBoxLayout.addLayout(rewardItemNavLayout, 1, 0, 1, 1)
        rewardGroupBoxLayout.addWidget(rewardItemIdLabel, 1, 1, 1, 1)
        rewardGroupBoxLayout.addWidget(self.rewardItemNameComboBox, 1, 2, 1, 1)
        rewardGroupBoxLayout.addWidget(rewardItemQtyLabel, 1, 3, 1, 1)
        rewardGroupBoxLayout.addWidget(self.rewardItemQtyInput, 1, 4, 1, 1)
        rewardGroupBox.setLayout(rewardGroupBoxLayout)

        actionNavLayout = QtWidgets.QHBoxLayout()
        actionNavLayout.setAlignment(QtCore.Qt.AlignLeft)
        actionNavLayout.addWidget(self.previousActionButton)
        actionNavLayout.addWidget(self.actionIndexLabel)
        actionNavLayout.addWidget(self.nextActionButton)
        actionNavLayout.addWidget(self.newActionButton)
        actionNavLayout.addWidget(self.deleteActionButton)

        actionGroupBoxLayout = QtWidgets.QGridLayout(actionTab)
        actionGroupBoxLayout.addLayout(actionNavLayout, 0, 0, 1, 1)
        actionGroupBoxLayout.addWidget(actionDescriptionLabel, 0, 1, 1, 1)
        actionGroupBoxLayout.addWidget(self.actionDescriptionInput, 0, 2, 1, 1)
        actionGroupBoxLayout.addWidget(actionGoToLabel, 0, 3, 1, 1)
        actionGroupBoxLayout.addWidget(self.actionGoToComboBox, 0, 4, 1, 1)
        actionGroupBoxLayout.addWidget(actionConsequenceLabel, 1, 1, 1, 1)
        actionGroupBoxLayout.addWidget(self.actionConsequenceInput, 1, 2, 1, 1)
        actionGroupBoxLayout.addWidget(actionSecretLabel, 1, 3, 1, 1)
        actionGroupBoxLayout.addWidget(self.actionSecretCheck, 1, 4, 1, 1)
        actionGroupBoxLayout.addWidget(disableOnSelectLabel, 2, 1, 1, 1)
        actionGroupBoxLayout.addWidget(self.disableOnSelectCheck, 2, 2, 1, 1)
        actionGroupBoxLayout.addWidget(removeOnSelectLabel, 2, 3, 1, 1)
        actionGroupBoxLayout.addWidget(self.removeOnSelectCheck, 2, 4, 1, 1)
        actionGroupBoxLayout.addWidget(requirementGroupBox, 3, 0, 1, 5)
        actionGroupBoxLayout.addWidget(rewardGroupBox, 4, 0, 1, 5)
        actionTab.setLayout(actionGroupBoxLayout)
        sceneTabWidget.addTab(actionTab, "Actions")

        sceneTabCentralLayout = QtWidgets.QVBoxLayout()
        sceneTabCentralLayout.addLayout(sceneNavLayout)
        sceneTabCentralLayout.addWidget(sceneTabWidget)
        sceneTabCentralWidget.setLayout(sceneTabCentralLayout)
        self.centralTabWidget.addTab(sceneTabCentralWidget, "Scenes")

        itemTabLayout = QtWidgets.QGridLayout(itemTab)
        itemTabLayout.addWidget(self.itemView, 0, 0, 1, 1)
        itemTab.setLayout(itemTabLayout)
        self.centralTabWidget.addTab(itemTab, "Item")

        centralLayout = QtWidgets.QGridLayout(centralWidget)
        centralLayout.addWidget(self.centralTabWidget, 0, 0, 1, 1)
        centralWidget.setLayout(centralLayout)
        self.window.setCentralWidget(centralWidget)

        self.settingsUi = UiSettings(QtWidgets.QMainWindow())
        self.settingsUi.connect(get_item_path=partial(self.__getattribute__, "itemDatabasePath"),
                                get_scene_path=partial(self.__getattribute__, "sceneDatabasePath"),
                                set_item_path=self.setItemDatabasePath,
                                set_scene_path=self.setSceneDatabasePath)

        self.centralTabWidget.currentChanged.connect(self.refresh)
        self.sceneNameInput.textEdited.connect(partial(self.set, "scene._name", self.sceneNameInput))
        self.imagePathInput.textEdited.connect(partial(self.set, "scene._imagePath", self.imagePathInput))
        self.imagePathButton.clicked.connect(self.pickImageFile)
        self.sceneDescriptionInput.textChanged.connect(
            partial(self.set, "scene._description", self.sceneDescriptionInput))
        self.actionGoToComboBox.textActivated.connect(partial(self.set, "action._id", self.actionGoToComboBox, int))
        self.actionDescriptionInput.textEdited.connect(
            partial(self.set, "action._description", self.actionDescriptionInput))
        self.actionConsequenceInput.textEdited.connect(
            partial(self.set, "action._consequence", self.actionConsequenceInput))
        self.actionSecretCheck.clicked.connect(partial(self.set, "action._secret", self.actionSecretCheck))
        self.disableOnSelectCheck.clicked.connect(
            partial(self.set, "action._disableOnSelect", self.disableOnSelectCheck))
        self.removeOnSelectCheck.clicked.connect(partial(self.set, "action._removeOnSelect", self.removeOnSelectCheck))
        self.requirementAbilityComboBox.textActivated.connect(
            partial(self.set, "action.requirement.ability.name", self.requirementAbilityComboBox))
        self.requirementAbilityScoreInput.textEdited.connect(
            partial(self.set, "action.requirement.ability.score", self.requirementAbilityScoreInput, int))
        self.requirementItemNameComboBox.textActivated.connect(
            partial(self.set, "action.requirement.item.id", self.requirementItemNameComboBox, int))
        self.requirementItemQtyInput.textEdited.connect(
            partial(self.set, "action.requirement.item.quantity", self.requirementItemQtyInput, int))
        self.rewardExpInput.textEdited.connect(partial(self.set, "action.reward.experience", self.rewardExpInput, int))
        self.rewardItemNameComboBox.textActivated.connect(partial(self.set, "action.reward.item.id",
                                                          self.rewardItemNameComboBox,
                                                          int))
        self.rewardItemQtyInput.textEdited.connect(
            partial(self.set, "action.reward.item.quantity", self.rewardItemQtyInput, int))

        self.sceneNameComboBox.textActivated.connect(partial(self.setSceneIndex, self.sceneNameComboBox))
        self.previousRequirementAbilityButton.clicked.connect(partial(self.previous, "requirement ability"))
        self.previousRequirementItemButton.clicked.connect(partial(self.previous, "requirement item"))
        self.previousRewardItemButton.clicked.connect(partial(self.previous, "reward item"))
        self.previousActionButton.clicked.connect(partial(self.previous, "action"))
        self.previousSceneButton.clicked.connect(partial(self.previous, "scene"))
        self.nextRequirementAbilityButton.clicked.connect(partial(self.next, "requirement ability"))
        self.nextRequirementItemButton.clicked.connect(partial(self.next, "requirement item"))
        self.nextRewardItemButton.clicked.connect(partial(self.next, "reward item"))
        self.nextActionButton.clicked.connect(partial(self.next, "action"))
        self.nextSceneButton.clicked.connect(partial(self.next, "scene"))
        self.deleteRequirementAbilityButton.clicked.connect(partial(self.delete, "requirement ability"))
        self.deleteRequirementItemButton.clicked.connect(partial(self.delete, "requirement item"))
        self.deleteRewardItemButton.clicked.connect(partial(self.delete, "reward item"))
        self.deleteActionButton.clicked.connect(partial(self.delete, "action"))
        self.deleteSceneButton.clicked.connect(partial(self.delete, "scene"))
        self.newRequirementAbilityButton.clicked.connect(partial(self.new, "requirement ability"))
        self.newRequirementItemButton.clicked.connect(partial(self.new, "requirement item"))
        self.newRewardItemButton.clicked.connect(partial(self.new, "reward item"))
        self.newActionButton.clicked.connect(partial(self.new, "action"))
        self.newSceneButton.clicked.connect(partial(self.new, "scene"))
        self.itemModel.layoutChanged.connect(self.updateItemNameComboBoxes)
        self.itemModel.layoutChanged.connect(self.refresh)
        menuDuplicateAction.triggered.connect(partial(self.duplicate, "action"))
        menuDuplicateScene.triggered.connect(partial(self.duplicate, "scene"))
        menuSettings.triggered.connect(self.settingsUi.refresh)
        menuSettings.triggered.connect(self.settingsUi.show)
        menuReset.triggered.connect(self.reset)
        menuReset.triggered.connect(self.refresh)
        menuSave.triggered.connect(self.saveAll)
        self.menuUndo.triggered.connect(self.undo)
        self.menuRedo.triggered.connect(self.redo)
        QtCore.QMetaObject.connectSlotsByName(self.window)

    def delete(self, context: str):
        callback = None
        deleteIndex = None
        data: list = None
        if context == "scene":
            deleteIndex = self.sceneIndex
            data = self.scenes
            callback = self.updateSceneNameComboBoxes
        elif context == "action":
            deleteIndex = self.actionIndex
            data = self.scenes[self.sceneIndex].actions
        elif context == "requirement ability":
            deleteIndex = self.requirementAbilityIndex
            data = self.scenes[self.sceneIndex].actions[self.actionIndex].requirement.abilities
        elif context == "requirement item":
            deleteIndex = self.requirementItemIndex
            data = self.scenes[self.sceneIndex].actions[self.actionIndex].requirement.items
        elif context == "reward item":
            deleteIndex = self.rewardItemIndex
            data = self.scenes[self.sceneIndex].actions[self.actionIndex].reward.items

        if deleteIndex is not None and data:
            self.previous(context)
            description = "Delete {}".format(context.capitalize())
            self.undoStack.push(UndoDelete(data, deleteIndex, description, callback))
        self.refresh()

    def duplicate(self, target: str):
        if len(self.scenes) < 1:
            return
        scene = self.scenes[self.sceneIndex]
        if target == "scene":
            duplicateScene = copy.deepcopy(scene)
            self.sceneIndex = len(self.scenes)
            self.undoStack.push(UndoNew(self.scenes, self.sceneIndex, duplicateScene, "Duplicate Scene", self.updateSceneNameComboBoxes))
        else:
            actions = scene.actions
            if not actions:
                return
            duplicateAction = copy.deepcopy(actions[self.actionIndex])
            self.actionIndex = len(actions)
            self.undoStack.push(UndoNew(actions, self.actionIndex, duplicateAction, "Duplicate Action"))
        self.refresh()

    @staticmethod
    def load(path: str):
        if not exists(path):
            return []
        with open(path, 'r') as file:
            return jsonpickle.decode(file.read())

    @staticmethod
    def loadConfig():
        if not exists(Editor.configPath):
            return
        with open(Editor.configPath, 'r') as file:
            data = jsonpickle.decode(file.read())
            Editor.__path_items = data["itemPath"]
            Editor.__path_scenes = data["scenePath"]

    def new(self, context: str):
        description = "New {}".format(context.capitalize())
        if context == "scene":
            self.sceneIndex = len(self.scenes)
            self.actionIndex = 0
            self.requirementAbilityIndex = 0
            self.requirementItemIndex = 0
            self.rewardItemIndex = 0
            newScene = Scene(actions=[])
            self.undoStack.push(UndoNew(self.scenes, self.sceneIndex, newScene, description, self.updateSceneNameComboBoxes))
        elif context == "action":
            actions = self.scenes[self.sceneIndex].actions
            self.actionIndex = len(actions)
            self.requirementAbilityIndex = 0
            self.requirementItemIndex = 0
            self.rewardItemIndex = 0
            newAction = Action(requirement=Requirement([], []), reward=Reward(10, []))
            self.undoStack.push(UndoNew(actions, self.actionIndex, newAction, description))
        elif context == "requirement ability":
            abilities = self.scenes[self.sceneIndex].actions[self.actionIndex].requirement.abilities
            if len(abilities) >= len(self.__ability_names):
                return
            self.requirementAbilityIndex = len(abilities)
            newAbility = Ability("dexterity")
            self.undoStack.push(UndoNew(abilities, self.requirementAbilityIndex, newAbility, description))
        elif context.__contains__("item"):
            if len(self.items) <= 0:
                title = "Error: No Existing Items"
                message = "There must be at least 1 item created in the 'Item' tab before requirements & rewards can use them."
                self.popup(title, message)
            elif context.__contains__("requirement"):
                requirementItems = self.scenes[self.sceneIndex].actions[self.actionIndex].requirement.items
                self.requirementItemIndex = len(requirementItems)
                newReqItem = ItemRef(0, 1)
                self.undoStack.push(UndoNew(requirementItems, self.requirementItemIndex, newReqItem, description))
            elif context.__contains__("reward"):
                rewardItems = self.scenes[self.sceneIndex].actions[self.actionIndex].reward.items
                self.rewardItemIndex = len(rewardItems)
                newRewardItem = ItemRef(0, 1)
                self.undoStack.push(UndoNew(rewardItems, self.rewardItemIndex, newRewardItem, description))
        self.refresh()

    def next(self, context: str):
        if context == "scene" and self.sceneIndex < len(self.scenes) - 1:
            self.sceneIndex += 1
            self.actionIndex = 0
            self.requirementAbilityIndex = 0
            self.requirementItemIndex = 0
            self.rewardItemIndex = 0
        elif context == "action" and self.actionIndex < len(self.scenes[self.sceneIndex].actions) - 1:
            self.actionIndex += 1
            self.requirementAbilityIndex = 0
            self.requirementItemIndex = 0
            self.rewardItemIndex = 0
        elif context == "requirement ability" and self.requirementAbilityIndex < len(
                self.scenes[self.sceneIndex].actions[self.actionIndex].requirement.abilities) - 1:
            self.requirementAbilityIndex += 1
        elif context == "requirement item" and self.requirementItemIndex < len(
                self.scenes[self.sceneIndex].actions[self.actionIndex].requirement.items) - 1:
            self.requirementItemIndex += 1
        elif context == "reward item" and self.rewardItemIndex < len(
                self.scenes[self.sceneIndex].actions[self.actionIndex].reward.items) - 1:
            self.rewardItemIndex += 1
        self.refresh()

    def pickImageFile(self):
        imagePath = "Data/Images/Scene"
        imageFilter = "Image File (*.png)"
        dialogOutput = QtWidgets.QFileDialog.getOpenFileName(self.window, "Select Image", imagePath, imageFilter)
        if dialogOutput:
            path = dialogOutput[0]
            dataIndex = path.find("Data")
            if 0 <= path.find("TextRPG") < dataIndex:
                path = path[dataIndex:]
                self.imagePathInput.setText(path)
                self.imagePathInput.textEdited.emit(path)
                return
        title = "Error: Invalid Image Selection"
        message = "The '{}' must be within the game directory '{}'.".format(imageFilter, imagePath)
        self.popup(title, message)

    def popup(self, title: str, message: str):
        icon = QtWidgets.QMessageBox.Warning
        buttons = QtWidgets.QMessageBox.Ok
        messageBox = QtWidgets.QMessageBox(icon, title, message, buttons, self.window)
        messageBox.accepted.connect(messageBox.close)
        messageBox.exec()

    def previous(self, context: str):
        if context == "scene" and self.sceneIndex > 0:
            self.sceneIndex -= 1
            self.actionIndex = 0
            self.requirementAbilityIndex = 0
            self.requirementItemIndex = 0
            self.rewardItemIndex = 0
        elif context == "action" and self.actionIndex > 0:
            self.actionIndex -= 1
            self.requirementAbilityIndex = 0
            self.requirementItemIndex = 0
            self.rewardItemIndex = 0
        elif context == "requirement ability" and self.requirementAbilityIndex > 0:
            self.requirementAbilityIndex -= 1
        elif context == "requirement item" and self.requirementItemIndex > 0:
            self.requirementItemIndex -= 1
        elif context == "reward item" and self.rewardItemIndex > 0:
            self.rewardItemIndex -= 1
        self.refresh()

    def redo(self):
        context = self.undoStack.redoText().lower().replace("redo ", "")
        self.undoStack.redo()
        function = self.next
        if context.__contains__("delete"):
            function = self.previous
        context = context[context.find(" ") + 1:]
        function(context)
        self.refresh()

    def refresh(self):
        undoText = "Undo"
        redoText = "Redo"
        if self.undoStack.canUndo():
            undoText += " {}".format(self.undoStack.undoText())
        if self.undoStack.canRedo():
            redoText += " {}".format(self.undoStack.redoText())
        self.menuUndo.setEnabled(self.undoStack.canUndo())
        self.menuUndo.setText(undoText)
        self.menuRedo.setEnabled(self.undoStack.canRedo())
        self.menuRedo.setText(redoText)

        if self.centralTabWidget.currentIndex() == 0:
            scene: Scene = None
            sceneAvailable = bool(self.scenes and self.sceneIndex < len(self.scenes))
            sceneIndex = 0
            sceneNameText = "-"
            imagePathText = "-"
            sceneDescription = "-"
            if sceneAvailable:
                scene = self.scenes[self.sceneIndex]
                sceneIndex = self.sceneIndex
                sceneNameText = scene.name
                imagePathText = scene.imagePath
                sceneDescription = scene.description
            self.sceneNameComboBox.setCurrentIndex(sceneIndex)
            self.sceneNameInput.setText(sceneNameText)
            self.imagePathInput.setText(imagePathText)
            self.sceneDescriptionInput.setText(sceneDescription)

            action: Action = None
            actionAvailable = bool(sceneAvailable and self.actionIndex < len(scene.actions))
            actionIndexText = "-"
            actionDescriptionText = "-"
            actionConsequenceText = "-"
            actionId = 0
            secret = False
            disableOnSelect = False
            removeOnSelect = False
            if actionAvailable:
                action = scene.actions[self.actionIndex]
                actionIndexText = "Action {}".format(str(self.actionIndex))
                actionDescriptionText = action.description
                actionConsequenceText = action.consequence
                actionId = max(0, min(len(self.scenes), action.id))
                actionId += self.__numberOfReservedActions
                secret = action.secret
                disableOnSelect = action.disableOnSelect
                removeOnSelect = action.removeOnSelect
            self.actionIndexLabel.setText(actionIndexText)
            self.actionDescriptionInput.setText(actionDescriptionText)
            self.actionConsequenceInput.setText(actionConsequenceText)
            self.actionGoToComboBox.setCurrentIndex(actionId)
            self.actionSecretCheck.setChecked(secret)
            self.disableOnSelectCheck.setChecked(disableOnSelect)
            self.removeOnSelectCheck.setChecked(removeOnSelect)

            requirement = action.requirement if actionAvailable else None
            requirementAbilityAvailable = bool(
                requirement and requirement.abilities and self.requirementAbilityIndex < len(requirement.abilities))
            requirementAbilityIndexText = "-"
            requirementAbilityText = self.__ability_names[0]
            requirementScoreText = "-"
            if requirementAbilityAvailable:
                ability = requirement.abilities[self.requirementAbilityIndex]
                requirementAbilityIndexText = "Ability {}".format(self.requirementAbilityIndex)
                requirementAbilityText = ability.name
                requirementScoreText = str(ability.score)
            self.requirementAbilityIndexLabel.setText(requirementAbilityIndexText)
            self.requirementAbilityComboBox.setCurrentText(requirementAbilityText)
            self.requirementAbilityScoreInput.setText(requirementScoreText)

            requirementItemAvailable = bool(
                len(self.items) > 0 and requirement and requirement.items and self.requirementItemIndex < len(
                    requirement.items))
            requirementItemIndexText = "-"
            requirementItemId = 0
            requirementItemQtyText = "-"
            if requirementItemAvailable:
                requiredItem = requirement.items[self.requirementItemIndex]
                requirementItemIndexText = "Item {}".format(self.requirementItemIndex)
                requirementItemId = requiredItem.id
                requirementItemQtyText = str(requiredItem.quantity)
            self.requirementItemIndexLabel.setText(requirementItemIndexText)
            self.requirementItemNameComboBox.setCurrentIndex(requirementItemId)
            self.requirementItemQtyInput.setText(requirementItemQtyText)

            reward = action.reward if actionAvailable else None
            rewardExperienceAvailable = bool(reward and reward.experience is not None)
            rewardExpText = "-"
            if rewardExperienceAvailable:
                rewardExpText = str(reward.experience)
            self.rewardExpInput.setText(rewardExpText)

            rewardItemAvailable = bool(
                len(self.items) > 0 and reward and reward.items and self.rewardItemIndex < len(reward.items))
            rewardItemIndexText = "-"
            rewardItemId = 0
            rewardItemQtyText = "-"
            if rewardItemAvailable:
                rewardItem = reward.items[self.rewardItemIndex]
                rewardItemIndexText = "Item {}".format(self.rewardItemIndex)
                rewardItemId = rewardItem.id
                rewardItemQtyText = str(rewardItem.quantity)
            self.rewardItemIndexLabel.setText(rewardItemIndexText)
            self.rewardItemNameComboBox.setCurrentIndex(rewardItemId)
            self.rewardItemQtyInput.setText(rewardItemQtyText)

            self.previousSceneButton.setEnabled(sceneAvailable)
            self.sceneNameComboBox.setEnabled(sceneAvailable)
            self.nextSceneButton.setEnabled(sceneAvailable)
            self.deleteSceneButton.setEnabled(sceneAvailable)
            self.sceneNameInput.setEnabled(sceneAvailable)
            self.imagePathInput.setEnabled(sceneAvailable)
            self.imagePathButton.setEnabled(sceneAvailable)
            self.sceneDescriptionInput.setEnabled(sceneAvailable)

            self.newActionButton.setEnabled(sceneAvailable)
            self.previousActionButton.setEnabled(actionAvailable)
            self.nextActionButton.setEnabled(actionAvailable)
            self.deleteActionButton.setEnabled(actionAvailable)
            self.actionDescriptionInput.setEnabled(actionAvailable)
            self.actionConsequenceInput.setEnabled(actionAvailable)
            self.actionGoToComboBox.setEnabled(actionAvailable)
            self.actionSecretCheck.setEnabled(actionAvailable)
            self.disableOnSelectCheck.setEnabled(actionAvailable)
            self.removeOnSelectCheck.setEnabled(actionAvailable)

            self.newRequirementAbilityButton.setEnabled(actionAvailable)
            self.previousRequirementAbilityButton.setEnabled(requirementAbilityAvailable)
            self.nextRequirementAbilityButton.setEnabled(requirementAbilityAvailable)
            self.deleteRequirementAbilityButton.setEnabled(requirementAbilityAvailable)
            self.requirementAbilityComboBox.setEnabled(requirementAbilityAvailable)
            self.requirementAbilityScoreInput.setEnabled(requirementAbilityAvailable)

            self.newRequirementItemButton.setEnabled(actionAvailable)
            self.previousRequirementItemButton.setEnabled(requirementItemAvailable)
            self.nextRequirementItemButton.setEnabled(requirementItemAvailable)
            self.deleteRequirementItemButton.setEnabled(requirementItemAvailable)
            self.requirementItemNameComboBox.setEnabled(requirementItemAvailable)
            self.requirementItemQtyInput.setEnabled(requirementItemAvailable)

            self.newRewardItemButton.setEnabled(actionAvailable)
            self.rewardExpInput.setEnabled(actionAvailable)
            self.previousRewardItemButton.setEnabled(rewardItemAvailable)
            self.nextRewardItemButton.setEnabled(rewardItemAvailable)
            self.deleteRewardItemButton.setEnabled(rewardItemAvailable)
            self.rewardItemNameComboBox.setEnabled(rewardItemAvailable)
            self.rewardItemQtyInput.setEnabled(rewardItemAvailable)
        else:
            self.itemView.update()

    def reset(self, ui_is_initialized=True):
        self.actionIndex = 0
        self.sceneIndex = 0
        self.requirementAbilityIndex = 0
        self.requirementItemIndex = 0
        self.rewardItemIndex = 0

        self.items: list[Item] = self.load(self.itemDatabasePath)
        if not isinstance(self.items, list) or len(self.items) <= 0 or not isinstance(self.items[0], Item):
            self.popup("Database Error", "The Item database is either formatted incorrectly or does not exist.")
        if ui_is_initialized:
            self.updateItemNameComboBoxes()

        self.scenes: list[Scene] = self.load(self.sceneDatabasePath)
        if not isinstance(self.scenes, list) or len(self.scenes) <= 0 or not isinstance(self.scenes[0], Scene):
            self.popup("Database Error", "The Scene database is either formatted incorrectly or does not exist.")
        if ui_is_initialized:
            self.updateSceneNameComboBoxes()

    @staticmethod
    def save(path: str, data):
        with open(path, 'w') as file:
            file.write(jsonpickle.encode(data, indent=4))

    def saveAll(self):
        self.save(self.itemDatabasePath, self.items)
        self.save(self.sceneDatabasePath, self.scenes)
        self.saveConfig()
        self.undoStack.clear()
        self.refresh()

    def saveConfig(self):
        data = {"itemPath": self.itemDatabasePath, "scenePath": self.sceneDatabasePath}
        with open(self.configPath, 'w') as file:
            file.write(jsonpickle.encode(data, indent=4))

    def set(self, context: str, widget: any, value_type=str):
        if self.sceneIndex >= len(self.scenes):
            return
        attribute = context.split(".")[-1]
        scene = self.scenes[self.sceneIndex]
        target = scene
        if context.__contains__("requirement"):
            requirement = scene.actions[self.actionIndex].requirement
            if context.__contains__("ability"):
                target = requirement.abilities[self.requirementAbilityIndex]
            else:
                target = requirement.items[self.requirementItemIndex]
        elif context.__contains__("reward"):
            reward = scene.actions[self.actionIndex].reward
            if context.__contains__("item"):
                target = reward.items[self.rewardItemIndex]
            else:
                target = reward
        elif context.__contains__("action"):
            target = scene.actions[self.actionIndex]
        elif context.__contains__("self"):
            target = self

        if isinstance(widget, QtWidgets.QTextEdit):
            value = widget.toPlainText()
        elif isinstance(widget, QtWidgets.QCheckBox):
            value = widget.isChecked()
        elif isinstance(widget, QtWidgets.QComboBox):
            if value_type == str:
                value = widget.currentText()
            elif value_type == int:
                value = widget.currentIndex()
                if context.__contains__("action"):
                    value -= self.__numberOfReservedActions
        else:
            value = widget.text()
            if value_type == int and len(value) > 0 and value != "-":
                value = int(value)

        target.__setattr__(attribute, value)

    def setItemDatabasePath(self, path: str):
        self.itemDatabasePath = path

    def setSceneDatabasePath(self, path: str):
        self.sceneDatabasePath = path

    def setSceneIndex(self, widget: QtWidgets.QComboBox):
        self.sceneIndex = widget.currentIndex()
        self.refresh()

    def undo(self):
        context = self.undoStack.undoText().lower().replace("undo ", "")
        self.undoStack.undo()
        function = self.previous
        if context.__contains__("delete"):
            function = self.next
        if context.__contains__("item"):
            self.updateItemNameComboBoxes()
        context = context[context.find(" ") + 1:]
        function(context)
        self.refresh()

    def updateSceneNameComboBoxes(self):
        sceneNames = []
        for scene in self.scenes:
            sceneNames.append(scene.name)
        self.sceneNameComboBox.clear()
        self.sceneNameComboBox.addItems(sceneNames)
        self.actionGoToComboBox.clear()
        self.actionGoToComboBox.addItems(["None", "Previous"])
        self.actionGoToComboBox.addItems(sceneNames)

    def updateItemNameComboBoxes(self):
        itemNames = []
        for item in self.items:
            itemNames.append(item.name)
        self.requirementItemNameComboBox.clear()
        self.requirementItemNameComboBox.addItems(itemNames)
        self.rewardItemNameComboBox.clear()
        self.rewardItemNameComboBox.addItems(itemNames)
