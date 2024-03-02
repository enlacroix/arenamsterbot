from random import randint
from datastore.dsources import SRC

class Chance:
    # if Chance(50, source=SRC.Mind).roll(unit): - пример
    def __init__(self, value, source: SRC = SRC.DEFAULT, extra: SRC = SRC.DEFAULT, adjust=0):
        self.value = value
        self.source = source
        self.extrasrc = extra

    def __bool__(self):
        # Для простых шансов, где не нужны параметры юнита.
        return randint(1, 100) <= self.value

    def addExtraSRC(self, extrasrc: SRC):
        self.extrasrc = extrasrc

    def roll(self, unit) -> bool:
        """
        другой способ подсчёта шансов. Если раньше при сопротивлении в 50% и шансе 50% итоговый шанс был бы 0, то теперь множитель от сопротивления
        50% равен 0.5, который умножается на шанс. Т.е. теперь 25%.
        Второе нововведение: подсчёт шанса СНИМАЕТ вард.
        """
        return randint(1, 100) <= self.value * unit.getSRCFactor(self.source) * unit.getSRCFactor(self.extrasrc)

    def count(self, unit):
        return round(self.value * unit.calcSRCFactor(self.source) * unit.calcSRCFactor(self.extrasrc))

    def show(self, unit):
        """
        Если вард или иммунитет, то верни 0%. Иначе: self.value - значение резиста по источнику.
        """
        return f'{min(100, self.count(unit))}%'