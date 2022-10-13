from functools import partial

from PyQt5 import QtCore, QtGui, QtWidgets

from Data.UI.ui import UI


class UiLoad(UI):
    def __init__(self, window: QtWidgets.QMainWindow):
        super().__init__(window, window_min_size=QtCore.QSize(400, 400), window_name="LoadWindow",
                         window_show_size=QtCore.QSize(400, 600), window_title="Text RPG - Load Game")
        self._window.setMaximumSize(QtCore.QSize(1280, 900))
        self._centralWidget = QtWidgets.QWidget(self._window)
        self._centralWidget.setObjectName("centralwidget")
        self._centralWidgetLayout = QtWidgets.QGridLayout(self._centralWidget)
        self._centralWidgetLayout.setObjectName("rootLayout")
        self._scrollArea = QtWidgets.QScrollArea(self._centralWidget)
        self._scrollArea.setFrameShape(QtWidgets.QFrame.NoFrame)
        self._scrollArea.setObjectName("scrollArea")
        self._scrollAreaContent = QtWidgets.QWidget(self._scrollArea)
        self._scrollAreaContent.setObjectName("scrollAreaContent")
        self._scrollAreaContentLayout = QtWidgets.QVBoxLayout(self._scrollAreaContent)
        self._scrollAreaContentLayout.setContentsMargins(10, -1, 10, -1)
        self._scrollAreaContentLayout.setObjectName("scrollAreaContentLayout")
        self._scrollArea.setWidget(self._scrollAreaContent)
        self._scrollArea.setLayout(self._scrollAreaContentLayout)
        self._returnButton = QtWidgets.QPushButton(self._centralWidget)
        self._returnButton.setFixedSize(self._defaultButtonSize)

        self._deleteButtons: list[QtWidgets.QPushButton] = []
        self._groupBoxes: list[QtWidgets.QGroupBox] = []
        self._loadButtons: list[QtWidgets.QPushButton] = []
        self._loadLabels: list[QtWidgets.QLabel] = []

        self._delete_save = None
        self._load_save = None
        self._load_info = None

        self._centralWidgetLayout.addWidget(self._scrollArea, 0, 0, 3, 3)
        self._centralWidgetLayout.addWidget(self._returnButton, 4, 1, 1, 1)
        self._window.setCentralWidget(self._centralWidget)

        self._returnButton.clicked.connect(self._window.hide)
        QtCore.QMetaObject.connectSlotsByName(self._window)

    def connect(self, delete_save=None, load_save=None, load_info=None):
        if delete_save:
            self._delete_save = delete_save
        if load_save:
            self._load_save = load_save
        if load_info:
            self._load_info = load_info

    def _connect_slots(self, start: int):
        if self._delete_save:
            for index in range(start, len(self._deleteButtons)):
                deleteButton = self._deleteButtons[index]
                deleteButton.clicked.connect(partial(self._delete_save, index))
                deleteButton.clicked.connect(self.refresh)
        if self._load_save:
            for index in range(start, len(self._loadButtons)):
                loadButton = self._loadButtons[index]
                loadButton.clicked.connect(partial(self._load_save, index))

    def _instantiate_slots(self, quantity: int):
        """
        Instantiates load slot ui if necessary.
        :param quantity: The number of slots required.
        :return: The index where new slots were appended.
        """
        quantity = abs(quantity)
        slots_available = len(self._loadButtons)
        if quantity <= slots_available:
            return -1

        for index in range(slots_available, quantity):
            groupBox = QtWidgets.QGroupBox(self._scrollAreaContent)
            groupBox.setObjectName("areaActionsGroupBox")
            self._groupBoxes.append(groupBox)
            layout = QtWidgets.QHBoxLayout(groupBox)
            layout.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
            layout.setSpacing(10)
            layout.setObjectName("loadLayout{}".format(index))
            label = QtWidgets.QLabel(groupBox)
            label.setMinimumSize(QtCore.QSize(100, 75))
            label.setObjectName("loadLabel{}".format(index))
            label.setWordWrap(True)
            self._loadLabels.append(label)
            layout.addWidget(label)
            load = QtWidgets.QPushButton(groupBox)
            load.setFixedSize(self._defaultButtonSize)
            load.setObjectName("loadButton{}".format(index))
            layout.addWidget(load)
            self._loadButtons.append(load)
            delete = QtWidgets.QPushButton(groupBox)
            delete.setFixedSize(self._defaultButtonSize)
            delete.setObjectName("deleteButton{}".format(index))
            layout.addWidget(delete)
            self._deleteButtons.append(delete)
            self._scrollAreaContentLayout.addWidget(groupBox)
        return slots_available

    def refresh(self):
        load_info = self._load_info() if self._load_info else None
        start_index = self._instantiate_slots(len(load_info)) if load_info else -1
        if start_index >= 0:
            self._connect_slots(start_index)

        for index in range(len(self._loadButtons)):
            groupBox = self._groupBoxes[index]
            label = self._loadLabels[index]
            loadButton = self._loadButtons[index]
            loadButton.setText(self._translate(self._window_name, "Load"))
            deleteButton = self._deleteButtons[index]
            deleteButton.setText(self._translate(self._window_name, "Delete"))

            if load_info and index < len(load_info):
                groupBox.show()
                label.setText(load_info[index])
                label.show()
                loadButton.show()
                deleteButton.show()
            else:
                groupBox.hide()
                label.hide()
                loadButton.hide()
                deleteButton.hide()
        self._returnButton.setText(self._translate(self._window_name, "Return"))
