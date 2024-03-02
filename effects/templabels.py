from datastore.deffect import EFF


class TempLabel:
    def __init__(self, identifier: EFF, rounds: int, power: list = None):
        self.identifier = identifier
        self.name= identifier.value['nm']
        self.canRemove = identifier.value.get('canRemove', True)
        self.isPositive = identifier.value.get('pos', True)
        self.power = power
        self.rounds = rounds

    def __str__(self):
        return f'{self.name}: ({self.rounds})'
