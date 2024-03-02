from core import root
from random import randint
from string import Template
from datastore.deffect import EFF
from datastore.dperks import PRK
from datastore.dsources import SRC
from datastore.misc import RACES
from myrandom import Chance
from resists.rstcls import Resist
from resists.rstmanager import ResistManager
from resists.rststates import Ward
from vkmodule import send


class Witch(root.Hero):
    def __init__(self, pvp_id):
        super().__init__(pvp_id)
        self.gun = 4
        self.race = RACES.UNDEAD
        self.resists = ResistManager({SRC.FINALSTRIKE: Resist(25, Ward), SRC.DEATH: Resist(25, Ward), SRC.FIRE: Resist(-20), SRC.WATER: Resist(-20)})
        self.skills = [PRK.TECHNO, PRK.TALISMANS]

    def options(self, other):
        opt_rep = f'[1] Дамский револьвер {"" if self.lvl <= 8 else "x2, 75%"}, {self.gun} патрон(-а) | Заострённый каблучок \n' \
                  f'[2]* Молочные клыки. Вампиризм и (+резист к Последнему удару). 3 МР. \n' \
                  f'[3] Смертный приговор. Метка + дебафф резистов к Разуму и Смерти на {25+self.lvl*2}%. \n' \
                  f'[4]** Деградация. Понизить уровень на {self.lvl // 6 + 1}, {Chance(70+self.lvl*2, SRC.MIND, SRC.LOWERINGLEVEL).show(other)}. 4 МР,' \
                  f'{self.power // 3 + self.lvl}% забыть перк. \n' \
                  f'[5] {{Земля / Превращение}} Превратить цель в толстого беса, 4 МР, {Chance(65+self.lvl, SRC.EARTH, SRC.POLYMORPH).show(other)} \n'\
                  + super().options(other)
        return opt_rep


    def firstAction(self, other, ctx):
        if self.gun > 0:
            res = self.ArcherPattern(other, ctx, source=SRC.ARROWS)
            if res == -1: return res
            self.gun -= 1
            if self.gun > 0 and self.lvl > 8 and Chance(75):
                send(ctx, f'Умудрённая опытом {self} стреляет ещё раз, используя технику стрельбы по-македонски - с двух рук! Что может быть круче...')
                res = self.ArcherPattern(other, ctx, source=SRC.ARROWS)
                self.morale += 5
                self.gun -= 1
            return res
        return self.MeleePattern(other, ctx, armorIgnore=0.5, specialReport=Template('Патроны кончились, миледи. Не отчаиваясь, вы совершаете прыжок и маленьким каблучком засаживаете аккурат в пах врага на $dmg урона. Это должно быть очень больно.'))


    def secondAction(self, other, ctx):
        res = self.MagicPattern(other, ctx, SRC.DEATH, 3, meleeFlag=True, specialReport=Template('Ведьмочка с шипением бросается на вас и вонзает острые клычки в шею, нанося $dmg урона'))
        if res not in (0, -1):
            self.resists[SRC.FINALSTRIKE].changeValue(5 + self.lvl // 2)
            send(ctx, f'Она смогла восстановить {self.heal(res // 3 + round(other.health) * 0.12)} здоровья.')
        return res

    def thirdAction(self, other, ctx):
        other.addEffect(EFF.MARKED, 2 + self.lvl // 6)
        other.addEffect(EFF.DEATHSENTENCE, 2, power=[25 + self.lvl*2, 25 + self.lvl*2])
        send(ctx, f'{self} указывает белой детской ручкой на вас и выносит вам свой вердикт...')

    def fourthAction(self, other: root.HeroInstance, ctx):
        if other.IsGuarded(ctx): return -1
        if not self.spend_mana(4, ctx): return -1
        if self.evade(other, -25, ctx): return 0
        if Chance(70+self.lvl*2, SRC.MIND, SRC.LOWERINGLEVEL).roll(other):
            other.levelup(-(self.lvl // 6 + 1))
            report = f'Ведьма загружает в ваш мозг двадцать сезонов Наруто, разрушая некоторые нейронные связи в мозгу. Ваш уровень понижен на {self.lvl // 7 + 1}. '
            if Chance(self.power // 3 + self.lvl) and not other.isSummon:
                other.skills.pop(randint(0, len(other.skills) - 1))
                report += f'Более того, ваш оппонент забыл какой-то из выученных им перков!'
        else:
            report = 'Вам не удалось понизить уровень противника... Какая досада. '
        send(ctx, report)


    def fifthAction(self, other: root.HeroInstance, ctx):
        if other.IsGuarded(ctx): return -1
        if not self.spend_mana(4, ctx): return -1
        if Chance(65+self.lvl, SRC.EARTH, SRC.POLYMORPH).roll(other):
            other.transformToAnotherClass(root.Imp)
            other.memory[1] = other.arm
            other.arm = 0
            send(ctx, 'Ведьма обращает врага в жалкого беса, который не может использовать особые атаки и теряет всю броню.')
            other.addEffect(EFF.IMPISH, 2)
        else:
            send(ctx, f'Превращение в беса не удалось!')


    def levelup(self, ind=1):
        if self.hidden_lvl % 5 == 0 and ind > 0:
            self.gun += 3
            self.dmg += randint(10, 15)
        self.mana += ind * randint(1, 2)
        self.power += (self.lvl // 2 + 3) * ind
        self.resists[SRC.EARTH].changeValue(3 * ind)
        self.resists[SRC.MIND].changeValue(2 * ind)
        super().levelup(ind)

    def protection(self, ctx):
        self.addEffect(EFF.FOCUSED, 2, power=[25])
        self.mana += 3
        super().protection(ctx)

    def startInventory(self):
        self.addRandItemsByTier(infimum=1, supremum=3, count=randint(1, 2))





