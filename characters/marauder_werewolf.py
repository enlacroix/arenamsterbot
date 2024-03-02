from string import Template
from random import randint
import varbank as vb
from core import root
from background import stats_dict
from datastore.deffect import EFF
from datastore.dperks import PRK
from datastore.dsources import SRC
from datastore.misc import RACES
from myrandom import Chance
from resists.rstcls import Resist
from resists.rstmanager import ResistManager
from resists.rststates import Ward
from vkmodule import send



class Marauder(root.Hero):
    def __init__(self, pvp_id):
        super().__init__(pvp_id)
        self.ulta = 1
        self.skills.append(PRK.DOUBLE_USING_INVENTORY)
        self.race = RACES.ELF
        self.resists = ResistManager({SRC.POLYMORPH: Resist(25, Ward), SRC.HOLY: Resist(40)})

    def options(self, other):
        return f'[1] 🏹 Композитный лук, +25% урона против Метки. \n' \
               f'[2]** Подавляющий огонь. Замедление, уменьшение удачи {60+self.lvl}% (на ряд) \n' \
               f'[3]** Мощный выстрел. х1.25 урона, х2 шанс крита, но накладывается Слабость после исп-ния. \n' \
               f'[4] Безумно хочется быть первым. ➡️ Превращение в оборотня, {self.ulta} применений. \n' \
               f'[5] {{Сакральный}} Тёмное пламя, x{self.morale_boost()}(чем ниже мораль). Сжечь ману, {Chance(67, source=SRC.DEATH).show(other)}, 3 МР \n' + super().options(other)

    def startInventory(self):
        self.addRandItemsByTier(supremum=2)

    def morale_boost(self):
        if self.morale >= 0: return 1
        return 1 + round(abs(self.morale) / 100, 1)

    def protection(self, ctx):
        super().protection(ctx)
        self.dodge_bank += 1

    def firstAction(self, other, ctx): return self.ArcherPattern(other, ctx, multCoef=1.25 if other.hasEffect(EFF.MARKED) else 1)

    def secondAction(self, other: root.HeroInstance, ctx):
        for enemy in other.getOwnRow():
            enemy: root.HeroInstance
            self.ArcherPattern(enemy, ctx, multCoef=0.5, specialReport=Template(f'Мародёр обрушивает на противника дождь из зачарованных стрел, которые наносят $dmg урона.'))
            if Chance(60+self.lvl):
                enemy.addEffect(EFF.UNLUCKY, 1+self.lvl//5, power=[20])
                enemy.addEffect(EFF.SLOW, 1+self.lvl//5, power=[0.5])
                send(ctx, f'{enemy} был ослаблен и замедлен.')

    def thirdAction(self, other, ctx):
        self.addEffect(EFF.WEAKNESS, 2, power=[0.3])
        return self.ArcherPattern(other, ctx, multCoef=1.25, critCoef=2, specialReport=Template(f'Эльф производит особо сильный выстрел из лука, который совершенно выматывает стрелка. Нанесено $dmg урона.'))

    def fourthAction(self, other, ctx):
        if self.position != 0: self.movement()
        self.transformToAnotherClass(Werewolf)
        self.resists[SRC.WEAPON].setWard(self.lvl // 7 + 1)
        self.ini //= 2
        self.ulta -= 1
        send(ctx, 'Мародёр обращается к своему звериному началу и превращается в ужасного оборотня...')

    def fifthAction(self, other: root.HeroInstance, ctx):
        if not self.spend_mana(3, ctx): return -1
        if self.evade(other, 1, ctx): return 0
        report = f'Мародёр взывает к истинным Богам: землю под ногами {other.cls_name} охватывает чёрное пламя, которое наносит {other.harmWithSRC(SRC.HOLY, self.power * self.morale_boost())} урона. '
        if Chance(67, source=SRC.DEATH).roll(other):
            other.mana -= randint(3, 4)
            report += 'Пламя дополнительно уничтожает ману противника.'
        send(ctx, report)

    def levelup(self, ind=1):
        if vb.stage % 5 == 0: self.ulta += 1
        self.dmg += (randint(2, 5) + self.lvl // 2) * ind
        self.addGold(randint(30, 50) * ind)
        self.mana += ind
        self.power += (self.lvl // 2 + 1) * ind
        super().levelup(ind)


class Werewolf(root.Hero):
    def options(self, other):
        opt_rep = f'[1]* Разорвать плоть, {Chance(71 + self.lvl*2, SRC.EARTH).show(other)} наложить Ослабление (Земля) \n' \
                  f'[2]** Вечный голод. Вампиризм {int(round(self.health / self.max_hp, 2)*100 + 20 + self.lvl * 3)}% (эф-ый на низком здоровье), игнорирует охрану \n' \
                  f'[3] Успокоение. Обратное превращение, восстановление {20 + self.lvl * 5} ОЗ и боевого духа. \n ' \
                  f'[4] {{Вода}} Звериная желчь. DoT на колонну, уничтожающий дополнительно броню. \n' + super().options(other)
        return opt_rep

    def firstAction(self, other, ctx):
        x = super().MeleePattern(other, ctx)
        if x not in (0, -1) and Chance(71 + self.lvl*2, SRC.EARTH).roll(other):
            other.addEffect(EFF.WEAKNESS, 2, power=[0.5])
            send(ctx, 'Оборотень наложил на вас магический эффект Ослабления, который временно снизит ваш физический урон на 50%.')
        return x

    def secondAction(self, other, ctx):
        if not self.isAtSecondRow(ctx): return -1
        res = self.MeleePattern(other, ctx, ignoreGuard=True)
        y = round((self.health / self.max_hp + 0.2 + self.lvl * 0.03) * res)
        send(ctx, f'Ликантроп вонзает в вас свои зубы, пытаясь оторвать кусок плоти - его терзает безумный и вечный голод. Нанесено {res} урона, '
                  f'оборотень поглотил {self.heal(y)} ОЗ и восстановил {y // 5} маны.')


    def thirdAction(self, other, ctx):
        send(ctx, f'Заглушив в себе ярость, волколак вернулся в эльфийское обличие, восстановив {self.heal(20 + self.lvl * 5)} здоровья и восполнив {10 + self.lvl} единиц боевого духа.')
        self.transformToAnotherClass(Marauder)
        self.resists[SRC.WEAPON].setDefault()
        self.ini = stats_dict['Marauder'].ini  # Накопленная от ран инициатива теряется при превращении, но при втором превращении переначислится вновь.
        self.morale += 10 + self.lvl


    def fourthAction(self, other, ctx):
        for enemy in other.getOwnColumn(): enemy.addEffect(EFF.GALL, 2 + self.lvl // 5, power=[1 + self.lvl * 0.05])
        send(ctx, f'С клыков оборотня падает омерзительная желчь, которая окажет губительное влияние на ваше здоровье и крепкость доспех.'
                  f' Лицо {other} перемазано этой мерзостью.')

    def get_rage(self):
        return round(2 - self.health / self.max_hp, 2)

    def levelup(self, ind=1):
        if vb.stage % 5 == 0 and ind > 0:
            self.ulta += 1
        self.dmg += (randint(1, 3) + self.lvl//2) * ind
        self.crit += (self.lvl // 2 + 1) * ind
        self.ini = round(28 * self.get_rage())  # 28 - ополовиненная инициатива Мародёра (56)
        self.max_hp += (self.lvl * 2 + randint(1, 5)) * ind
        if ind > 0:
            self.morale -= randint(4, 6)
        super().levelup(ind)



