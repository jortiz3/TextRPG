from functools import partial

from PyQt5.QtCore import QModelIndex
from PyQt5.QtGui import QContextMenuEvent, QIcon, QCursor
from PyQt5.QtWidgets import QAction, QMenu, QTableView, QWidget


class ItemView(QTableView):
    def __init__(self, newIcon: QIcon, deleteIcon: QIcon, parent: QWidget = None):
        super().__init__(parent)
        self._deleteIcon: QIcon = deleteIcon
        self._newIcon: QIcon = newIcon
        self.menu = None

    def contextMenuEvent(self, a0: QContextMenuEvent):
        self.menu = QMenu()
        index = self.indexAt(a0.pos())
        addItemAction = QAction(self.menu)
        addItemAction.setText("New Item")
        addItemAction.setIcon(self._newIcon)
        addItemAction.triggered.connect(partial(self._insertRow, index))
        removeItemAction = QAction(self.menu)
        removeItemAction.setText("Remove Item")
        removeItemAction.setIcon(self._deleteIcon)
        removeItemAction.triggered.connect(partial(self._removeRow, index))
        self.menu.addAction(addItemAction)
        self.menu.addAction(removeItemAction)
        self.menu.popup(QCursor.pos())

    def _insertRow(self, index: QModelIndex):
        self.model().insertRow(index.row(), index)

    def _removeRow(self, index: QModelIndex):
        self.model().removeRow(index.row(), index)
