from Data.Scene.requirement import Requirement
from Data.Scene.reward import Reward
from Data.Character.player import Player


class Action:
    def __init__(self, description: str = "[ null ]", disable_on_select=False, id: int = -777, remove_on_select=False,
                 requirement: Requirement = None, reward: Reward = None):
        self.description = description
        self.enabled = True
        self.disableOnSelect = disable_on_select
        self.id = id
        self.removed = False
        self.removeOnSelect = remove_on_select
        self.requirement: Requirement = requirement
        self.reward: Reward = reward
        self.selected = False

    def __eq__(self, other):
        if type(self) is not type(other):
            return False
        otherAction: Action = other
        return self.id == otherAction.id and self.description == otherAction.description

    def requirementMet(self, player: Player):
        """
        Determines whether the player meets the requirement for this action.
        :param player: The player to validate.
        :return: True if the action is enabled, and the requirement is met.
        """
        if not self.enabled:
            return False
        elif not self.requirement:
            return True
        return self.requirement.met(player)

    def select(self, player: Player):
        """
        Selects this action, consumes requirements and distributes rewards.
        :param player: The active player.
        :return: True if scene change is required.
        """
        if not self.enabled or self.selected:
            return False
        if self.requirement:
            self.requirement.consume(player)
        if self.reward:
            self.reward.distribute(player)
        self.enabled = not self.disableOnSelect
        self.removed = self.removeOnSelect
        self.selected = True
        return self.id >= 0
