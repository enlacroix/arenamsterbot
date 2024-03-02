from random import randint, choice
from datastore.deffect import EFF
from datastore.dperks import PRK
from datastore.dsources import SRC
from datastore.misc import RACES
from ditems.itemcls import Item
from core.root import Hero, HeroInstance
from vkmodule import send


class EvilTree(Hero):
    def __init__(self, _id):
        super().__init__(_id)
        self.race = RACES.MYST

    # if Chance(65): self.addEffect(EFF.IMAGINARYHEALTH, 1, power=[50 + self.lvl * 5])
    def options(self, other):
        opt_report = f'[1] Шёпот леса. Увеличить точность на {20+self.lvl*2}% и крит на {10+self.lvl*2}% союзнику. \n' \
                     f'[2] {{Земля}} Опутать корнями. Нанесённый урон будет равномерно распределён по его ряду в виде лечения.  \n' \
                     f'[3] Запретное слово. Противник временно не будет получать лечения. \n' \
                     f'[4] Мудрость. Обучить союзника случайному перку, 3 МР \n' + super().options(other)
        return opt_report

    def preChoiceAction(self, other, ctx):
        for ally in self.getOwnRow():
            ally.resists[SRC.WEAPON].changeValue(2 + self.lvl // 5)

    def startInventory(self):
        self.inv.addItem(Item(347))

    def firstAction(self, other, ctx):
        if self.allyActionForEnemy(other, ctx): return -1
        other.addEffect(EFF.FOCUSED, 1 + self.lvl // 4, power=[20 + self.lvl * 2])
        other.addEffect(EFF.LUCKY, 1 + self.lvl // 5, power=[10 + self.lvl * 2])
        send(ctx, f'{other} сконцентрирован и уверен в себе. Хорошая работа.')

    def secondAction(self, other, ctx):
        x = self.MagicPattern(other, ctx, mana=0, source=SRC.EARTH)
        if x in (0, -1): return x
        heal_report = ' '
        N = len(self.getRow(self.position))
        for ally in self.getOwnRow():
            heal_report += f'{ally} восстановил(-а) {ally.heal(x // N)} здоровья. \n'
        send(ctx, heal_report)


    def thirdAction(self, other, ctx):
        send(ctx, f'Хуорн проклинает {other} на невосприимчивость к заклинаниям лечения.')
        other.addEffect(EFF.INTERDICT, power=[1], rounds=2 + self.lvl // 4)

    def fourthAction(self, other: HeroInstance, ctx):
        if self.allyActionForEnemy(other, ctx): return -1
        randPerk = choice(list(PRK))
        other.skills.append(randPerk)
        send(ctx, f'{other} теперь обучен перку {randPerk.value[0]}!')


    def levelup(self, ind=1):
        self.dmg += randint(1, 3) * ind
        self.power += randint(2, 3) * ind
        self.mana += randint(0, 1) * ind
        super().levelup(ind)