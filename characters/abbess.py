from random import randint, sample
from core.root import Hero, HeroInstance
from datastore.deffect import EFF
from datastore.dperks import PRK
from datastore.dsources import SRC
from myrandom import Chance
from resists.rstcls import Resist
from resists.rstmanager import ResistManager
from resists.rststates import Ward
from vkmodule import send
import varbank as vb
'''
Дева-воительница с копьем, амазонка?
'''

class Abbess(Hero):
    def __init__(self, pvp_id):
        super().__init__(pvp_id)
        self.resists = ResistManager({SRC.IMITATION: Resist(0, Ward), SRC.AIR: Resist(20, Ward), SRC.EARTH: Resist(15)})
        self.merchant = 0.2
        self.skills.append(PRK.GRAND_MERCHANT)
        self.skills.append(PRK.RELICS)


    def options(self, other):
        opt_rep = f'[1] {{Святой}} Копьё Солнца / Замедление {75 + self.lvl}%, 2 МР\n' \
                  f'[2]** Божественная длань. Массовое лечение, {20+self.lvl*2}% поднять уровень союзника, 3 МР \n'\
                  f'[3] Святая броня. Временное усиление брони союзника и случайный вард цели и себе, 3 МР  \n' \
                  f'[4] Перерождение. Рассеивание ВСЕХ эффектов на ряду цели заклинания \n'\
                  f'[5] Призыв к оружию. Накладывает Контрудар на ряд цели. \n' + super().options(other)
        return opt_rep

    def startInventory(self):
        self.addRandItemsByTier(supremum=3)

    def firstAction(self, other, ctx):
        res = self.MagicPattern(other, ctx, SRC.HOLY, 2)
        if res not in (0, -1) and Chance(75 + self.lvl):
            other.addEffect(EFF.SLOW, power=[0.5 + self.lvl/25], rounds=2)
            if Chance(25+self.lvl): other.isForbiddenToResurrect = True
        return res

    def secondAction(self, other, ctx):
        if not self.spend_mana(3, ctx): return -1
        if not self.isAtSecondRow(ctx): return -1
        heal_report = ' '
        for ally in vb.teams[self.team]:
            x = self.power + self.lvl + randint(1, 15)
            heal_report += f'{ally.cls_name} восстановил(-а) {ally.heal(x)} здоровья. \n'
            if Chance(20 + self.lvl*2):
                ally.levelup()
        send(ctx, heal_report)


    def thirdAction(self, other: HeroInstance, ctx):
        if self.allyActionForEnemy(other, ctx): return -1
        if not self.spend_mana(3, ctx): return -1
        other.addEffect(EFF.STONEFLESH, 2 + self.lvl // 4, power=[20+self.lvl*2])
        randSRCs = sample([SRC.FIRE, SRC.AIR, SRC.WEAPON, SRC.ARROWS, SRC.WEAPON, SRC.EARTH, SRC.WATER, SRC.MIND, SRC.DEATH, SRC.STUN], 2)
        first, second = randSRCs
        self.resists[first].setWard()
        other.resists[second].setWard()
        send(ctx, f'Святая броня усиливает защиту от оружия и дарует вард от случайного источника: {self} - защиту от {first}, {other} - {second}.')


    def fourthAction(self, other: HeroInstance, ctx):
        if self.allyActionForEnemy(other, ctx): return -1
        for unit in other.getOwnRow():
            for eff in unit.effects.pool:
                if eff.canRemove: eff.rounds = 0
        send(ctx, 'Все эффекты были сняты.')

    def fifthAction(self, other, ctx):
        for ally in other.getOwnRow():
            ally.addEffect(EFF.CONTR, 2 + self.lvl//4)
        send(ctx, f'Аббатиса призывает всех к оружию!')

    def protection(self, ctx):
        self.addEffect(EFF.LUCKY, 2, power=[20])
        super().protection(ctx)

    def levelup(self, ind=1):
        if vb.stage % 6 == 0 and ind > 0: self.dodge_bank += 1
        self.power += (randint(0, 2) + self.lvl // 2)* ind
        self.mana += ind
        self.max_hp += 5 * ind
        super().levelup(ind)




