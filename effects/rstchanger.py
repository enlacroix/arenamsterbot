from datastore.deffect import EFF
from datastore.dsources import SRC


class ResistChanger:
    def __init__(self, identifier: EFF, power: list, rounds: int):
        self.name, self.isPositive = identifier.value['nm'], identifier.value['pos']
        self.listOfChangingAttributes: list[SRC] = identifier.value['attrs']
        self.rounds = rounds
        self.identifier = identifier
        self.canRemove = True
        self.power = power
        assert len(self.listOfChangingAttributes) == len(self.power), 'переданы неверные аргументы для инициализации нового эффекта.'
        self.delta = None

    def __str__(self):
        return f'{self.name}({self.rounds}): {", ".join([str(subpower) if ResistChanger.IsAdding(subpower) else str(round(subpower * 100)) + "%" for subpower in self.power])}'

    @staticmethod
    def IsAdding(subpower) -> bool:
        """
        А. Случай умножения. power - (0, 1]
        power = 1 or 0: нейтральный элемент, ничего не измениться.
        Б. Случай прибавления/вычитания. power (-inf, 0] or (1, +inf).
        """
        return subpower > 1 or subpower <= 0

    def straight(self, unit):
        self.delta = [0] * len(self.listOfChangingAttributes)
        for i, attr in enumerate(self.listOfChangingAttributes):
            attrValue = unit.resists[attr].value
            if ResistChanger.IsAdding(self.power[i]):
                self.delta[i] = self.power[i]
            else:
                self.delta[i] = round(attrValue * self.power[i])
            self.delta[i] = self.delta[i] if self.isPositive else -self.delta[i]
            unit.resists.changeValue(attr, self.delta[i])

    def reverse(self, unit):
        """
        Восстановиться после баффа или дебаффа к изначальному состоянию.
        Допустим тебе снизили урон в два раза. Используя сгущ. молоко ты получил +10 урона.
        На бринг ми бэке получаешь удвоение баффа и незаконные 10 урона - РЕШЕНО. используем дельту.
        """
        for i, attr in enumerate(self.listOfChangingAttributes):
            unit.resists.changeValue(attr, -self.delta[i])
        self.delta.clear()