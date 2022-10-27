from functools import partial

from PyQt5 import QtCore, QtGui, QtWidgets

from Data.UI.ui import UI


class UiSettings(UI):
    def __init__(self, window: QtWidgets.QMainWindow):
        super().__init__(window, window_name="SettingsWindow", window_show_size=QtCore.QSize(400, 400),
                         window_title="Text RPG - Settings")
        self._centralWidget = QtWidgets.QWidget(window)
        self._itemDatabaseLabel = QtWidgets.QLabel(self._centralWidget)
        self._itemDatabaseLabel.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self._itemDatabaseLabel.setAlignment(QtCore.Qt.AlignCenter)
        self._itemFilePathLabel = QtWidgets.QLabel(self._centralWidget)
        self._itemFilePathLabel.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self._itemFilePathLabel.setAlignment(QtCore.Qt.AlignCenter)
        self._itemFilePathLabel.setFrameStyle(QtWidgets.QLabel.Box)
        self._itemFilePickerButton = QtWidgets.QPushButton(self._centralWidget)
        self._itemFilePickerButton.setFixedSize(self._defaultButtonSize)
        self._itemFilePickerButton.setIcon(self._folderIcon)

        self._sceneDatabaseLabel = QtWidgets.QLabel(self._centralWidget)
        self._sceneDatabaseLabel.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self._sceneDatabaseLabel.setAlignment(QtCore.Qt.AlignCenter)
        self._sceneFilePathLabel = QtWidgets.QLabel(self._centralWidget)
        self._sceneFilePathLabel.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self._sceneFilePathLabel.setAlignment(QtCore.Qt.AlignCenter)
        self._sceneFilePathLabel.setFrameStyle(QtWidgets.QLabel.Box)
        self._sceneFilePickerButton = QtWidgets.QPushButton(self._centralWidget)
        self._sceneFilePickerButton.setFixedSize(self._defaultButtonSize)
        self._sceneFilePickerButton.setIcon(self._folderIcon)

        self._returnButton = QtWidgets.QPushButton(self._centralWidget)
        self._returnButton.setFixedSize(self._largeButtonSize)

        self._centralWidgetLayout = QtWidgets.QGridLayout(self._centralWidget)
        self._centralWidgetLayout.addWidget(self._itemDatabaseLabel, 0, 0, 1, 1)
        self._centralWidgetLayout.addWidget(self._itemFilePathLabel, 0, 1, 1, 1)
        self._centralWidgetLayout.addWidget(self._itemFilePickerButton, 0, 2, 1, 1)
        self._centralWidgetLayout.addWidget(self._sceneDatabaseLabel, 1, 0, 1, 1)
        self._centralWidgetLayout.addWidget(self._sceneFilePathLabel, 1, 1, 1, 1)
        self._centralWidgetLayout.addWidget(self._sceneFilePickerButton, 1, 2, 1, 1)
        self._centralWidgetLayout.addWidget(self._returnButton, 2, 1, 1, 1, alignment=QtCore.Qt.AlignHCenter)
        self._centralWidget.setLayout(self._centralWidgetLayout)
        self._window.setCentralWidget(self._centralWidget)

        self._getItemPath = None
        self._getScenePath = None
        self._returnButton.clicked.connect(self._window.close)
        QtCore.QMetaObject.connectSlotsByName(self._window)

    def connect(self, get_item_path="", get_scene_path="", set_item_path=None, set_scene_path=None):
        if get_item_path:
            self._getItemPath = get_item_path
        if get_scene_path:
            self._getScenePath = get_scene_path
        if set_item_path:
            self._itemFilePickerButton.clicked.connect(partial(self.pickDatabaseFile, self._itemFilePathLabel, set_item_path))
        if set_scene_path:
            self._sceneFilePickerButton.clicked.connect(partial(self.pickDatabaseFile, self._sceneFilePathLabel, set_scene_path))

    def pickDatabaseFile(self, label: QtWidgets.QLabel, callback):
        dbPath = "Data"
        dbFilter = "Json File (*.json)"
        dialogOutput = QtWidgets.QFileDialog.getOpenFileName(self.window, "Select Json File", dbPath, dbFilter)
        if dialogOutput:
            filePath = dialogOutput[0]
            dataIndex = filePath.find("Data")
            if 0 <= filePath.find("TextRPG") < dataIndex:
                filePath = filePath[dataIndex:]
                label.setText(self._translate(self._window_name, filePath))
                if callback:
                    callback(filePath)
                return
        title = "Error: Invalid File Selection"
        message = "The '{}' must be within the game directory '{}'.".format(dbFilter, dbPath)
        icon = QtWidgets.QMessageBox.Warning
        buttons = QtWidgets.QMessageBox.Ok
        messageBox = QtWidgets.QMessageBox(icon, title, message, buttons, self.window)
        messageBox.accepted.connect(messageBox.close)
        messageBox.exec()

    def refresh(self):
        self._sceneDatabaseLabel.setText(self._translate(self._window_name, "Scene Database:"))
        self._itemDatabaseLabel.setText(self._translate(self._window_name, "Item Database:"))
        self._returnButton.setText(self._translate(self._window_name, "Return"))

    def show(self):
        if self._getItemPath:
            self._itemFilePathLabel.setText(self._translate(self._window_name, self._getItemPath()))
        if self._getScenePath:
            self._sceneFilePathLabel.setText(self._translate(self._window_name, self._getScenePath()))
        super().show()
