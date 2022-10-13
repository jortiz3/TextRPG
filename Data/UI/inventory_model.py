from PyQt5.QtCore import QModelIndex, Qt, QAbstractTableModel
from PyQt5.QtWidgets import QWidget

from Data.Character.character import Character


class InventoryModel(QAbstractTableModel):
    def __init__(self, character: Character, parent: QWidget = None):
        super().__init__(parent)
        self._character = character
        self._headers = ["NAME", "QTY"]
        self._character.inventory.setOnModified(self.layoutChanged.emit)

    def columnCount(self, parent: QModelIndex = ...) -> int:
        return 2

    def data(self, index: QModelIndex, role: int = ...):
        if role == Qt.DisplayRole:
            item_reference = self._character.inventory.get(index.row())
            if not item_reference:
                return "null"
            if index.column() == 1:
                return item_reference.quantity
            item = item_reference.item()
            if not item:
                return "null"
            return item.name

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...):
        if role == Qt.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self._headers[section]
            else:
                return section + 1

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self._character.inventory)

