import bisect

from Data.Item.item_reference import ItemRef


class Inventory:
    __modified = None

    def __init__(self):
        super().__init__()
        self.currency: int = 0
        self.itemRefs: list[ItemRef] = []

    @staticmethod
    def capacity():
        """The maximum item capacity."""
        return 10

    def clear(self):
        """Removes all items."""
        self.itemRefs.clear()
        Inventory.__modified()

    def __contains__(self, item_reference: ItemRef):
        """Return key in self."""
        return self.itemRefs.__contains__(item_reference)

    def empty(self) -> list[ItemRef]:
        """
        Removes all items.
        :return: A list containing the removed items.
        """
        emptied_items = self.itemRefs
        self.itemRefs = []
        Inventory.__modified()
        return emptied_items

    def full(self) -> bool:
        """
        Checks the size against the capacity.
        :return: True if size meets or exceeds the capacity.
        """
        return len(self.itemRefs) >= Inventory.capacity()

    def get(self, index: int = None, item_id: int = None):
        """
        Retrieves the item ref at a given index.
        :param index: The item ref index.
        :param item_id: The item ref id.
        :return: ItemRef object if found, or None.
        """
        if index is not None:
            if self.validIndex(index):
                return self.itemRefs[index]
        elif item_id is not None:
            for item in self.itemRefs:
                if item.id == item_id:
                    return item
        return None

    def __getstate__(self):
        return {
            "currency": self.currency,
            "itemRefs": self.itemRefs
        }

    def __len__(self):
        return len(self.itemRefs)

    def put(self, *item_references: ItemRef) -> list[ItemRef]:
        """
        Puts the given items into the inventory.
        :param item_references: The item refs to put.
        :return: List of items that did not fit into the inventory.
        """
        rejected_items: list[ItemRef] = []
        for item_reference in item_references:
            try:  # try to increase quantity of existing item
                index = self.itemRefs.index(item_reference)
                existing_item = self.itemRefs[index]
                existing_item.quantity = existing_item.quantity + item_reference.quantity
                continue
            except ValueError:
                if self.full():
                    rejected_items.append(item_reference)
                    continue
                bisect.insort(self.itemRefs, item_reference)
                continue
        Inventory.__modified()
        return rejected_items

    def remove(self, index: int = None, item_reference: ItemRef = None, quantity: int = 0):
        """
        Removes an item using either the index or the item ref itself.
        :param index: The item index.
        :param item_reference: The item reference.
        :param quantity: The quantity to remove.
        """
        if index:
            if not self.validIndex(index):
                return
            item_reference = self.itemRefs[index]
        elif item_reference and not self.__contains__(item_reference):
            return
        item_reference.quantity -= abs(quantity)
        if quantity == 0 or item_reference.quantity <= 0:
            self.itemRefs.remove(item_reference)
        Inventory.__modified()

    @staticmethod
    def setOnModified(slot):
        Inventory.__modified = slot

    def __setstate__(self, state):
        self.__dict__.update(state)

    def use(self, index: int = None, item_reference: ItemRef = None, quantity: int = 1):
        if index:
            if not self.validIndex(index):
                return
            item_reference = self.get(index)
        elif item_reference and not self.itemRefs.__contains__(item_reference):
            return
        item_reference.quantity -= quantity
        if item_reference.quantity <= 0:
            self.remove(item_reference=item_reference)
        Inventory.__modified()

    def validIndex(self, index: int):
        """
        Validates the given index is within bounds.
        :param index: The index to be validated.
        :return: True if the index is in bounds.
        """
        return abs(index) in range(len(self.itemRefs))
