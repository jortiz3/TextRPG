from Data.Scene.requirement import Requirement
from Data.Scene.reward import Reward
from Data.Character.player import Player


class Action:
    def __init__(self, description: str = "New Action", disable_on_select=False, id: int = -777, remove_on_select=False,
                 requirement: Requirement = None, reward: Reward = None):
        self._description = description
        self.enabled = True
        self._disableOnSelect = disable_on_select
        self._id = id
        self.removed = False
        self._removeOnSelect = remove_on_select
        self._requirement: Requirement = requirement
        self._reward: Reward = reward
        self.selected = False

    def __eq__(self, other):
        if type(self) is not type(other):
            return False
        otherAction: Action = other
        return self._id == otherAction._id and self._description == otherAction._description

    def requirementMet(self, player: Player):
        """
        Determines whether the player meets the requirement for this action.
        :param player: The player to validate.
        :return: True if the action is enabled, and the requirement is met.
        """
        if not self.enabled:
            return False
        elif not self._requirement:
            return True
        return self._requirement.met(player)

    def select(self, player: Player):
        """
        Selects this action, consumes requirements and distributes rewards.
        :param player: The active player.
        :return: True if scene change is required.
        """
        if not self.enabled:
            return False
        if not self.selected:
            if self._requirement:
                self._requirement.consume(player)
            if self._reward:
                self._reward.distribute(player)
        self.enabled = not self._disableOnSelect
        self.removed = self._removeOnSelect
        self.selected = True
        return self._id >= -1

    def description(self):
        return self._description

    def setDescription(self, value: str):
        self._description = value

    def disableOnSelect(self):
        return self._disableOnSelect

    def id(self):
        return self._id

    def removeOnSelect(self):
        return self._removeOnSelect

    def requirement(self):
        return self._requirement

    def reward(self):
        return self._reward
