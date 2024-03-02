from random import choice

from datastore.deffect import EFF
from datastore.dsources import SRC
from datastore.misc import RACES
from ditems.itemcls import Item
from myrandom import Chance
from resists.rstcls import Resist
from resists.rstmanager import ResistManager
from resists.rststates import Ward
from core.root import Hero
from vkmodule import send


class Herbalist(Hero):
    def __init__(self, _id):
        super().__init__(_id)
        self.resists = ResistManager({SRC.STUN: Resist(0, Ward)})
        self.resists[SRC.STUN].setWard()
        self.race = RACES.NONHUMAN


    def options(self, other):
        opt_report = f'[1] Бодрящий эликсир. Увеличение атаки на {50 + 5 * self.lvl}% на {1 + self.lvl // 6} раунд(-а). \n ' \
                     f'[2] Укрепляющие пары (1 МР). +20% атаки и {20+self.lvl} точности на 2 раунда на СВОЙ ряд. \n ' \
                     f'[3] Компот гномов. Очистить цели от отрицательных эффектов. \n' \
                     f'[4] Изготовить случайный расходник поддержки, {10*self.lvl}% сохранить ход. \n' + super().options(other)
        return opt_report

    def startInventory(self):
        self.addRandItemsByTier(supremum=1)

    def firstAction(self, other, ctx):
        if self.team != other.team: return -1 # Защита от мискликов
        other.addEffect(EFF.STRENGTH, 1 + self.lvl // 6, power=[0.5 + 0.05 * self.lvl])
        send(ctx, f'Травница вливает в рот {other} снадобье, которое временно усилит его физический потенциал.')

    def secondAction(self, other, ctx):
        if not self.spend_mana(1, ctx): return -1
        for target in self.getOwnRow():
            target.addEffect(EFF.STRENGTH, 2, power=[0.2])
            target.addEffect(EFF.FOCUSED, 2, power=[20+self.lvl])
        send(ctx, f'Благовония травницы придают бойцам {self.position + 1}-го ряда особую решимость.')

    def thirdAction(self, other, ctx):
        if self.team != other.team: return -1
        for eff in other.effects.pool:
            if not eff.isPositive: eff.rounds = 0
        send(ctx, 'Невкусно и грустно. Зато эффективно. Вы избавились от всех отрицательных эффектов, которые могут снять зелья.')

    def fourthAction(self, other, ctx):
        possibleItemCodes = [237, 147, 307, 367, 207, 0, 0, 117]
        myCode = choice(possibleItemCodes)
        if myCode == 0:
            send(ctx, 'Травница не смогла изготовить что-то путное - одно мутное варево.')
            return 1
        self.inv.addItem(Item(myCode))
        send(ctx, f'Травнице удалось изготовить чудную вещицу - {Item(myCode)}!')
        if Chance(10 * self.lvl):
            send(ctx, 'Травница может сделать дополнительный ход!')
            return -1


    def levelup(self, ind=1):
        self.arm += 2 * ind
        super().levelup(ind)