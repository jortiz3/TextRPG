from Data.Scene.requirement import Requirement
from Data.Scene.reward import Reward
from Data.Character.player import Player


class Action:
    def __init__(self, description: str = "", consequence: str = "", disable_on_select=False, id: int = -777,
                 remove_on_select=False, requirement: Requirement = Requirement(), reward: Reward = Reward(),
                 secret=False):
        self._consequence: str = consequence
        self._description: str = description
        self.enabled: bool = True
        self._disableOnSelect: bool = disable_on_select
        self._id: int = id
        self.removed: bool = False
        self._removeOnSelect: bool = remove_on_select
        self._requirement: Requirement = requirement
        self._reward: Reward = reward
        self._secret: bool = secret
        self.selected: bool = False

    def __eq__(self, other):
        if type(self) is not type(other):
            return False
        otherAction: Action = other
        return self.id == otherAction.id and self._description == otherAction._description

    def getDescription(self):
        """Includes the requirement description."""
        if self.id == -1:
            return self._description
        description = self._description
        reqDescription = self.requirement.description()
        if reqDescription:
            description = "{} {}".format(description, reqDescription)
        return description

    def getState(self):
        """Override to be used conditionally for json pickling."""
        return {"enabled": self.enabled, "removed": self.removed, "selected": self.selected}

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
        self.enabled = not self.disableOnSelect
        self.removed = self.removeOnSelect
        self.selected = True
        return self.id >= -1

    @property
    def consequence(self):
        return self._consequence

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value: str):
        self._description = value

    @property
    def disableOnSelect(self):
        return self._disableOnSelect

    @property
    def id(self):
        return int(self._id)

    @property
    def removeOnSelect(self):
        return self._removeOnSelect

    @property
    def requirement(self):
        return self._requirement

    @property
    def reward(self):
        return self._reward

    @property
    def secret(self):
        return self._secret
