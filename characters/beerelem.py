from random import randint

from datastore.deffect import EFF
from datastore.misc import RACES
from myrandom import Chance
from core.root import Hero
from vkmodule import send


class BeerElemental(Hero):
    def __init__(self, _id):
        super().__init__(_id)
        self.ulta = 3
        self.race = RACES.MYST

    def options(self, other):
        opt_report = f'[1] "Homie De Flanders". Увеличение боевого духа на {10+self.lvl*2}, если депрессия (<0), иначе +5 пт. \n ' \
                     f'[2] "МЧС, Классическое". Опьянение, {70 + self.lvl*2}%: временно уменьшить точность \n' \
                     f'[3] "Огуречное". Дать {1 + self.lvl//5} гарант крит атаку. \n' \
                     f'[4] "Торпеда". Отравление на противника, осталось {self.ulta} шт. \n'\
                     + super().options(other)
        return opt_report

    def preChoiceAction(self, other, ctx):
        casino = -randint(10, 80)
        self.addGold(casino)
        send(ctx, f'Пивной элементаль просадил {-casino} золота в азартные игры!')

    def firstAction(self, other, ctx):
        other.morale = other.morale + 10 + self.lvl*2 if other.morale < 0 else other.morale + 5
        send(ctx, f'Пиво 🍺 течёт во мне, я един с пивом 🍻 ... \n Пиво 🍺 течёт во мне, я един с пивом 🍻 ... \n Пиво 🍺 течёт во мне, я един с пивом 🍻 ... ')

    def secondAction(self, other, ctx):
        if Chance(70 + self.lvl*2):
            other.addEffect(EFF.DRUNK, 2, power=[20+self.lvl])
            send(ctx, f'Смотрю тебя с 2009, стал пивным алкоголиком, спасибо за юность!')
        else:
            send(ctx, f'[ПРОВАЛ]. Вы забыли, что обещания действуют один час. Элементаль укатил на пьянку, счастливо оставаться.')

    def thirdAction(self, other, ctx):
        if self.allyActionForEnemy(other, ctx): return -1
        other.crit_bank += 1 + self.lvl//5
        send(ctx, f'Есть информация, что следующая атака {other} будет крайне удачной.')


    def fourthAction(self, other, ctx):
        if self.ulta > 0:
            self.ulta -= 1
            other.addEffect(EFF.POISON, 2, power=[1.5])
            send(ctx, f'Какая мерзость... {other} грозит трёхдневный курс промывания.')
        else:
            send(ctx, 'У вас нет "снарядов".')
            return -1

    def levelup(self, ind=1):
        if self.hidden_lvl % 6 == 0: self.ulta += 1
        super().levelup(ind)