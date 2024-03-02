from string import Template

from core import root
from random import randint
from datastore.deffect import EFF
from datastore.dsources import SRC
from datastore.misc import RACES
from ditems.itemcls import Item
from myrandom import Chance
from resists.rstcls import Resist
from resists.rstmanager import ResistManager
from resists.rststates import Ward
from vkmodule import send


# Лечение (эффективнее на низком зд-вье)
# 1.2 if isinstance(other, root.Undead) else 1 - бонусный урон по нежити. Более того, каждому классу можно прописать свою фракцию, таку же как и Undead.
# Например, класс Nonhuman для орков, Myst для демонолога, Order для ординаторов и т.п.

class Paladin(root.Hero):
    def __init__(self, pvp_id):
        super().__init__(pvp_id)
        self.resists = ResistManager({SRC.HOLY: Resist(20), SRC.WATER: Resist(25, Ward), SRC.DESTROYARMOR: Resist(0, Ward)})
        self.ulta = 2

    def options(self, other):
        opt_rep = f'[1]* Парные клинки (двойная атака) \n' \
                  f'[2] Разжечь пламя, {self.ulta} применений. Пылающие мечи и вард от Огня на себя. \n' \
                  f'[3]* {{Святой}} Разбить душу (д/б, магия) / Поглотить {1 + self.lvl // 5} уровней, {Chance(70, SRC.HOLY, SRC.LOWERINGLEVEL).show(other)}, 2 МР. \n' \
                  f'[4]** Святое копьё (+25% урона по Нежити)➡️, +ускорение на себя. \n' \
                  f'[5] Военная молитва ➡️. +Регенерация и защита от Оглушения, 3 МР \n'\
                  + super().options(other)
        return opt_rep

    def firstAction(self, other, ctx):
        x = self.MeleePattern(other, ctx)
        if x in (0, -1): return x
        # Возможность выбрать другую цель для второй атаки?
        return self.MeleePattern(other, ctx)


    def secondAction(self, other, ctx):
        if self.ulta > 0:
            self.ulta -= 1
            self.resists[SRC.FIRE].setWard()
            self.addEffect(EFF.FIREDWEAPON, 2 + self.lvl // 5)
            send(ctx, f'Клинки паладина окутаны святым пламенем Младшего.')
        else:
            send(ctx, f'Недостаточно сил.')
            return -1

    def thirdAction(self, other: root.HeroInstance, ctx):
        x = self.MagicPattern(other, ctx, SRC.HOLY, 2, meleeFlag=True)
        if x in (0, -1): return x
        if Chance(70, SRC.HOLY, extra=SRC.LOWERINGLEVEL).roll(other):
            n = 1 + self.lvl // 5
            other.levelup(-n)
            self.levelup(n)
            send(ctx, f'Мститель разбивает душу противника и поглощает все знания и умения {other.cls_name}, отнимая {n} уровней. ')


    def fourthAction(self, other, ctx):
        if not self.isAtSecondRow(ctx): return -1
        self.movement()
        self.addEffect(EFF.HASTE, 2, power=[20])
        return self.MeleePattern(other, ctx, multCoef=1.25 if other.race == RACES.UNDEAD else 1, specialReport=Template(f'Защитник совершает пируэт из задних рядов, нанося особый удар по {other} на $dmg урона.'))


    def fifthAction(self, other, ctx):
        if not self.spend_mana(3, ctx): return -1
        self.addEffect(EFF.REGENHP, 2 + self.lvl // 5, power=[1.1])
        self.addEffect(EFF.STUNRESIST, 3, power=[50])
        self.movement()
        send(ctx, f'Молитва мстителя защищает его от параличей и оглушения и наложила Регенерацию {2 + self.lvl // 5} ступени.')


    def protection(self, ctx):
        super().protection(ctx)
        #effects.add_effect(self, 'crit_im', 2)

    def startInventory(self):
        # Случайный предмет из категории "Реликвии"
        self.inv.addSeveralItems(Item.createRandItemsByTypeAndTier(5, infimum=1, supremum=3))

    def levelup(self, ind=1):
        if self.hidden_lvl % 7 == 0:
            self.ulta += 1
            self.mana += 5
            self.inv.addItem(Item(475))
        self.arm += randint(1, 2) * self.lvl//2 * ind
        self.dmg += (2 + self.lvl // 4) * ind
        super().levelup(ind)
