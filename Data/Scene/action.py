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
        self.requirement: Requirement = requirement
        self.reward: Reward = reward
        self.selected = False

    def __eq__(self, other):
        if type(self) is not type(other):
            return False
        otherAction: Action = other
        return self.id == otherAction.id and self._description == otherAction._description

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
        if not self.enabled:
            return False
        if not self.selected:
            if self.requirement:
                self.requirement.consume(player)
            if self.reward:
                self.reward.distribute(player)
        self.enabled = not self.disableOnSelect
        self.removed = self.removeOnSelect
        self.selected = True
        return self.id >= -1

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value: str):
        self._description = value

    @property
    def disableOnSelect(self):
        return self._disableOnSelect

    @disableOnSelect.setter
    def disableOnSelect(self, value: bool):
        self._disableOnSelect = value

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value: int):
        self._id = value

    @property
    def removeOnSelect(self):
        return self._removeOnSelect

    @removeOnSelect.setter
    def removeOnSelect(self, value: bool):
        self._removeOnSelect = value
