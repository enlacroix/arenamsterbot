from string import Template

from core import root
from random import randint
from datastore.deffect import EFF
from datastore.dsources import SRC
from datastore.misc import RACES
from myrandom import Chance
from vkmodule import send
import varbank as vb
from resists.rstcls import Resist
from resists.rstmanager import ResistManager
from resists.rststates import Ward

# Призвать своего клона с {self.lvl} ОЗ. Не способен на создание предметов. 5 МР
# Дары Демиурга. Сгенерировать случайный предмет ценностью {1 + self.lvl // 4}-{3 + self.lvl // 5}, +эффект Отражение на себя, 3 МР.

class Inquisitor(root.Hero):
    def __init__(self, pvp_id):
        super().__init__(pvp_id)
        self.resists = ResistManager({SRC.MIND: Resist(60, Ward), SRC.FIRE: Resist(20), SRC.LOWERINGLEVEL: Resist(0, Ward)})

    def options(self, other):
        opt_rep = f'[1]* Булава Порядка. \n' \
                  f'[2] {{Воздух}} Пыточная молния. Ослабление СМ и снижение б.духа цели. 3 МР.\n' \
                  f'[3] Телекинез. Притянуть противника. {Chance(75+self.lvl, source=SRC.MOVEMENT).show(other)}, 3 МР \n' \
                  f'[4]* Мощный удар (+25% урона, -15% базовой точности) / Оглушение, {Chance(62 + self.lvl, SRC.WEAPON, SRC.STUN).show(other)} | Разбить броню. \n' \
                  f'[5]** {{Земля}} Град кристаллов. {Chance(50+self.lvl*3, source=SRC.EARTH).show(other)} Безмолвия на врага, 2 МР \n' + super().options(other)
        return opt_rep

    def secondAction(self, other: root.HeroInstance, ctx):
        x  = self.MagicPattern(other, ctx, SRC.AIR, 3, evadeCoef=-10, specialReport=Template(f'Инквизитор безжалостно применяет неконвенциональную пыточную молнию на противника. Нанесено $dmg урона, сила магии временно ослаблена.'))
        if x in (0, -1): return x
        other.addEffect(EFF.INTERFERENCE, 1 + self.lvl // 6, power=[0.25 + 0.02 * self.lvl])
        if other.race in (RACES.UNDEAD, RACES.ARTIFICIAL): return
        moraleDamage = randint(3, 6) + self.lvl
        other.morale -= moraleDamage
        report = f'{other} от пыток потерял {moraleDamage} боевого духа.'
        send(ctx, report)

    def thirdAction(self, other: root.HeroInstance, ctx):
        if other.IsGuarded(ctx): return -1
        if not self.spend_mana(3, ctx): return -1
        if self.evade(other, -20, ctx): return 0
        if self.luck(ctx, other) == -1: return 0
        if Chance(75+self.lvl, source=SRC.MOVEMENT).roll(other):
            if other.movement():
                send(ctx, f'{other} был перемещён на другой ряд!')
            else:
                send(ctx, f'{other} ограничен в своих перемещениях, поэтому попробуйте другое действие.')
                return -1
        else:
            send(ctx, f'Инквизитор не смог телекинезом сместить {other}. Экая досада.')

    def fourthAction(self, other: root.HeroInstance, ctx):
        res = self.MeleePattern(other, ctx, evadeCoef=15, multCoef=1.25)
        if res not in (0, -1):
            if other.stunMyself(Chance(162 + self.lvl, SRC.WEAPON)):
                send(ctx, f'Булава инквизитора попала прямиком в голову несчастного {other.cls_name}, что приводит к его оглушению.')
            else:
                send(ctx, f'Противника не удалось оглушить, однако инквизитор уничтожил {other.destroyArmor(res * 0.25)} брони {self.cls_name}.')
        return res

    def fifthAction(self, other, ctx):
        if not self.isAtSecondRow(ctx): return -1
        res = self.MagicPattern(other, ctx, source=SRC.EARTH, mana=2)
        if res not in (0, -1) and Chance(50+self.lvl*3, source=SRC.EARTH).roll(other):
            send(ctx, f'{other} был замьючен.')
            other.addEffect(EFF.SILENCE, 2)
        return res


    def protection(self, ctx):
        super().protection(ctx)
        self.addEffect(EFF.CONTR, 2)

    def startInventory(self):
        self.addRandItemsByTier(2)

    def levelup(self, ind=1):
        if vb.stage % 5 == 0 and ind > 0:
            self.arm += 20
            self.power += 10
        if self.health > 0:  # Чтобы не восставал из мертвых, когда сражается с наемником.
            self.heal(randint(10, 15 + self.lvl) * ind)
        self.mana += randint(1, 2) * ind
        self.dmg += (randint(1, 3) + self.lvl // 3) * ind
        super().levelup(ind)

