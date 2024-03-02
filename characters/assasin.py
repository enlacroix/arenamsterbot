import random
from core import root
from random import randint
from datastore.deffect import EFF
from datastore.dsources import SRC
from ditems.itemcls import Item
from myrandom import Chance
from resists.rstcls import Resist
from resists.rstmanager import ResistManager
from resists.rststates import Ward
from vkmodule import send
import varbank as vb


class Assassin(root.Hero):
    def __init__(self, _id):
        super().__init__(_id)
        self.dnote = 0  # модификатор мгновенного убийства
        self.darts = 2
        self.kira = 0
        self.resists = ResistManager({SRC.MIND: Resist(-25), SRC.DEATH: Resist(35, Ward)})

        '''Новые атрибуты, которые можно удалить.'''
        self.cum_rage = 0
        self.radius = 0
        self.authority = 0
        self.gun = 1
        self.horseIsDead = True

    def options(self, other):
        opt_rep = f'[1]* {{Оружие}} Заточенный стилет. ' \
                  f'\n[2] Звон смерти. Превратиться в случайного участника сражения, +мораль на {self.lvl + 3} пт.' \
                  f'\n[3] Приговор шинигами. {self.dnote}% оставить врагу 1 ОЗ. {self.decor()}' \
                  f'\n[4] {{Смерть}} Отравленный дротик. Осталось - {self.darts}. ' \
                  f'\n[5] Злобный хохот психопата. Хамелеон, +тетрадь, -рассудок. \n' + super().options(other)
        return opt_rep

    def startInventory(self):
        self.addRandItemsByTier(infimum=1, supremum=4, count=1)

    def firstAction(self, other, ctx):
        # other.beer += 1 для тестирования исключений и ошибок
        return self.MeleePattern(other, ctx)

    def secondAction(self, other, ctx):
        # todo сделать выборку из трех и предложить выбор из трёх классов. Abbess, Detective, DemonLord, OrcKing, Inquisitor, Paladin, Witch, Archlich
        chosenClass = random.choice([x.__class__ for x in vb.teams[0]+vb.teams[1] if x.__class__ != Assassin])
        self.transformToAnotherClass(chosenClass)
        self.cls_name = 'Мимик ' + self.cls_name
        self.morale += self.lvl + 3
        send(ctx, f'Ассасин достаёт пыльные серебряные карманные часы и через секунду превращается в одну из убиенных жертв... Временно он становится {self.cls_name}')
        self.addEffect(EFF.POLYMORPH, 2)


    def thirdAction(self, other, ctx):
        if self.kira == 0:
            if Chance(self.dnote):
                send(ctx,
                     'Дрожащими пальцами вы вписываете имя своего оппонента в тетрадь, надеясь, что на сей раз голоса указали верное. О ДА! '
                     'Сердечный приступ настигает противника! Остается только добить его, ведь он сохранил 1 ОЗ...')
                other.health = 1
                self.morale += 15
                self.dnote -= 10
            else:
                send(ctx,
                     'Увы, видимо вы еще недостаточно в контакте с Богами, так как ничего не произошло после того, как вы вписали имя. Голова болит невыносимо: вы подвели голоса, которые'
                     ' так рассчитывали на вас. Вы временно ослаблены на последующие два раунда.')
                self.morale -= 14
                self.dnote += 7
                self.addEffect(EFF.FALSEKIRA, 3, [0.5, 0.5])
                send(ctx, 'Обессиленный своим провалом, вы бессознательно хотите сдаться - ваше уклонение снижено вдвое,'
                          ' а критические атаки стали в два раза хуже.')
            self.kira = 3
        else:
            send(ctx, f'Вы еще не отошли от предыдущего применения Тетради. И вообще нельзя работать так эффективно, нужно еще немного повыделываться! ')
            return -1

    def fourthAction(self, other, ctx):
        if self.darts > 0:
            self.darts -= 1
            if self.evade(other, 1, ctx):
                return 0
            x = randint(1, 5) + self.lvl
            send(ctx,
                 f'Ассасин кидает ядовитый дротик в противника. Нанесено {x} урона. Противник отравлен, а голоса в вашей голове поутихли.')
            other.health -= x

            other.addEffect(EFF.POISON, 2, power=[1.2])
        else:
            send(ctx, 'Ядовитые дротики кончились, зайдите позже.')
            return -1

    def fifthAction(self, other, ctx):
        x = randint(4, 8)
        z = randint(3, 6)
        self.morale -= x
        self.addEffect(EFF.CHAMELEON, 1, [20])
        self.dnote += z
        send(ctx,
             f'Разразившись дьявольским хохотом, вы кричите о том, что вы УЖЕ победили, и всё идёт по вашему Плану. Вы накладываете на себя эффект Хамелеона, '
             f'усиливаете мощь Тетради на {z}%, но теряете {x} боевого духа.')

    def levelup(self, ind=1):
        if vb.stage % 4 == 0 and ind > 0:
            self.darts += randint(1, 2)
            self.inv.addItem(Item(107))
        self.dnote += 3 * ind
        self.crit += randint(1, 3) * ind
        self.dmg += self.lvl * ind
        super().levelup(ind)
        if self.kira != 0 and ind > 0:
            self.kira -= 1

    def protection(self, ctx):
        super().protection(ctx)
        self.crit_bank += 1

    def decor(self):
        if self.kira != 0:
            return f'Осталось {self.kira} рнд до применения.'
        return ''
