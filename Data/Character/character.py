import copy
import math

from Data.Character.ability import Ability
from Data.Item.inventory import Inventory
from Data.Item.item_reference import ItemRef


class Character:
    __default_abilities = [
        Ability("dexterity", "Ability checks", 1.0),
        Ability("intelligence", "Ability checks and enchanting", 1.0),
        Ability("strength", "Ability checks and crafting", 1.0),
        Ability("will", "Ability checks and crafting", 1.0),
        Ability("wisdom", "Ability checks and enchanting", 1.0),
    ]
    __round_digits = 2

    def __init__(self, name="", abilities: list[Ability] = [], inventory=Inventory()):
        self.abilities = abilities if len(abilities) > 0 else copy.deepcopy(self.__default_abilities)
        self.inventory = inventory
        self.name = name

    def ability(self, name: str, context: str = "score"):
        name = name.lower()
        for ability in self.abilities:
            if ability.name != name:
                continue
            if context == "ability":
                return ability
            elif context == "description":
                return ability.description
            else:
                return ability.score

    def craftingBonus(self):
        return self.ability("will") + self.ability("strength")

    def enchantingBonus(self):
        return self.ability("wisdom") + self.ability("intelligence")

    def powerLevel(self):
        return math.floor(
            self.ability("intelligence") + self.ability("dexterity") + self.ability("strength") + self.ability(
                "will") + self.ability("wisdom"))

    def use(self, item_id: int = None, quantity: int = 1, item_reference: ItemRef = None):
        if item_id is not None:
            item_reference = ItemRef(item_id, quantity)
        elif not item_reference:
            return
        self.inventory.use(item_reference=item_reference, quantity=quantity)
