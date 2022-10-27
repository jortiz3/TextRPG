import copy

import jsonpickle

from Data.Item.item import Item


class ItemDatabase:
    __db: list[Item] = []

    @staticmethod
    def initialize(path: str):
        with open(path, 'r') as itemdb:
            ItemDatabase.__db = jsonpickle.decode(itemdb.read())
        message = "File at path '{}' did not contain {}."
        if not isinstance(ItemDatabase.__db, list):
            raise ValueError(message.format(path, "a list"))
        elif len(ItemDatabase.__db) <= 0:
            raise ValueError("a populated list")
        elif not isinstance(ItemDatabase.__db[0], Item):
            raise ValueError(message.format(path, "a list of Items"))

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
