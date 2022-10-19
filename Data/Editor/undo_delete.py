from PyQt5.QtWidgets import QUndoCommand


class UndoDelete(QUndoCommand):
    def __init__(self, db: list, index: int, description: str = "Delete", callback=None):
        super().__init__(description)
        self._callback = callback
        self._db: list = db
        self._index: int = index
        self._value = self._db[self._index]

    def redo(self) -> None:
        self._db.pop(self._index)
        if self._callback:
            self._callback()

    def undo(self) -> None:
        self._db.insert(self._index, self._value)
        if self._callback:
            self._callback()
