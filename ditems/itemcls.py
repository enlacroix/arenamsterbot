from random import sample
from typing import Self

from datastore.dinventroy import inventory_dict
from datastore.dperks import PRK, PerkCategoryDict



class Item:
    def __init__(self, code: int):
        self.code = code
        # TODO Несовпадение кода в инвентори дикт и кодировки предмета в реализации - основная причина багов, от которого НУЖНО избавиться.
        res = inventory_dict[code][0].split(" | ")
        if len(res) == 2:
            self.name, self.description = res
        else:
            self.name = res[0]
            self.description = res[0]
        self.cost = inventory_dict[code][1]
        # Код может быть каким угодно числом (начиная с двузначных), однако его последняя цифра - категория предмета, первая - уровень предмета.
        self.category: int = code % 10
        self.tier = int(str(code)[0])
        self.charges = 1  # Количество зарядов, сколько раз можно использовать до исчезновения из инвентаря.
        self.protection_from_steal = False  # Можно ли украсть предмет.
        self.protection_from_destroy = False  # Можно ли уничтожить предмет.

    def generalUseItem(self, result, owner):
        self.charges -= 1
        if result not in (0, -1) and self.charges <= 0:
            owner.inv.removeItem(self)
        return result

    def __str__(self):
        return self.name

    def show(self):
        return f'{self.name}: {self.description}'

    def getAmount(self, inventory):
        # Если предмета в инвентаре нет, то верни количество 0.
        return inventory.pool.get(self, 0)

    def getPurchasePrice(self, owner):
        return round(self.cost * max(0.8, 1.2 - owner.merchant))

    def getSalePrice(self, owner):
        return round(self.cost * min(0.8, 0.6 + owner.merchant * 0.5))

    def getPosition(self, inventory):
        try:
            return inventory.content.index(self) + 1
        except ValueError:
            return False

    def showAbility(self, owner):
        """
        :return: смайлик ✅, если можно использовать.
        или 🚫 c сокращенным названием необходимого навыка.
        """
        if self.isAble(owner):
            return ' ✅'
        else:
            return f' 🚫, {PerkCategoryDict[self.category].value[0]}.'

    def isAble(self, owner) -> bool:
        """есть навык или нет"""
        return PerkCategoryDict[self.category] in owner.skills

    def __eq__(self, other):
        return self.code == other.code

    def __hash__(self):
        return hash(self.code)

    @classmethod
    def createRandItemsByType(cls, _type: tuple[int, ...], count=1) -> list[Self]:
        rtrn = []
        for key in sample([x for x in list(inventory_dict.keys()) if x % 10 in _type], count):
            rtrn.append(cls(key))
        return rtrn

    @classmethod
    def createRandItemsByTypeAndTier(cls, _type: int, infimum, supremum, count=1) -> list[Self]:
        rtrn = []
        for key in sample([x for x in list(inventory_dict.keys()) if x % 10 == _type and infimum <= x // 100 <= supremum], count):
            rtrn.append(cls(key))
        return rtrn

    @classmethod
    def createRandItemsByTier(cls, infimum, supremum, count=1) -> list[Self]:
        """
        :param infimum: нижняя граница
        :param supremum: верхняя граница тира предмета. Вернет что-то, что лежит в отрезке [inf, sup].
        :param count: сколько предметов нужно создать.
        :return: список из Item, инициализированных по ключам.
        """
        rtrn = []
        for key in sample([x for x in list(inventory_dict.keys()) if infimum <= x // 100 <= supremum], count):
            rtrn.append(cls(key))
        return rtrn

    @classmethod
    def createRandItems(cls, count) -> list[Self]:
        return [cls(key) for key in sample(tuple(inventory_dict.keys()), count)]

    def use(self, owner, other, ctx):
        """
        :return: всегда методы use() должны возвращать 1 (успешное применение), -1(дать ход после применения, ошибка), 0(?)
        связать с GENERAL USE ITEM (ВЫШЕ)
        """
        pass


