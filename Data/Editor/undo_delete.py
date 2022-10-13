from PyQt5.QtWidgets import QUndoCommand


class UndoDelete(QUndoCommand):
    def __init__(self, db: list, index: int, description: str = "Undo Delete"):
        super().__init__(description)
        self._db: list = db
        self._index: int = index
        self._value = self._db[self._index]

    def redo(self) -> None:
        self._db.pop(self._index)

    def undo(self) -> None:
        self._db.insert(self._index, self._value)
