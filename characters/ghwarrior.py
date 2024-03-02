from datastore.deffect import EFF
from datastore.dsources import SRC
from datastore.misc import RACES
from myrandom import Chance
from resists.rstcls import Resist
from resists.rstmanager import ResistManager
from core.root import Hero
from vkmodule import send
import varbank as vb

class GhostWarrior(Hero):
    def __init__(self, pvp_id):
        super().__init__(pvp_id)
        self.race = RACES.UNDEAD
        self.ulta = 1
        self.resists = ResistManager({SRC.DEATH: Resist(85), SRC.HOLY: Resist(-35), SRC.WEAPON: Resist(20)})

    def getHunger(self):
        return round(1 + 0.15 * len(vb.Team.Entry(self.team).graveyard), 2)

    def options(self, other):
        opt_report = f'[1]* Призрачная катана x{self.getHunger()}, {Chance(65 +self.lvl * (1 if self.hasMaster() else 0.5), source=SRC.DEATH, extra=SRC.STUN).show(other)} шанс парализации. \n' \
                     f'[2] Сэппуку. Следующие удары катаны ([1]) будут поглощать здоровье противника.\n' \
                     f'[3] Горн мертвецов. Временные +{3+self.lvl//4} уровня на свой ряд. \n' \
                     f'[4] Примирение, {self.ulta} раз. Восстановить себе {self.max_hp // 4} ОЗ (c о/х). \n' \
                     + super().options(other)
        return opt_report

    def firstAction(self, other, ctx):
        x = self.MeleePattern(other, ctx, multCoef=self.getHunger())
        adjustingStunCoef = 1 if self.hasMaster() else 0.5
        if x not in (0, -1) and other.stunMyself(Chance(65 +self.lvl * adjustingStunCoef, source=SRC.DEATH)):
            send(ctx, f'Клинок воина-призрака парализовал {other.cls_name}!')
        return x

    def secondAction(self, other, ctx):
        self.addEffect(EFF.VAMPWEAPON, 2 + self.lvl // 5, power=[0.5 + 0.08*self.lvl])
        send(ctx, f'Катану охватывает красновато-кровавое свечение. Теперь она вампирическая. На время.')

    def thirdAction(self, other, ctx):
        for ally in self.getOwnRow():
            ally.addEffect(EFF.TEMPLVLUP, 2, power=[3+self.lvl//4])
        send(ctx, f'{self} использует свой фантомный горн, поднимая мастерство стоящих рядом с ним солдат.')

    def fourthAction(self, other, ctx):
        if self.ulta <= 0: return -1
        self.health += self.max_hp // 4
        self.ulta -= 1
        send(ctx, f'В результате медитаций нежить вылечила себя на {self.max_hp // 4}')

    def levelup(self, ind=1):
        if self.hidden_lvl % 5 == 0: self.ulta += 1
        self.heal(ind * 5)
        self.dmg += ind * 3
        self.ini += ind * 2
        super().levelup(ind)