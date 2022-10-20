from Data.Character.ability import Ability
from Data.Character.character import Character
from Data.Item.item_reference import ItemRef


class Requirement:
    def __init__(self, abilities: list[Ability] = [], items: list[ItemRef] = []):
        self.abilities: list[Ability] = abilities
        self.items: list[ItemRef] = items

    def consume(self, character: Character):
        """
        Consumes the required items.
        :param character: The character using the items.
        """
        if self.items:
            for item_reference in self.items:
                character.use(quantity=item_reference.quantity, item_reference=item_reference)

    def description(self):
        description = ""
        partFormat = "{}: {},"
        for ability in self.abilities:
            description += partFormat.format(ability.name, ability.score)
        description = description[:-1]
        for itemRef in self.items:
            description += partFormat.format(itemRef.item().name, itemRef.quantity)
        description = description[:-1]
        if len(description) < 1:
            return None
        return "[{}]".format(description)

    def met(self, character: Character):
        """
        Determines whether the character meets all the requirements.
        :param character: The character to validate.
        :return: True if all requirements are met.
        """
        for ability in self.abilities:
            if character.ability(ability.name, "score") < ability.score:
                return False

        if self.items:
            for required_item in self.items:
                current_item = character.inventory.get(item_id=required_item.id)
                if not current_item or current_item.quantity < required_item.quantity:
                    return False
        return True
