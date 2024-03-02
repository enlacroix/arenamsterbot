from functools import reduce
from typing import TypeVar

from datastore.dperks import PRK


class Parent:
    size = 1

    def __init__(self, id):
        self.id = id

    def attack(self):
        self.attack.passive = False
        print('атакую!')

H = TypeVar("H", bound=Parent)

class Ghost:
    size = 2

    def __init__(self, id=50, position=0):
        self.health = 100
        self.ini = 90
        self.position = position
        self.max_hp = 120
        self.id = [PRK.MISC]

    def heal(self, amount):
        x = max(min(self.max_hp - self.health, amount), 0)
        self.health += x
        print(self.health, x)
        return x

    def attack(self, crit):
        print(f'изощренно атакую на x{crit}')

    def __getattr__(self, item):
        if item == 'inv':
            return 'особое'
        else:
            super().__getattribute__(item)

    def __str__(self):
        return f'призрак {self.gold} зол, {self.health} ОЗ'

n = [Ghost(10), Ghost(60)]
print(list(reduce(lambda a, x: a + x.id, n, [])))


Ghost.size += 1
print(Ghost.size)