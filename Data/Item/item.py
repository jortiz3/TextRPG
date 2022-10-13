class Item:
	def __init__(self, name: str, type: str):
		self.name = name
		self.type = type

	def __eq__(self, other):
		if isinstance(other, Item):
			return self.type == other.type and self.name == other.name
		return False

	def __lt__(self, other):
		if isinstance(other, Item):
			return self.name < other.name
		return False
