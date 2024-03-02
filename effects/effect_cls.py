from datastore.deffect import EFF


class Effect:
    # Effect(EffEnum.STRENGTH, rounds=2, power=0.25)
    # Effect(EffEnum.SWAMP, power=[0.25, 20], rounds=2)
    def __init__(self, identifier: EFF, power: list, rounds: int):
        self.name, self.isPositive, self.listOfChangingAttributes = identifier.value['nm'], identifier.value['pos'], identifier.value['attrs']
        self.rounds = rounds
        self.identifier = identifier
        self.canRemove = True
        self.power = power
        assert len(self.listOfChangingAttributes) == len(self.power), 'переданы неверные аргументы для инициализации нового эффекта.'
        self.delta = None

    def __str__(self):
        return f'{self.name}({self.rounds}): {", ".join([str(subpower) if Effect.IsAdding(subpower) else str(round(subpower * 100)) + "%" for subpower in self.power])}'

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
            attrValue = getattr(unit, attr)
            if Effect.IsAdding(self.power[i]):
                self.delta[i] = self.power[i]
            else:
                self.delta[i] = round(attrValue * self.power[i])
            self.delta[i] = self.delta[i] if self.isPositive else -self.delta[i]
            setattr(unit, attr, attrValue + self.delta[i])

    def reverse(self, unit):
        """
        Восстановиться после баффа или дебаффа к изначальному состоянию.
        Допустим тебе снизили урон в два раза. Используя сгущ. молоко ты получил +10 урона.
        На бринг ми бэке получаешь удвоение баффа и незаконные 10 урона - РЕШЕНО. используем дельту.
        """
        for i, attr in enumerate(self.listOfChangingAttributes):
            setattr(unit, attr, getattr(unit, attr) - self.delta[i])
        self.delta.clear()


