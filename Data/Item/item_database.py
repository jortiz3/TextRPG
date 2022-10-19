import copy

import jsonpickle

from Data.Item.item import Item


class ItemDatabase:
    __db: list[Item] = []
    __db_path = "Data/items.json"

    @staticmethod
    def initialize():
        with open(ItemDatabase.__db_path, 'r') as itemdb:
            ItemDatabase.__db = jsonpickle.decode(itemdb.read())

    @staticmethod
    def get(db_id: int) -> Item:
        """
		Retrieves a deep copy of an item within the database.
		:param db_id: The item's database id.
		:return: An instance of Item class.
		"""
        if db_id not in range(0, len(ItemDatabase.__db)):
            raise IndexError("Id '{}' is not within the bounds of the database".format(db_id))
        return copy.deepcopy(ItemDatabase.__db[db_id])

    @staticmethod
    def size():
        return len(ItemDatabase.__db)
