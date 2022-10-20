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


class Editor(QtCore.QObject):
    __path_scenes = "Data/scenes.json"
    __path_items = "Data/items.json"
    __ability_names = ["dexterity", "intelligence", "strength", "will", "wisdom"]

    def __init__(self):
        super().__init__()
        self.items: list[Item] = self.load(self.__path_items)
        self.scenes: list[Scene] = self.load(self.__path_scenes)
        self.actionIndex = 0
        self.sceneIndex = 0
        self.requirementAbilityIndex = 0
        self.requirementItemIndex = 0
        self.rewardItemIndex = 0
        app = QtWidgets.QApplication(sys.argv)
        self.__initializeUi()
        sys.exit(app.exec())

    def __initializeUi(self):
        self.checkIcon = QtGui.QIcon("Data/Images/UI/check.png")
        self.deleteIcon = QtGui.QIcon("Data/Images/UI/x.png")
        self.editorIcon = QtGui.QIcon("Data/Images/UI/editor.png")
        self.folderIcon = QtGui.QIcon("Data/Images/UI/folder.png")
        self.gearIcon = QtGui.QIcon("Data/Images/UI/gear.png")
        self.newIcon = QtGui.QIcon("Data/Images/UI/plus.png")
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

        sceneTab = QtWidgets.QTabWidget(self.centralTabWidget)
        sceneTab.setObjectName("scene")
        infoTab = QtWidgets.QWidget(sceneTab)
        sceneNameLabel = QtWidgets.QLabel(infoTab)
        sceneNameLabel.setText("Name:")
        sceneNameLabel.setToolTip("Name of the scene.")
        self.sceneNameInput = QtWidgets.QLineEdit(infoTab)
        enterDescriptionLabel = QtWidgets.QLabel(infoTab)
        enterDescriptionLabel.setText("Enter:")
        enterDescriptionLabel.setToolTip("Text displayed when entering the scene.")
        self.enterDescriptionInput = QtWidgets.QTextEdit(infoTab)
        exitDescriptionLabel = QtWidgets.QLabel(infoTab)
        exitDescriptionLabel.setText("Exit:")
        exitDescriptionLabel.setToolTip("Text displayed when exiting the scene.")
        self.exitDescriptionInput = QtWidgets.QTextEdit(infoTab)
        imagePathLabel = QtWidgets.QLabel(infoTab)
        imagePathLabel.setText("Image:")
        imagePathLabel.setToolTip("The image to display for this scene.")
        self.imagePathInput = QtWidgets.QLineEdit(infoTab)
        self.imagePathButton = QtWidgets.QPushButton(infoTab)
        self.imagePathButton.setIcon(self.folderIcon)
        self.imagePathButton.setFixedSize(buttonSize)
        self.sceneIndexInput = QtWidgets.QLineEdit(infoTab)
        self.sceneIndexInput.setMaximumWidth(indexLabelWidth)
        self.sceneIndexInput.setAlignment(QtCore.Qt.AlignCenter)
        self.sceneIndexInput.setToolTip("Scene Index")
        self.previousSceneButton = QtWidgets.QPushButton(infoTab)
        self.previousSceneButton.setToolTip("Previous Scene")
        self.previousSceneButton.setIcon(self.previousIcon)
        self.previousSceneButton.setFixedSize(buttonSize)
        self.deleteSceneButton = QtWidgets.QPushButton(infoTab)
        self.deleteSceneButton.setToolTip("Delete Scene")
        self.deleteSceneButton.setIcon(self.deleteIcon)
        self.deleteSceneButton.setFixedSize(buttonSize)
        self.newSceneButton = QtWidgets.QPushButton(infoTab)
        self.newSceneButton.setToolTip("New Scene")
        self.newSceneButton.setIcon(self.newIcon)
        self.newSceneButton.setFixedSize(buttonSize)
        self.nextSceneButton = QtWidgets.QPushButton(infoTab)
        self.nextSceneButton.setToolTip("Next Scene")
        self.nextSceneButton.setIcon(self.nextIcon)
        self.nextSceneButton.setFixedSize(buttonSize)

        actionTab = QtWidgets.QWidget(sceneTab)
        actionTab.setObjectName("action")
        actionDescriptionLabel = QtWidgets.QLabel(actionTab)
        actionDescriptionLabel.setText("Description:")
        actionDescriptionLabel.setAlignment(QtCore.Qt.AlignRight)
        self.actionDescriptionInput = QtWidgets.QLineEdit(actionTab)
        actionIdTooltip = "< -1: scene index unaffected\n-1: go to previous scene\n>= 0: go to scene index"
        actionIdLabel = QtWidgets.QLabel(actionTab)
        actionIdLabel.setText("Id:")
        actionIdLabel.setToolTip(actionIdTooltip)
        actionIdLabel.setAlignment(QtCore.Qt.AlignRight)
        self.actionIdInput = QtWidgets.QLineEdit(actionTab)
        self.actionIdInput.setFixedWidth(indexLabelWidth)
        self.actionIdInput.setToolTip(actionIdTooltip)
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
        self.actionIndexInput = QtWidgets.QLineEdit(actionTab)
        self.actionIndexInput.setMaximumWidth(indexLabelWidth)
        self.actionIndexInput.setAlignment(QtCore.Qt.AlignCenter)
        self.actionIndexInput.setToolTip("Action Index")
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
        requirementScoreLabel = QtWidgets.QLabel(requirementGroupBox)
        requirementScoreLabel.setText("Ability Score:")
        requirementScoreLabel.setToolTip("Score required to take this action.")
        requirementScoreLabel.setAlignment(QtCore.Qt.AlignRight)
        self.requirementScoreInput = QtWidgets.QLineEdit(requirementGroupBox)
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
        itemIdTooltip = "Row number of the item in the 'Item' tab."
        requirementItemIdLabel = QtWidgets.QLabel(requirementGroupBox)
        requirementItemIdLabel.setText("Item Id:")
        requirementItemIdLabel.setToolTip(itemIdTooltip)
        requirementItemIdLabel.setAlignment(QtCore.Qt.AlignRight)
        self.requirementItemIdInput = QtWidgets.QLineEdit(requirementGroupBox)
        self.requirementItemIdInput.setToolTip(itemIdTooltip)
        requirementItemQtyLabel = QtWidgets.QLabel(requirementGroupBox)
        requirementItemQtyLabel.setText("Item Quantity:")
        requirementItemQtyLabel.setToolTip("Quantity of item required to take this action.")
        requirementItemQtyLabel.setAlignment(QtCore.Qt.AlignRight)
        self.requirementItemQtyInput = QtWidgets.QLineEdit(requirementGroupBox)
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
        rewardItemIdLabel = QtWidgets.QLabel(rewardGroupBox)
        rewardItemIdLabel.setText("Item Id:")
        rewardItemIdLabel.setToolTip(itemIdTooltip)
        rewardItemIdLabel.setAlignment(QtCore.Qt.AlignRight)
        self.rewardItemIdInput = QtWidgets.QLineEdit(rewardGroupBox)
        rewardItemQtyLabel = QtWidgets.QLabel(rewardGroupBox)
        rewardItemQtyLabel.setText("Item Quantity:")
        rewardItemQtyLabel.setToolTip("Quantity of item rewarded for taking this action.")
        rewardItemQtyLabel.setAlignment(QtCore.Qt.AlignRight)
        self.rewardItemQtyInput = QtWidgets.QLineEdit(rewardGroupBox)
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
        self.itemView = ItemView(self.newIcon, self.deleteIcon, itemTab)
        self.itemView.setModel(self.itemModel)
        self.itemView.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        menuDuplicateScene = QtWidgets.QAction(self.window)
        menuDuplicateScene.setText("Scene")
        menuDuplicateScene.setShortcut("Ctrl+D")
        menuDuplicateAction = QtWidgets.QAction(self.window)
        menuDuplicateAction.setText("Action")
        menuDuplicateAction.setShortcut("Ctrl+Shift+D")
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
        menuEdit = QtWidgets.QMenu(menuBar)
        menuEdit.setTitle("Edit")
        menuEdit.addAction(self.menuUndo)
        menuEdit.addAction(self.menuRedo)
        menuDuplicate = QtWidgets.QMenu(menuEdit)
        menuDuplicate.setTitle("Duplicate")
        menuDuplicate.addAction(menuDuplicateScene)
        menuDuplicate.addAction(menuDuplicateAction)
        menuEdit.addAction(menuDuplicate.menuAction())
        menuBar.addMenu(menuFile)
        menuBar.addMenu(menuEdit)
        self.window.setMenuBar(menuBar)

        sceneNavLayout = QtWidgets.QGridLayout()
        sceneNavLayout.addWidget(self.previousSceneButton, 0, 0, 1, 1)
        sceneNavLayout.addWidget(self.sceneIndexInput, 0, 1, 1, 1)
        sceneNavLayout.addWidget(self.nextSceneButton, 0, 2, 1, 1)
        sceneNavLayout.addWidget(self.newSceneButton, 0, 3, 1, 1)
        sceneNavLayout.addWidget(self.deleteSceneButton, 0, 4, 1, 1)

        sceneGroupBoxLayout = QtWidgets.QGridLayout(infoTab)
        sceneGroupBoxLayout.addLayout(sceneNavLayout, 0, 0, 1, 2)
        sceneGroupBoxLayout.addWidget(sceneNameLabel, 1, 0, 1, 1)
        sceneGroupBoxLayout.addWidget(self.sceneNameInput, 1, 1, 1, 2)
        sceneGroupBoxLayout.addWidget(imagePathLabel, 2, 0, 1, 1)
        sceneGroupBoxLayout.addWidget(self.imagePathInput, 2, 1, 1, 1)
        sceneGroupBoxLayout.addWidget(self.imagePathButton, 2, 2, 1, 1)
        sceneGroupBoxLayout.addWidget(enterDescriptionLabel, 3, 0, 1, 1)
        sceneGroupBoxLayout.addWidget(self.enterDescriptionInput, 3, 1, 1, 2)
        sceneGroupBoxLayout.addWidget(exitDescriptionLabel, 4, 0, 1, 1)
        sceneGroupBoxLayout.addWidget(self.exitDescriptionInput, 4, 1, 1, 2)
        infoTab.setLayout(sceneGroupBoxLayout)
        sceneTab.addTab(infoTab, "Info")

        hSpacerItem = QtWidgets.QSpacerItem(buttonSize.width(), buttonSize.height(), Qt.QSizePolicy.Policy.Expanding)
        requirementAbilityNavLayout = QtWidgets.QHBoxLayout()
        requirementAbilityNavLayout.addWidget(self.previousRequirementAbilityButton)
        requirementAbilityNavLayout.addWidget(self.requirementAbilityIndexLabel)
        requirementAbilityNavLayout.addWidget(self.nextRequirementAbilityButton)
        requirementAbilityNavLayout.addWidget(self.newRequirementAbilityButton)
        requirementAbilityNavLayout.addWidget(self.deleteRequirementAbilityButton)
        requirementAbilityNavLayout.addItem(hSpacerItem)

        hSpacerItem = QtWidgets.QSpacerItem(buttonSize.width(), buttonSize.height(), Qt.QSizePolicy.Policy.Expanding)
        requirementItemNavLayout = QtWidgets.QHBoxLayout()
        requirementItemNavLayout.addWidget(self.previousRequirementItemButton)
        requirementItemNavLayout.addWidget(self.requirementItemIndexLabel)
        requirementItemNavLayout.addWidget(self.nextRequirementItemButton)
        requirementItemNavLayout.addWidget(self.newRequirementItemButton)
        requirementItemNavLayout.addWidget(self.deleteRequirementItemButton)
        requirementItemNavLayout.addItem(hSpacerItem)

        requirementGroupBoxLayout = QtWidgets.QGridLayout(requirementGroupBox)
        requirementGroupBoxLayout.addLayout(requirementAbilityNavLayout, 0, 0, 1, 1)
        requirementGroupBoxLayout.addWidget(requirementAbilityLabel, 0, 1, 1, 1)
        requirementGroupBoxLayout.addWidget(self.requirementAbilityComboBox, 0, 2, 1, 1)
        requirementGroupBoxLayout.addWidget(requirementScoreLabel, 0, 3, 1, 1)
        requirementGroupBoxLayout.addWidget(self.requirementScoreInput, 0, 4, 1, 1)
        requirementGroupBoxLayout.addLayout(requirementItemNavLayout, 1, 0, 1, 1)
        requirementGroupBoxLayout.addWidget(requirementItemIdLabel, 1, 1, 1, 1)
        requirementGroupBoxLayout.addWidget(self.requirementItemIdInput, 1, 2, 1, 1)
        requirementGroupBoxLayout.addWidget(requirementItemQtyLabel, 1, 3, 1, 1)
        requirementGroupBoxLayout.addWidget(self.requirementItemQtyInput, 1, 4, 1, 1)
        requirementGroupBox.setLayout(requirementGroupBoxLayout)

        hSpacerItem = QtWidgets.QSpacerItem(buttonSize.width(), buttonSize.height(), Qt.QSizePolicy.Policy.Expanding)
        rewardItemNavLayout = QtWidgets.QHBoxLayout()
        rewardItemNavLayout.addWidget(self.previousRewardItemButton)
        rewardItemNavLayout.addWidget(self.rewardItemIndexLabel)
        rewardItemNavLayout.addWidget(self.nextRewardItemButton)
        rewardItemNavLayout.addWidget(self.newRewardItemButton)
        rewardItemNavLayout.addWidget(self.deleteRewardItemButton)
        rewardItemNavLayout.addItem(hSpacerItem)

        rewardGroupBoxLayout = QtWidgets.QGridLayout(rewardGroupBox)
        rewardGroupBoxLayout.addWidget(rewardExpLabel, 0, 1, 1, 1)
        rewardGroupBoxLayout.addWidget(self.rewardExpInput, 0, 2, 1, 1)
        rewardGroupBoxLayout.addLayout(rewardItemNavLayout, 1, 0, 1, 1)
        rewardGroupBoxLayout.addWidget(rewardItemIdLabel, 1, 1, 1, 1)
        rewardGroupBoxLayout.addWidget(self.rewardItemIdInput, 1, 2, 1, 1)
        rewardGroupBoxLayout.addWidget(rewardItemQtyLabel, 1, 3, 1, 1)
        rewardGroupBoxLayout.addWidget(self.rewardItemQtyInput, 1, 4, 1, 1)
        rewardGroupBox.setLayout(rewardGroupBoxLayout)

        hSpacerItem = QtWidgets.QSpacerItem(buttonSize.width(), buttonSize.height(), Qt.QSizePolicy.Policy.Expanding)
        actionNavLayout = QtWidgets.QHBoxLayout()
        actionNavLayout.addWidget(self.previousActionButton)
        actionNavLayout.addWidget(self.actionIndexInput)
        actionNavLayout.addWidget(self.nextActionButton)
        actionNavLayout.addWidget(self.newActionButton)
        actionNavLayout.addWidget(self.deleteActionButton)
        actionNavLayout.addItem(hSpacerItem)

        actionGroupBoxLayout = QtWidgets.QGridLayout(actionTab)
        actionGroupBoxLayout.addLayout(actionNavLayout, 0, 0, 1, 1)
        actionGroupBoxLayout.addWidget(actionDescriptionLabel, 0, 1, 1, 1)
        actionGroupBoxLayout.addWidget(self.actionDescriptionInput, 0, 2, 1, 1)
        actionGroupBoxLayout.addWidget(actionIdLabel, 0, 3, 1, 1)
        actionGroupBoxLayout.addWidget(self.actionIdInput, 0, 4, 1, 1)
        actionGroupBoxLayout.addWidget(disableOnSelectLabel, 1, 1, 1, 1)
        actionGroupBoxLayout.addWidget(self.disableOnSelectCheck, 1, 2, 1, 1)
        actionGroupBoxLayout.addWidget(removeOnSelectLabel, 1, 3, 1, 1)
        actionGroupBoxLayout.addWidget(self.removeOnSelectCheck, 1, 4, 1, 1)
        actionGroupBoxLayout.addWidget(requirementGroupBox, 2, 0, 1, 5)
        actionGroupBoxLayout.addWidget(rewardGroupBox, 3, 0, 1, 5)
        actionTab.setLayout(actionGroupBoxLayout)

        sceneTab.addTab(actionTab, "Actions")
        self.centralTabWidget.addTab(sceneTab, "Scene")

        itemTabLayout = QtWidgets.QGridLayout(itemTab)
        itemTabLayout.addWidget(self.itemView, 0, 0, 1, 1)
        itemTab.setLayout(itemTabLayout)
        self.centralTabWidget.addTab(itemTab, "Item")

        centralLayout = QtWidgets.QGridLayout(centralWidget)
        centralLayout.addWidget(self.centralTabWidget, 0, 0, 1, 1)
        centralWidget.setLayout(centralLayout)
        self.window.setCentralWidget(centralWidget)

        self.centralTabWidget.currentChanged.connect(self.refresh)
        self.sceneNameInput.editingFinished.connect(partial(self.set, "scene.name", self.sceneNameInput))
        self.imagePathInput.editingFinished.connect(partial(self.set, "scene.imagePath", self.imagePathInput))
        self.imagePathButton.clicked.connect(self.pickImageFile)
        self.enterDescriptionInput.textChanged.connect(
            partial(self.set, "scene.enterDescription", self.enterDescriptionInput))
        self.exitDescriptionInput.textChanged.connect(
            partial(self.set, "scene.exitDescription", self.exitDescriptionInput))
        self.actionIdInput.editingFinished.connect(partial(self.set, "action._id", self.actionIdInput))
        self.actionDescriptionInput.editingFinished.connect(
            partial(self.set, "action.description", self.actionDescriptionInput))
        self.disableOnSelectCheck.clicked.connect(
            partial(self.set, "action.disableOnSelect", self.disableOnSelectCheck))
        self.removeOnSelectCheck.clicked.connect(partial(self.set, "action._removeOnSelect", self.removeOnSelectCheck))
        self.requirementAbilityComboBox.currentTextChanged.connect(
            partial(self.set, "action.requirement.ability.name", self.requirementAbilityComboBox))
        self.requirementScoreInput.editingFinished.connect(
            partial(self.set, "action.requirement.ability.score", self.requirementScoreInput))
        self.requirementItemIdInput.editingFinished.connect(
            partial(self.set, "action.requirement.item.id", self.requirementItemIdInput))
        self.requirementItemQtyInput.editingFinished.connect(
            partial(self.set, "action.requirement.item.quantity", self.requirementItemQtyInput))
        self.rewardExpInput.editingFinished.connect(partial(self.set, "action.reward.experience", self.rewardExpInput))
        self.rewardItemIdInput.editingFinished.connect(
            partial(self.set, "action.reward.item.id", self.rewardItemIdInput))
        self.rewardItemQtyInput.editingFinished.connect(
            partial(self.set, "action.reward.item.quantity", self.rewardItemQtyInput))
        self.sceneIndexInput.editingFinished.connect(partial(self.setIndex, "scene", self.sceneIndexInput))
        self.actionIndexInput.editingFinished.connect(partial(self.setIndex, "action", self.actionIndexInput))
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
        self.itemModel.layoutChanged.connect(self.refresh)
        menuDuplicateAction.triggered.connect(partial(self.duplicate, "action"))
        menuDuplicateScene.triggered.connect(partial(self.duplicate, "scene"))
        menuSave.triggered.connect(self.saveAll)
        self.menuUndo.triggered.connect(self.undo)
        self.menuRedo.triggered.connect(self.redo)
        QtCore.QMetaObject.connectSlotsByName(self.window)

        self.refresh()
        self.window.showMaximized()

    def delete(self, context: str):
        deleteIndex = None
        data: list = None
        callback = None
        if context == "scene":
            deleteIndex = self.sceneIndex
            data = self.scenes
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
            self.undoStack.push(UndoDelete(data, deleteIndex, description))
        self.refresh()

    def duplicate(self, target: str):
        if len(self.scenes) < 1:
            return
        scene = self.scenes[self.sceneIndex]
        if target == "scene":
            duplicateScene = copy.deepcopy(scene)
            self.sceneIndex = len(self.scenes)
            self.scenes.append(duplicateScene)
        else:
            actions = scene.actions
            if not actions:
                return
            duplicateAction = copy.deepcopy(actions[self.actionIndex])
            self.actionIndex = len(actions)
            actions.append(duplicateAction)
        self.refresh()

    @staticmethod
    def load(path: str):
        if not exists(path):
            return []
        with open(path, 'r') as file:
            return jsonpickle.decode(file.read())

    def new(self, context: str):
        description = "New {}".format(context.capitalize())
        if context == "scene":
            self.sceneIndex = len(self.scenes)
            self.actionIndex = 0
            self.requirementAbilityIndex = 0
            self.requirementItemIndex = 0
            self.rewardItemIndex = 0
            newScene = Scene(actions=[])
            self.undoStack.push(UndoNew(self.scenes, self.sceneIndex, newScene, description))
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
            self.requirementAbilityIndex = len(abilities)
            newAbility = Ability("dexterity")
            self.undoStack.push(UndoNew(abilities, self.requirementAbilityIndex, newAbility, description))
        elif context.__contains__("item"):
            if len(self.items) <= 0:
                self.noExistingItemsDialog()
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

    def noExistingItemsDialog(self):
        title = "Error: No Existing Items"
        message = "There must be at least 1 item created in the 'Item' tab before requirements & rewards can use them."
        icon = QtWidgets.QMessageBox.Warning
        buttons = QtWidgets.QMessageBox.Ok
        messageBox = QtWidgets.QMessageBox(icon, title, message, buttons, self.window)
        messageBox.exec()

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
                self.imagePathInput.editingFinished.emit()
                return
        title = "Error: Invalid Image Selection"
        message = "The '{}' must be within the game directory '{}'.".format(imageFilter, imagePath)
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
            sceneIndexText = "-"
            sceneNameText = "-"
            imagePathText = "-"
            enterText = "-"
            exitText = "-"
            if sceneAvailable:
                scene = self.scenes[self.sceneIndex]
                sceneIndexText = str(self.sceneIndex)
                sceneNameText = scene.name
                imagePathText = scene.imagePath
                enterText = scene.enterDescription
                exitText = scene.exitDescription
            self.sceneIndexInput.setText(sceneIndexText)
            self.sceneNameInput.setText(sceneNameText)
            self.imagePathInput.setText(imagePathText)
            self.enterDescriptionInput.setText(enterText)
            self.exitDescriptionInput.setText(exitText)

            action: Action = None
            actionAvailable = bool(sceneAvailable and self.actionIndex < len(scene.actions))
            actionIndexText = "-"
            actionDescriptionText = "-"
            actionIdInputText = "-"
            disableOnSelect = False
            removeOnSelect = False
            if actionAvailable:
                action = scene.actions[self.actionIndex]
                actionIndexText = str(self.actionIndex)
                actionDescriptionText = action.description
                actionIdInputText = str(action.id)
                disableOnSelect = action.disableOnSelect
                removeOnSelect = action.removeOnSelect
            self.actionIndexInput.setText(actionIndexText)
            self.actionDescriptionInput.setText(actionDescriptionText)
            self.actionIdInput.setText(actionIdInputText)
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
            self.requirementScoreInput.setText(requirementScoreText)

            requirementItemAvailable = bool(
                len(self.items) > 0 and requirement and requirement.items and self.requirementItemIndex < len(
                    requirement.items))
            requirementItemIndexText = "-"
            requirementItemIdText = "-"
            requirementItemQtyText = "-"
            if requirementItemAvailable:
                requiredItem = requirement.items[self.requirementItemIndex]
                requirementItemIndexText = "Item {}".format(self.requirementItemIndex)
                requirementItemIdText = str(requiredItem.id)
                requirementItemQtyText = str(requiredItem.quantity)
            self.requirementItemIndexLabel.setText(requirementItemIndexText)
            self.requirementItemIdInput.setText(requirementItemIdText)
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
            rewardItemIdText = "-"
            rewardItemQtyText = "-"
            if rewardItemAvailable:
                rewardItem = reward.items[self.rewardItemIndex]
                rewardItemIndexText = "Item {}".format(self.rewardItemIndex)
                rewardItemIdText = str(rewardItem.id)
                rewardItemQtyText = str(rewardItem.quantity)
            self.rewardItemIndexLabel.setText(rewardItemIndexText)
            self.rewardItemIdInput.setText(rewardItemIdText)
            self.rewardItemQtyInput.setText(rewardItemQtyText)

            self.previousSceneButton.setEnabled(sceneAvailable)
            self.sceneIndexInput.setEnabled(sceneAvailable)
            self.nextSceneButton.setEnabled(sceneAvailable)
            self.deleteSceneButton.setEnabled(sceneAvailable)
            self.sceneNameInput.setEnabled(sceneAvailable)
            self.imagePathInput.setEnabled(sceneAvailable)
            self.imagePathButton.setEnabled(sceneAvailable)
            self.enterDescriptionInput.setEnabled(sceneAvailable)
            self.exitDescriptionInput.setEnabled(sceneAvailable)

            self.newActionButton.setEnabled(sceneAvailable)
            self.previousActionButton.setEnabled(actionAvailable)
            self.actionIndexInput.setEnabled(actionAvailable)
            self.nextActionButton.setEnabled(actionAvailable)
            self.deleteActionButton.setEnabled(actionAvailable)
            self.actionDescriptionInput.setEnabled(actionAvailable)
            self.actionIdInput.setEnabled(actionAvailable)
            self.disableOnSelectCheck.setEnabled(actionAvailable)
            self.removeOnSelectCheck.setEnabled(actionAvailable)

            self.newRequirementAbilityButton.setEnabled(actionAvailable)
            self.previousRequirementAbilityButton.setEnabled(requirementAbilityAvailable)
            self.nextRequirementAbilityButton.setEnabled(requirementAbilityAvailable)
            self.deleteRequirementAbilityButton.setEnabled(requirementAbilityAvailable)
            self.requirementAbilityComboBox.setEnabled(requirementAbilityAvailable)
            self.requirementScoreInput.setEnabled(requirementAbilityAvailable)

            self.newRequirementItemButton.setEnabled(actionAvailable)
            self.previousRequirementItemButton.setEnabled(requirementItemAvailable)
            self.nextRequirementItemButton.setEnabled(requirementItemAvailable)
            self.deleteRequirementItemButton.setEnabled(requirementItemAvailable)
            self.requirementItemIdInput.setEnabled(requirementItemAvailable)
            self.requirementItemQtyInput.setEnabled(requirementItemAvailable)

            self.newRewardItemButton.setEnabled(actionAvailable)
            self.rewardExpInput.setEnabled(actionAvailable)
            self.previousRewardItemButton.setEnabled(rewardItemAvailable)
            self.nextRewardItemButton.setEnabled(rewardItemAvailable)
            self.deleteRewardItemButton.setEnabled(rewardItemAvailable)
            self.rewardItemIdInput.setEnabled(rewardItemAvailable)
            self.rewardItemQtyInput.setEnabled(rewardItemAvailable)
        else:
            self.itemView.update()

    @staticmethod
    def save(path: str, data):
        # args = {"indent": 4, "sort_keys": True}
        with open(path, 'w') as file:
            file.write(jsonpickle.encode(data, indent=4))

    def saveAll(self):
        self.save(self.__path_items, self.items)
        self.save(self.__path_scenes, self.scenes)
        self.undoStack.clear()
        self.refresh()

    def set(self, context: str, widget):
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
            value = widget.currentText()
        else:
            value = widget.text()
        target.__setattr__(attribute, value)

    def setIndex(self, context: str, widget: QtWidgets.QLineEdit):
        try:
            value = int(widget.text()) - 1
        except ValueError:
            value = 0
        value = max(value, 0)
        if context.__contains__("action"):
            value = min(value, len(self.scenes[self.sceneIndex].actions) - 1)
            self.actionIndex = value
        else:
            value = min(value, len(self.scenes) - 1)
            self.sceneIndex = value
        widget.setText(str(value))
        self.refresh()

    def undo(self):
        context = self.undoStack.undoText().lower().replace("undo ", "")
        self.undoStack.undo()
        function = self.previous
        if context.__contains__("delete"):
            function = self.next
        context = context[context.find(" ") + 1:]
        function(context)
        self.refresh()
