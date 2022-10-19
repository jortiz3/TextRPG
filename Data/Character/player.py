from Data.Character.ability import Ability
from Data.Character.character import Character
from Data.Item.inventory import Inventory


class Player(Character):
    __ability_points_per_level = 2
    __initial_ability_points = 5
    __max_ability_score = 10
    __min_ability_score = 0
    __required_experience_scale = 50

    def __init__(self, name="New Player", abilities: list[Ability] = [], level=1, experience=0, ability_points=5,
                 inventory=Inventory()):
        super().__init__(name, abilities, inventory)
        self.ability_points = ability_points
        self.experience = experience
        self.level = level

    def addExperience(self, experience):
        """
        Increases the player's experience and levels up the player when the required experience is met.
        :param experience: The amount of experience to increase by.
        """
        self.experience += abs(experience)
        while True:
            required_experience = self.requiredExperience()
            if self.experience < required_experience:
                break
            self.experience -= required_experience
            self._levelUp()

    def copyAttributes(self, other):
        if not isinstance(other, Player):
            self.resetAttributes()
            return
        self.name = other.name
        self.level = other.level
        self.experience = other.experience
        self.ability_points = other.ability_points
        self.inventory = other.inventory
        if len(self.abilities) != len(other.abilities):
            return
        for index, ability in enumerate(self.abilities):
            ability.score = other.abilities[index].score

    def requiredExperience(self):
        """
        Calculates the experience required to level up.
        :return: Required experience as a number.
        """
        return self.level * self.__required_experience_scale

    def _levelUp(self):
        self.level += 1
        self.ability_points += self.__ability_points_per_level

    @staticmethod
    def maxAbilityScore():
        return Player.__max_ability_score

    def modifyAbilityScore(self, ability_name: str, amount: int, allow_decrement=False):
        """
        Modifies an ability score by the given amount.
        :param ability_name: The name of the ability to modify.
        :param amount: The amount to modify by.
        :param allow_decrement: When true, allows the player to correct their mistakes.
        """
        if not allow_decrement and amount < 0:
            return
        if self.ability_points - amount < 0:
            return

        ability = self.ability(ability_name, "ability")
        new_score = ability.score + amount
        if new_score < self.__min_ability_score or new_score > self.__max_ability_score:
            return
        ability.score = new_score
        self.ability_points -= amount

    def resetAttributes(self):
        self.copyAttributes(Player())
