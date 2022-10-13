import math

from Data.Character.ability import Ability
from Data.Item.inventory import Inventory
from Data.Item.item_reference import ItemRef


class Character:
    __round_digits = 2

    def __init__(self, name="", strength=1.0, dexterity=1.0, intelligence=1.0, will=1.0, wisdom=1.0,
                 inventory=Inventory()):
        self.abilities: dict[str, Ability] = {
            "dexterity": Ability("dexterity", "Ability checks and run chance", dexterity),
            "intelligence": Ability("intelligence", "Ability checks and enchanting", intelligence),
            "strength": Ability("strength", "Ability checks and crafting", strength),
            "will": Ability("will", "Ability checks and crafting", will),
            "wisdom": Ability("wisdom", "Ability checks and enchanting", wisdom)}
        self.inventory = inventory
        self.name = name

    def ability(self, name: str, context: str = "score"):
        ability = self.abilities[name.lower()]
        if context == "score":
            return ability.score
        elif context == "description":
            return ability.description
        else:
            return ability.name

    def craftingBonus(self):
        bonus = self.ability("will")
        bonus += self.ability("strength") / 2.0
        return round(bonus, Character.__round_digits)

    def dodgeBonus(self):
        bonus = self.ability("dexterity") + self.ability("wisdom")
        return round(bonus, Character.__round_digits)

    def enchantingBonus(self):
        bonus = self.ability("wisdom")
        bonus += self.ability("intelligence") / 2.0
        return round(bonus, Character.__round_digits)

    def powerLevel(self):
        return math.floor(
            self.ability("intelligence") + self.ability("dexterity") + self.ability("strength") + self.ability(
                "will") + self.ability("wisdom"))

    def runBonus(self):
        bonus = self.ability("dexterity") + self.ability("will")
        return round(bonus, Character.__round_digits)

    def use(self, item_id: int = None, quantity: int = 1, item_reference: ItemRef = None):
        if item_id is not None:
            item_reference = ItemRef(item_id, quantity)
        elif not item_reference:
            return
        self.inventory.use(item_reference=item_reference, quantity=quantity)
