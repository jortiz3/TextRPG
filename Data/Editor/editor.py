import copy
import sys
from functools import partial
from os.path import exists
from typing import Union, Type

import jsons
from PyQt5 import Qt, QtCore, QtGui, QtWidgets

from Data.Character.ability import Ability
from Data.Editor.item_model import ItemModel
from Data.Editor.item_view import ItemView
from Data.Editor.undo_delete import UndoDelete
from Data.Editor.undo_new import UndoNew
from Data.Item.item_reference import ItemRef
from Data.Scene.scene import Scene
from Data.Scene.action import Action
from Data.Scene.requirement import Requirement
from Data.Scene.reward import Reward
from Data.Item.item import Item


class Editor(QtCore.QObject):
    __path_scenes = "Data/scenes.json"
    __path_items = "Data/items.json"

    def __init__(self):
        super().__init__()
        self.items: list[Item] = self.load(self.__path_items, list[Item])
        self.scenes: list[Scene] = self.load(self.__path_scenes, list[Scene])
        self.actionIndex = 0
        self.sceneIndex = 0
        self.itemIndex = 0
        self.requirementAbilityIndex = 0
        self.requirementItemIndex = 0
        self.rewardItemIndex = 0
        app = QtWidgets.QApplication(sys.argv)
        self.__initializeUi()
        sys.exit(app.exec())

    def __initializeUi(self):
        checkIcon = QtGui.QIcon("Data/Images/UI/check.png")
        folderIcon = QtGui.QIcon("Data/Images/UI/folder.png")
        gearIcon = QtGui.QIcon("Data/Images/UI/gear.png")
        self.newIcon = QtGui.QIcon("Data/Images/UI/plus.png")
        nextIcon = QtGui.QIcon("Data/Images/UI/next.png")
        previousIcon = QtGui.QIcon("Data/Images/UI/previous.png")
        self.deleteIcon = QtGui.QIcon("Data/Images/UI/x.png")

        buttonSize = Qt.QSize(50, 25)
        indexLabelWidth = buttonSize.width() * 2
        navGroupBoxHeight = buttonSize.height() * 4

        self.window = QtWidgets.QMainWindow()
        self.window.setMinimumSize(800, 400)
        self.window.setStyleSheet("font-size: 14pt")
        self.window.setWindowTitle("Text RPG - Editor")
        centralWidget = QtWidgets.QWidget(self.window)
        self.centralTabWidget = QtWidgets.QTabWidget(centralWidget)

        self.undoStack = QtWidgets.QUndoStack(self.window)

        sceneTabWidget = QtWidgets.QTabWidget(self.centralTabWidget)
        sceneTabWidget.setObjectName("scene")
        infoTab = QtWidgets.QWidget(sceneTabWidget)
        sceneGroupBox = QtWidgets.QGroupBox(infoTab)
        sceneNameLabel = QtWidgets.QLabel(sceneGroupBox)
        sceneNameLabel.setText("Name:")
        sceneNameLabel.setToolTip("Name of the scene.")
        self.sceneNameInput = QtWidgets.QLineEdit(sceneGroupBox)
        enterDescriptionLabel = QtWidgets.QLabel(sceneGroupBox)
        enterDescriptionLabel.setText("Enter:")
        enterDescriptionLabel.setToolTip("Text displayed when entering the scene.")
        self.enterDescriptionInput = QtWidgets.QTextEdit(sceneGroupBox)
        exitDescriptionLabel = QtWidgets.QLabel(sceneGroupBox)
        exitDescriptionLabel.setText("Exit:")
        exitDescriptionLabel.setToolTip("Text displayed when exiting the scene.")
        self.exitDescriptionInput = QtWidgets.QTextEdit(sceneGroupBox)
        imagePathLabel = QtWidgets.QLabel(sceneGroupBox)
        imagePathLabel.setText("Image:")
        imagePathLabel.setToolTip("The image to display for this scene.")
        self.imagePathInput = QtWidgets.QLineEdit(sceneGroupBox)
        self.imagePathButton = QtWidgets.QPushButton(sceneGroupBox)
        self.imagePathButton.setIcon(folderIcon)
        self.imagePathButton.setFixedSize(buttonSize)
        sceneNavGroupBox = QtWidgets.QGroupBox(centralWidget)
        sceneNavGroupBox.setTitle("Navigation")
        sceneNavGroupBox.setFixedHeight(navGroupBoxHeight)
        self.sceneIndexInput = QtWidgets.QLineEdit(sceneNavGroupBox)
        self.sceneIndexInput.setMaximumWidth(indexLabelWidth)
        self.sceneIndexInput.setAlignment(QtCore.Qt.AlignCenter)
        self.previousSceneButton = QtWidgets.QPushButton(sceneNavGroupBox)
        self.previousSceneButton.setToolTip("Previous Scene")
        self.previousSceneButton.setIcon(previousIcon)
        self.previousSceneButton.setFixedSize(buttonSize)
        self.deleteSceneButton = QtWidgets.QPushButton(sceneNavGroupBox)
        self.deleteSceneButton.setToolTip("Delete Scene")
        self.deleteSceneButton.setIcon(self.deleteIcon)
        self.deleteSceneButton.setFixedSize(buttonSize)
        self.newSceneButton = QtWidgets.QPushButton(sceneNavGroupBox)
        self.newSceneButton.setToolTip("New Scene")
        self.newSceneButton.setIcon(self.newIcon)
        self.newSceneButton.setFixedSize(buttonSize)
        self.nextSceneButton = QtWidgets.QPushButton(sceneNavGroupBox)
        self.nextSceneButton.setToolTip("Next Scene")
        self.nextSceneButton.setIcon(nextIcon)
        self.nextSceneButton.setFixedSize(buttonSize)

        actionTab = QtWidgets.QWidget(sceneTabWidget)
        actionGroupBox = QtWidgets.QGroupBox(actionTab)
        actionNavGroupBox = QtWidgets.QGroupBox(actionGroupBox)
        actionNavGroupBox.setTitle("Navigation")
        actionNavGroupBox.setFixedHeight(navGroupBoxHeight)
        actionDescriptionLabel = QtWidgets.QLabel(actionGroupBox)
        actionDescriptionLabel.setText("Description:")
        self.actionDescriptionInput = QtWidgets.QLineEdit(actionGroupBox)
        actionIdLabel = QtWidgets.QLabel(actionGroupBox)
        actionIdLabel.setText("Id:")
        actionIdLabel.setToolTip("# < -1: scene index unaffected\n# == -1: go to previous scene\n# >= 0: go to scene "
                                 "index")
        self.actionIdInput = QtWidgets.QLineEdit(actionGroupBox)
        disableOnSelectLabel = QtWidgets.QLabel(actionGroupBox)
        disableOnSelectLabel.setText("Disable On Select:")
        self.disableOnSelectCheck = QtWidgets.QCheckBox(actionGroupBox)
        removeOnSelectLabel = QtWidgets.QLabel(actionGroupBox)
        removeOnSelectLabel.setText("Remove On Select:")
        self.removeOnSelectCheck = QtWidgets.QCheckBox(actionGroupBox)
        self.actionIndexInput = QtWidgets.QLineEdit(actionTab)
        self.actionIndexInput.setMaximumWidth(indexLabelWidth)
        self.actionIndexInput.setAlignment(QtCore.Qt.AlignCenter)
        self.previousActionButton = QtWidgets.QPushButton(actionTab)
        self.previousActionButton.setToolTip("Previous Action")
        self.previousActionButton.setIcon(previousIcon)
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
        self.nextActionButton.setIcon(nextIcon)
        self.nextActionButton.setFixedSize(buttonSize)

        requirementGroupBox = QtWidgets.QGroupBox(actionTab)
        requirementGroupBox.setTitle("Requirements")
        requirementAbilityLabel = QtWidgets.QLabel(requirementGroupBox)
        requirementAbilityLabel.setText("Ability Name:")
        requirementAbilityLabel.setToolTip("Ability required to take this action.")
        self.requirementAbilityInput = QtWidgets.QLineEdit(requirementGroupBox)
        requirementScoreLabel = QtWidgets.QLabel(requirementGroupBox)
        requirementScoreLabel.setText("Ability Score:")
        requirementScoreLabel.setToolTip("Score required to take this action.")
        self.requirementScoreInput = QtWidgets.QLineEdit(requirementGroupBox)
        self.requirementAbilityIndexLabel = QtWidgets.QLabel(requirementGroupBox)
        self.requirementAbilityIndexLabel.setMaximumWidth(indexLabelWidth)
        self.requirementAbilityIndexLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.previousRequirementAbilityButton = QtWidgets.QPushButton(requirementGroupBox)
        self.previousRequirementAbilityButton.setToolTip("Previous Ability Requirement")
        self.previousRequirementAbilityButton.setIcon(previousIcon)
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
        self.nextRequirementAbilityButton.setIcon(nextIcon)
        self.nextRequirementAbilityButton.setFixedSize(buttonSize)
        requirementItemIdLabel = QtWidgets.QLabel(requirementGroupBox)
        requirementItemIdLabel.setText("Item Id:")
        requirementItemIdLabel.setToolTip("Database id for the item required to take this action.")
        self.requirementItemIdInput = QtWidgets.QLineEdit(requirementGroupBox)
        requirementItemQtyLabel = QtWidgets.QLabel(requirementGroupBox)
        requirementItemQtyLabel.setText("Item Quantity:")
        requirementItemQtyLabel.setToolTip("Quantity of item required to take this action.")
        self.requirementItemQtyInput = QtWidgets.QLineEdit(requirementGroupBox)
        self.requirementItemIndexLabel = QtWidgets.QLabel(requirementGroupBox)
        self.requirementItemIndexLabel.setMaximumWidth(indexLabelWidth)
        self.requirementItemIndexLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.previousRequirementItemButton = QtWidgets.QPushButton(requirementGroupBox)
        self.previousRequirementItemButton.setToolTip("Previous Item Requirement")
        self.previousRequirementItemButton.setIcon(previousIcon)
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
        self.nextRequirementItemButton.setIcon(nextIcon)
        self.nextRequirementItemButton.setFixedSize(buttonSize)

        rewardGroupBox = QtWidgets.QGroupBox(sceneGroupBox)
        rewardGroupBox.setTitle("Rewards")
        rewardExpLabel = QtWidgets.QLabel(rewardGroupBox)
        rewardExpLabel.setText("Experience:")
        rewardExpLabel.setToolTip("Experience rewarded for taking this action.")
        self.rewardExpInput = QtWidgets.QLineEdit(rewardGroupBox)
        rewardItemIdLabel = QtWidgets.QLabel(rewardGroupBox)
        rewardItemIdLabel.setText("Item Id:")
        rewardItemIdLabel.setToolTip("Database id for the item rewarded for taking this action.")
        self.rewardItemIdInput = QtWidgets.QLineEdit(rewardGroupBox)
        rewardItemQtyLabel = QtWidgets.QLabel(rewardGroupBox)
        rewardItemQtyLabel.setText("Item Quantity:")
        rewardItemQtyLabel.setToolTip("Quantity of item rewarded for taking this action.")
        self.rewardItemQtyInput = QtWidgets.QLineEdit(rewardGroupBox)
        self.rewardItemIndexLabel = QtWidgets.QLabel(rewardGroupBox)
        self.rewardItemIndexLabel.setMaximumWidth(indexLabelWidth)
        self.rewardItemIndexLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.previousRewardItemButton = QtWidgets.QPushButton(rewardGroupBox)
        self.previousRewardItemButton.setToolTip("Previous Item Reward")
        self.previousRewardItemButton.setIcon(previousIcon)
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
        self.nextRewardItemButton.setIcon(nextIcon)
        self.nextRewardItemButton.setFixedSize(buttonSize)

        itemTab = QtWidgets.QWidget()
        itemTab.setObjectName("item")
        self.itemModel = ItemModel(self.items, self.deleteIcon)
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

        sceneNavLayout = QtWidgets.QGridLayout(sceneNavGroupBox)
        sceneNavLayout.addWidget(self.previousSceneButton, 0, 0, 1, 1)
        sceneNavLayout.addWidget(self.sceneIndexInput, 0, 1, 1, 1)
        sceneNavLayout.addWidget(self.nextSceneButton, 0, 2, 1, 1)
        sceneNavLayout.addWidget(self.deleteSceneButton, 0, 3, 1, 1)
        sceneNavLayout.addWidget(self.newSceneButton, 0, 4, 1, 1)
        sceneNavGroupBox.setLayout(sceneNavLayout)

        sceneGroupBoxLayout = QtWidgets.QGridLayout(sceneGroupBox)
        sceneGroupBoxLayout.addWidget(sceneNameLabel, 0, 0, 1, 1)
        sceneGroupBoxLayout.addWidget(self.sceneNameInput, 0, 1, 1, 2)
        sceneGroupBoxLayout.addWidget(imagePathLabel, 1, 0, 1, 1)
        sceneGroupBoxLayout.addWidget(self.imagePathInput, 1, 1, 1, 1)
        sceneGroupBoxLayout.addWidget(self.imagePathButton, 1, 2, 1, 1)
        sceneGroupBoxLayout.addWidget(enterDescriptionLabel, 2, 0, 1, 1)
        sceneGroupBoxLayout.addWidget(self.enterDescriptionInput, 2, 1, 1, 2)
        sceneGroupBoxLayout.addWidget(exitDescriptionLabel, 3, 0, 1, 1)
        sceneGroupBoxLayout.addWidget(self.exitDescriptionInput, 3, 1, 1, 2)
        sceneGroupBox.setLayout(sceneGroupBoxLayout)

        infoTabLayout = QtWidgets.QGridLayout(sceneGroupBox)
        infoTabLayout.addWidget(sceneNavGroupBox, 0, 0, 1, 1)
        infoTabLayout.addWidget(sceneGroupBox, 1, 0, 1, 1)
        infoTab.setLayout(infoTabLayout)
        sceneTabWidget.addTab(infoTab, "Info")

        requirementGroupBoxLayout = QtWidgets.QGridLayout(requirementGroupBox)
        requirementGroupBoxLayout.addWidget(requirementAbilityLabel, 0, 0, 1, 1)
        requirementGroupBoxLayout.addWidget(self.requirementAbilityInput, 0, 1, 1, 1)
        requirementGroupBoxLayout.addWidget(requirementScoreLabel, 0, 2, 1, 1)
        requirementGroupBoxLayout.addWidget(self.requirementScoreInput, 0, 3, 1, 1)
        requirementGroupBoxLayout.addWidget(self.previousRequirementAbilityButton, 1, 0, 1, 1)
        requirementGroupBoxLayout.addWidget(self.requirementAbilityIndexLabel, 1, 1, 1, 1)
        requirementGroupBoxLayout.addWidget(self.nextRequirementAbilityButton, 1, 2, 1, 1)
        requirementGroupBoxLayout.addWidget(self.deleteRequirementAbilityButton, 1, 3, 1, 1)
        requirementGroupBoxLayout.addWidget(self.newRequirementAbilityButton, 1, 4, 1, 1)
        requirementGroupBoxLayout.addWidget(requirementItemIdLabel, 2, 0, 1, 1)
        requirementGroupBoxLayout.addWidget(self.requirementItemIdInput, 2, 1, 1, 1)
        requirementGroupBoxLayout.addWidget(requirementItemQtyLabel, 2, 2, 1, 1)
        requirementGroupBoxLayout.addWidget(self.requirementItemQtyInput, 2, 3, 1, 1)
        requirementGroupBoxLayout.addWidget(self.previousRequirementItemButton, 3, 0, 1, 1)
        requirementGroupBoxLayout.addWidget(self.requirementItemIndexLabel, 3, 1, 1, 1)
        requirementGroupBoxLayout.addWidget(self.nextRequirementItemButton, 3, 2, 1, 1)
        requirementGroupBoxLayout.addWidget(self.deleteRequirementItemButton, 3, 3, 1, 1)
        requirementGroupBoxLayout.addWidget(self.newRequirementItemButton, 3, 4, 1, 1)
        requirementGroupBox.setLayout(requirementGroupBoxLayout)

        rewardGroupBoxLayout = QtWidgets.QGridLayout(rewardGroupBox)
        rewardGroupBoxLayout.addWidget(rewardExpLabel, 0, 0, 1, 1)
        rewardGroupBoxLayout.addWidget(self.rewardExpInput, 0, 1, 1, 1)
        rewardGroupBoxLayout.addWidget(rewardItemIdLabel, 1, 0, 1, 1)
        rewardGroupBoxLayout.addWidget(self.rewardItemIdInput, 1, 1, 1, 1)
        rewardGroupBoxLayout.addWidget(rewardItemQtyLabel, 1, 2, 1, 1)
        rewardGroupBoxLayout.addWidget(self.rewardItemQtyInput, 1, 3, 1, 1)
        rewardGroupBoxLayout.addWidget(self.previousRewardItemButton, 2, 0, 1, 1)
        rewardGroupBoxLayout.addWidget(self.rewardItemIndexLabel, 2, 1, 1, 1)
        rewardGroupBoxLayout.addWidget(self.nextRewardItemButton, 2, 2, 1, 1)
        rewardGroupBoxLayout.addWidget(self.deleteRewardItemButton, 2, 3, 1, 1)
        rewardGroupBoxLayout.addWidget(self.newRewardItemButton, 2, 4, 1, 1)
        rewardGroupBox.setLayout(rewardGroupBoxLayout)

        actionNavLayout = QtWidgets.QGridLayout(actionNavGroupBox)
        actionNavLayout.addWidget(self.previousActionButton, 0, 0, 1, 1)
        actionNavLayout.addWidget(self.actionIndexInput, 0, 1, 1, 1)
        actionNavLayout.addWidget(self.nextActionButton, 0, 2, 1, 1)
        actionNavLayout.addWidget(self.deleteActionButton, 0, 3, 1, 1)
        actionNavLayout.addWidget(self.newActionButton, 0, 4, 1, 1)
        actionNavGroupBox.setLayout(actionNavLayout)

        actionGroupBoxLayout = QtWidgets.QGridLayout(actionGroupBox)
        actionGroupBoxLayout.addWidget(actionDescriptionLabel, 1, 0, 1, 1)
        actionGroupBoxLayout.addWidget(self.actionDescriptionInput, 1, 1, 1, 1)
        actionGroupBoxLayout.addWidget(actionIdLabel, 1, 2, 1, 1)
        actionGroupBoxLayout.addWidget(self.actionIdInput, 1, 3, 1, 1)
        actionGroupBoxLayout.addWidget(disableOnSelectLabel, 2, 0, 1, 1)
        actionGroupBoxLayout.addWidget(self.disableOnSelectCheck, 2, 1, 1, 1)
        actionGroupBoxLayout.addWidget(removeOnSelectLabel, 2, 2, 1, 1)
        actionGroupBoxLayout.addWidget(self.removeOnSelectCheck, 2, 3, 1, 1)
        actionGroupBoxLayout.addWidget(requirementGroupBox, 3, 0, 1, 4)
        actionGroupBoxLayout.addWidget(rewardGroupBox, 4, 0, 1, 4)
        actionGroupBox.setLayout(actionGroupBoxLayout)

        actionTabLayout = QtWidgets.QGridLayout(actionTab)
        actionTabLayout.addWidget(actionNavGroupBox, 0, 0, 1, 1)
        actionTabLayout.addWidget(actionGroupBox, 1, 0, 1, 1)
        actionTab.setLayout(actionTabLayout)
        sceneTabWidget.addTab(actionTab, "Actions")
        self.centralTabWidget.addTab(sceneTabWidget, "Scene")

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
        self.requirementAbilityInput.editingFinished.connect(
            partial(self.set, "action._requirement.ability.name", self.requirementAbilityInput))
        self.requirementScoreInput.editingFinished.connect(
            partial(self.set, "action._requirement.ability.score", self.requirementScoreInput))
        self.requirementItemIdInput.editingFinished.connect(
            partial(self.set, "action._requirement.item.id", self.requirementItemIdInput))
        self.requirementItemQtyInput.editingFinished.connect(
            partial(self.set, "action._requirement.item.quantity", self.requirementItemQtyInput))
        self.rewardExpInput.editingFinished.connect(partial(self.set, "action.reward.experience", self.rewardExpInput))
        self.rewardItemIdInput.editingFinished.connect(
            partial(self.set, "action._reward.item.id", self.rewardItemIdInput))
        self.rewardItemQtyInput.editingFinished.connect(
            partial(self.set, "action._reward.item.quantity", self.rewardItemQtyInput))
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
            data = self.scenes[self.sceneIndex].actions[self.actionIndex].requirement().abilities
        elif context == "requirement item":
            deleteIndex = self.requirementItemIndex
            data = self.scenes[self.sceneIndex].actions[self.actionIndex].requirement().items
        elif context == "reward item":
            deleteIndex = self.rewardItemIndex
            data = self.scenes[self.sceneIndex].actions[self.actionIndex].reward().items
        elif context == "item":
            deleteIndex = self.itemIndex
            data = self.items
            callback = self.itemModel.layoutChanged.emit

        if deleteIndex is not None and data:
            self.previous(context)
            description = "Delete {}".format(context.capitalize())
            self.undoStack.push(UndoDelete(data, deleteIndex, description))
            if callback:
                callback()
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
    def load(path: str, data_type: Type[list[Union[Item, Scene]]]):
        data: data_type = []
        if exists(path):
            with open(path, 'r') as file:
                data: data_type = jsons.loads(file.read())
        return data

    def new(self, context: str):
        description = "New {}".format(context.capitalize())
        if context == "scene":
            self.sceneIndex = len(self.scenes)
            newScene = Scene("New Scene", "New Enter Description", "You carry on...", "", [])
            self.undoStack.push(UndoNew(self.scenes, self.sceneIndex, newScene, description))
        elif context == "action":
            actions = self.scenes[self.sceneIndex].actions
            self.actionIndex = len(actions)
            newAction = Action(requirement=Requirement([], []), reward=Reward(0, []))
            self.undoStack.push(UndoNew(actions, self.actionIndex, newAction, description))
        elif context == "requirement ability":
            abilities = self.scenes[self.sceneIndex].actions[self.actionIndex].requirement().abilities
            self.requirementAbilityIndex = len(abilities)
            newAbility = Ability("dexterity")
            self.undoStack.push(UndoNew(abilities, self.requirementAbilityIndex, newAbility, description))
        elif context == "requirement item":
            requirementItems = self.scenes[self.sceneIndex].actions[self.actionIndex].requirement().items
            self.requirementItemIndex = len(requirementItems)
            newReqItem = ItemRef(0, 0)
            self.undoStack.push(UndoNew(requirementItems, self.requirementItemIndex, newReqItem, description))
        elif context == "reward item":
            rewardItems = self.scenes[self.sceneIndex].actions[self.actionIndex].reward().items
            self.rewardItemIndex = len(rewardItems)
            newRewardItem = ItemRef(0, 0)
            self.undoStack.push(UndoNew(rewardItems, self.rewardItemIndex, newRewardItem, description))
        elif context == "item":
            self.itemIndex = len(self.items)
            newItem = Item("New Item", "New Type")
            self.undoStack.push(UndoNew(self.items, self.itemIndex, newItem, description))
            self.itemModel.layoutChanged.emit()
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
                self.scenes[self.sceneIndex].actions[self.actionIndex].requirement().abilities) - 1:
            self.requirementAbilityIndex += 1
        elif context == "requirement item" and self.requirementItemIndex < len(
                self.scenes[self.sceneIndex].actions[self.actionIndex].requirement().items) - 1:
            self.requirementItemIndex += 1
        elif context == "reward item" and self.rewardItemIndex < len(
                self.scenes[self.sceneIndex].actions[self.actionIndex].reward().items) - 1:
            self.rewardItemIndex += 1
        elif context == "item" and self.itemIndex < len(self.items):
            self.itemIndex += 1
        self.refresh()

    def pickImageFile(self):
        dialogOutput = QtWidgets.QFileDialog.getOpenFileName(self.window, "Select Image", "Data/Images/Scene",
                                                             "Image Files (*.png)")
        if dialogOutput:
            path = dialogOutput[0]
            dataIndex = path.find("Data")
            if 0 <= path.find("TextRPG") < dataIndex:
                path = path[dataIndex:]
                self.imagePathInput.setText(path)
                self.imagePathInput.editingFinished.emit()

    def previous(self, context: str):
        if context == "scene" and self.sceneIndex > 0:
            self.sceneIndex -= 1
        elif context == "action" and self.actionIndex > 0:
            self.actionIndex -= 1
        elif context == "requirement ability" and self.requirementAbilityIndex > 0:
            self.requirementAbilityIndex -= 1
        elif context == "requirement item" and self.requirementItemIndex > 0:
            self.requirementItemIndex -= 1
        elif context == "reward item" and self.rewardItemIndex > 0:
            self.rewardItemIndex -= 1
        elif context == "item" and self.itemIndex > 0:
            self.itemIndex -= 1
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
            if sceneAvailable:
                scene = self.scenes[self.sceneIndex]
                self.sceneNameInput.setText(scene.name)
                self.imagePathInput.setText(scene.imagePath)
                self.enterDescriptionInput.setText(scene.enterDescription)
                self.exitDescriptionInput.setText(scene.exitDescription)
            action: Action = None
            actionAvailable = bool(sceneAvailable and self.actionIndex < len(scene.actions))
            if actionAvailable:
                action = scene.actions[self.actionIndex]
                self.actionDescriptionInput.setText(action.description())
                self.actionIdInput.setText(str(action.id()))
                self.disableOnSelectCheck.setChecked(action.disableOnSelect())
                self.removeOnSelectCheck.setChecked(action.removeOnSelect())

            requirement = action.requirement() if actionAvailable else None
            requirementAbilityAvailable = bool(
                requirement and requirement.abilities and self.requirementAbilityIndex < len(requirement.abilities))
            if requirementAbilityAvailable:
                ability = requirement.abilities[self.requirementAbilityIndex]
                self.requirementAbilityInput.setText(ability.name)
                self.requirementScoreInput.setText(str(ability.score))

            requirementItemAvailable = bool(
                requirement and requirement.items and self.requirementItemIndex < len(requirement.items))
            if requirementItemAvailable:
                requiredItem = requirement.items[self.requirementItemIndex]
                self.requirementItemIdInput.setText(str(requiredItem.id))
                self.requirementItemQtyInput.setText(str(requiredItem.quantity))

            reward = action.reward() if actionAvailable else None
            rewardExperienceAvailable = bool(reward and reward.experience is not None)
            if rewardExperienceAvailable:
                self.rewardExpInput.setText(str(reward.experience))

            rewardItemAvailable = bool(reward and reward.items and self.rewardItemIndex < len(reward.items))
            if rewardItemAvailable:
                rewardItem = reward.items[self.rewardItemIndex]
                self.rewardItemIdInput.setText(str(rewardItem.id))
                self.rewardItemQtyInput.setText(str(rewardItem.quantity))

            self.previousSceneButton.setEnabled(sceneAvailable)
            self.sceneIndexInput.setEnabled(sceneAvailable)
            self.sceneIndexInput.setText(str(self.sceneIndex + 1))
            self.nextSceneButton.setEnabled(sceneAvailable)
            self.deleteSceneButton.setEnabled(sceneAvailable)
            self.sceneNameInput.setEnabled(sceneAvailable)
            self.enterDescriptionInput.setEnabled(sceneAvailable)
            self.exitDescriptionInput.setEnabled(sceneAvailable)

            self.newActionButton.setEnabled(sceneAvailable)
            self.previousActionButton.setEnabled(actionAvailable)
            self.actionIndexInput.setEnabled(actionAvailable)
            self.actionIndexInput.setText(str(self.actionIndex + 1))
            self.nextActionButton.setEnabled(actionAvailable)
            self.deleteActionButton.setEnabled(actionAvailable)
            self.actionDescriptionInput.setEnabled(actionAvailable)
            self.actionIdInput.setEnabled(actionAvailable)
            self.disableOnSelectCheck.setEnabled(actionAvailable)
            self.removeOnSelectCheck.setEnabled(actionAvailable)

            self.requirementAbilityIndexLabel.setText("Ability {}".format(self.requirementAbilityIndex + 1))
            self.newRequirementAbilityButton.setEnabled(actionAvailable)
            self.previousRequirementAbilityButton.setEnabled(requirementAbilityAvailable)
            self.nextRequirementAbilityButton.setEnabled(requirementAbilityAvailable)
            self.deleteRequirementAbilityButton.setEnabled(requirementAbilityAvailable)
            self.requirementAbilityInput.setEnabled(requirementAbilityAvailable)
            self.requirementScoreInput.setEnabled(requirementAbilityAvailable)

            self.requirementItemIndexLabel.setText("Item {}".format(self.requirementItemIndex + 1))
            self.newRequirementItemButton.setEnabled(actionAvailable)
            self.previousRequirementItemButton.setEnabled(requirementItemAvailable)
            self.nextRequirementItemButton.setEnabled(requirementItemAvailable)
            self.deleteRequirementItemButton.setEnabled(requirementItemAvailable)
            self.requirementItemIdInput.setEnabled(requirementItemAvailable)
            self.requirementItemQtyInput.setEnabled(requirementItemAvailable)

            self.rewardItemIndexLabel.setText("Item {}".format(self.rewardItemIndex + 1))
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
        args = {"indent": 4, "sort_keys": True}
        with open(path, 'w') as file:
            file.write(jsons.dumps(data, jdkwargs=args, verbose=True))

    def saveAll(self):
        self.save(self.__path_items, self.items)
        self.save(self.__path_scenes, self.scenes)
        self.undoStack.clear()
        self.refresh()

    def set(self, context: str, widget):
        attribute = context.split(".")[-1]
        scene = self.scenes[self.sceneIndex]
        target = scene
        if context.__contains__("requirement"):
            requirement = scene.actions[self.actionIndex].requirement()
            if context.__contains__("ability"):
                target = requirement.abilities[self.requirementAbilityIndex]
            else:
                target = requirement.items[self.requirementItemIndex]
        elif context.__contains__("reward"):
            reward = scene.actions[self.actionIndex].reward()
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
