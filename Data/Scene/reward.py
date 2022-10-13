from Data.Character.player import Player
from Data.Item.item_reference import ItemRef


class Reward:
    def __init__(self, experience: int = 10, items: list[ItemRef] = None):
        self.experience = experience
        self.items = items

    def distribute(self, player: Player):
        player.addExperience(self.experience)
        if self.items:
            player.inventory.put(*self.items)
