from PyQt5.QtWidgets import QUndoCommand


class UndoNew(QUndoCommand):
    def __init__(self, db: list, index: int, value, description: str = "Undo New"):
        super().__init__(description)
        self._db: list = db
        self._index: int = index
        self._value = value

    def redo(self) -> None:
        self._db.insert(self._index, self._value)

    def undo(self) -> None:
        self._db.pop(self._index)
