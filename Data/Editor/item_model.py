from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt, QVariant
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget

from Data.Item.item import Item


class ItemModel(QAbstractTableModel):
    def __init__(self, items: list[Item], delete_icon: QIcon, parent: QWidget = None):
        super().__init__(parent)
        self._items: list[Item] = items
        self._headers = ["NAME", "TYPE"]
        self._deleteIcon = delete_icon

    def columnCount(self, parent: QModelIndex = ...) -> int:
        return 2

    def data(self, index: QModelIndex, role: int = ...):
        if role == Qt.DisplayRole:
            item = self._items[index.row()]
            if index.column() == 0:
                return item.name
            elif index.column() == 1:
                return item.type
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        return QVariant()

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if index.column() == 2:
            return Qt.ItemFlags(Qt.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
        else:
            return Qt.ItemFlags(
                Qt.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsDragEnabled | Qt.ItemFlag.ItemIsDropEnabled)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...):
        if role == Qt.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self._headers[section]
            else:
                return section + 1

    def insertRow(self, row: int, parent: QModelIndex = ...) -> bool:
        if row < 0:
            row = self.rowCount()
        self._items.insert(row, Item("New Item", "New Type"))
        self.layoutChanged.emit()
        return True

    def removeRow(self, row: int, parent: QModelIndex = ...) -> bool:
        if self.rowCount() == 0:
            return False
        if row < 0:
            row = self.rowCount() - 1
        self._items.pop(row)
        self.layoutChanged.emit()
        return True

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self._items)

    def setData(self, index: QModelIndex, value, role: int = ...) -> bool:
        item = self._items[index.row()]
        if index.column() == 1:
            item.type = value
        else:
            item.name = value
        return True
