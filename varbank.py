from functools import reduce
from typing import Self
from datastore.misc import TURN_STATE
from ditems.inventory import Inventory

teams = [[], []]
delayed = []
disabled = []
done = []
archive = [[], []]
stage = 1

class Team:
    _instance = {}
    stage = 1

    def __init__(self, teamNumber: int):
        if teamNumber not in Team._instance:
            self.num = teamNumber
            self.gold: int = 0
            self.members: list = []
            self.graveyard: list = []
            self.inventory = Inventory()

    @classmethod
    def Entry(cls, teamNumber: int) -> Self:
        if teamNumber not in Team._instance:
            cls._instance[teamNumber] = Team(teamNumber)
        return cls._instance[teamNumber]

    def getTeamInventory(self, unit):
        self.inventory.owner = unit
        return self.inventory

    def __len__(self):
        return len(self.members)

    def getSize(self):
        return reduce(lambda a, x: a + x.size, self.members, 0)

    def __iter__(self):
        return iter(self.members)

    def __contains__(self, item):
        return item in self.members

    def getDoneUnits(self):
        return list(filter(lambda x: x.turnState == TURN_STATE.DONE, self.members))

    def getWaitedUnits(self):
        return list(filter(lambda x: x.turnState == TURN_STATE.WAIT, self.members))

    def getRow(self, row_num: int):
        return list(filter(lambda x: x.position == row_num, self.members))




