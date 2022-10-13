from Data.Item.item_database import ItemDatabase


class ItemRef:
    def __init__(self, id: int, quantity: int):
        self.id = id
        self.quantity = quantity

    def __eq__(self, other):
        if not isinstance(other, ItemRef):
            return False
        return self.id == other.id

    def item(self):
        return ItemDatabase.get(self.id)

    def __lt__(self, other):
        if not isinstance(other, ItemRef):
            return False
        return self.item().__lt__(other.item())
