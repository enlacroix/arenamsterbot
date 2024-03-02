"""
Гном-пироман это смесь пиро и инженера из тф2, обязательно назови какую-нибудь абилку "как набухала сталь")
* - только ближний бой. ** - только дальний бой.
1. *Огнемёт безумного гения. Две случайные цели на любых рядах.
огнемёт имеет топливо и поражает две случайные цели. Тратится случайное кол-во топлива, и как только оно закончиться, нужно перезарядить огнемёт.
2. **Паровой арбалет. Разбить броню. (аля Защитник горна)
5. Самосожжение.

Удар по области - поразить фронтлейны ОБЕИХ команд.
"""
from random import randint, shuffle
from string import Template

from datastore.deffect import EFF
from datastore.dperks import PRK
from datastore.dsources import SRC
from datastore.misc import RACES
from resists.rstcls import Resist
from resists.rstmanager import ResistManager
from resists.rststates import Ward
from core.root import Hero, HeroInstance
from vkmodule import send
import varbank as vb

class Pyro(Hero):
    def __init__(self, _id):
        super().__init__(_id)
        self.resists = ResistManager({SRC.FIRE: Resist(0, Ward)})
        self.resists[SRC.FIRE].setWard()
        self.race = RACES.NONHUMAN
        self.skills.append(PRK.TECHNO)

    def options(self, other): # Братцы, да эти архиличи - просто малыши!
        opt_report = f'[1]* Огнемёт безумного гения, 2 случайные цели. \n ' \
                     f'[2]** Паровой арбалет / Разбить броню. Доп. урон по подожжённым. \n' \
                     f'[3] Огненная бомба. Поджог на первые ряды ОБЕИХ команд. Ряды вражеской команды будет перемешаны. \n' \
                     f'[4] Смола гномов. Наложить чары пламени на оружие союзника. \n'\
                     f'[5] Акт самосожжения. -{self.lvl * 6} морали выбранной цели, +20% урона и СМ лидеру отряда. \n' + super().options(other)
        return opt_report

    def firstAction(self, other, ctx):
        results = []
        for enemy in other.RandomUnitsFromMyTeam(2):
            results.append(self.MagicPattern(enemy, ctx, source=SRC.FIRE, mana=0, meleeFlag=True))
        if results == [-1, -1]: return -1 # todo ПРОТЕСТИРОВАТЬ
        return

    def secondAction(self, other: HeroInstance, ctx):
        if not self.isAtSecondRow(ctx): return -1
        eps = 10 + self.lvl if other.hasEffect(EFF.BURNING) else 0
        result = self.ArcherPattern(other, ctx, addComp=eps, specialReport=Template(f'Арбалетный болт, разогнанный энергией пара, наносит $dmg урона противнику. "Этот {other} - просто сосунок", - кричит гном.'))
        if result not in (0, -1): send(ctx, f'Вражеская броня была разбита на {other.destroyArmor(randint(2, 6 + self.lvl), -10)} единиц.')
        return result

    def thirdAction(self, other, ctx):
        #targets = filter(lambda x: x.position == 0, vb.teams[self.team] + vb.teams[other.team])
        targets = [x for x in vb.teams[self.team] + vb.teams[other.team] if x.position == 0]
        shuffle(vb.teams[other.team])
        for unit in targets:
            unit.addEffect(EFF.BURNING, 2 + self.lvl // 7, power=[1.3])
        descr = ', '.join(map(str, targets))
        send(ctx, f'Коктейль пироманьяка поражает следующие цели: {descr}.')


    def fourthAction(self, other, ctx):
        if self.allyActionForEnemy(other, ctx): return -1
        other.addEffect(EFF.FIREDWEAPON, 1 + self.lvl // 6)
        send(ctx, f'Используя особые румяна, гном придаёт огненные чары оружию {other}, рассказывая попутно истории о том, как "набухала сталь".')

    def fifthAction(self, other, ctx):
        if self.team == other.team: return -1
        self.kill()
        other.morale -= self.lvl * 6
        send(ctx, f'Гном демонстративно обливает себя бензином и указывает на {other}, крича: "Именно ОН повинен в моей кончине! УБИЙЦА." \n '
                  f'Пироман бросает зажжённую спичку в лужу бензина, которая незамедлительно вспыхивает. Загнанный в ловушку гном показывает палец вверх, говоря'
                  f'тем самым, что это вроде как всё понарошку, и у него есть План. \n Или нет, думаете вы, осматривая то, что осталось от {self}.'
                  f'{other.name}, тем не менее, под впечатлением и потерял {self.lvl * 6} боевого духа. Это будет сниться ему в кошмарах.')
        if len(vb.teams[self.team]) > 1 and vb.teams[self.team][0] == self:
            newLeader = vb.teams[self.team][1]
        else:
            newLeader = vb.teams[self.team][0]
        newLeader.power = round(newLeader.power * 1.2)
        newLeader.dmg = round(newLeader.dmg * 1.2)


    def levelup(self, ind=1):
        self.dmg += 2
        self.power += (2 + self.lvl // 3) * ind
        super().levelup(ind)
