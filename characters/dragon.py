from string import Template
from core import root
from random import shuffle
from datastore.deffect import EFF
from datastore.dsources import SRC
from datastore.misc import RACES
from myrandom import Chance
from resists.rstcls import Resist
from resists.rstmanager import ResistManager
from resists.rststates import Ward, Immunity
from vkmodule import send, longpoll, id_checker
import varbank as vb


class Dracolich(root.Hero):
    size = 2

    def __init__(self, pvp_id):
        super().__init__(pvp_id)
        self.resists = ResistManager({SRC.MOVEMENT: Resist(0, Ward), SRC.DEATH: Resist(80, Ward), SRC.LOWERINGLEVEL: Resist(0, Immunity), SRC.POLYMORPH: Resist(0, Ward)})
        self.race = RACES.UNDEAD

    def preChoiceAction(self, other, ctx):
        send(ctx, f'Дракон регенерирует на {self.heal(self.max_hp // 6)} здоровья. \n')

    def calculateLowHPCoef(self):
        return (1 - self.health / self.max_hp) * 36

    def options(self, other):
        opt_rep = f'[1] Дыхание смерти. Массовый магический урон и отравление ({70 + self.lvl}%). \n'\
                  f'[2]* Гнилые испарения. Падение боевого духа, Ослабление и перемешивание внутри рядов противника. \n'\
                  f'[3] Пожирание. Если у цели меньше 20% от макс ОЗ, то моментальная смерть. \n'\
                  f'[4] Высшая Некромантия. Воскресить нежить, убитую во время боя. \n'\
                  f'[5]* Удар хвостом. 75% игнорирование брони по Метке. \n' + super().options(other)
        return opt_rep

    def firstAction(self, other: root.HeroInstance, ctx):
        for enemy in vb.teams[other.team]:
            enemy: root.HeroInstance
            x = self.MagicPattern(enemy, ctx, mana=-1, source=SRC.DEATH, evadeCoef=-self.calculateLowHPCoef())
            if x not in (0, -1) and Chance(70+self.lvl): enemy.addEffect(EFF.POISON, 2, power=[1.3 + self.lvl * 0.03])

    def secondAction(self, other: root.HeroInstance, ctx):
        shuffle(vb.teams[other.team])
        report = f''
        for enemy in other.getOwnRow():
            report += f'{enemy} потерял {7 + self.lvl*2} боевого духа. '
            enemy.morale -= 7 + self.lvl*2
            if Chance(85):
                enemy.addEffect(EFF.WEAKNESS, 2, power=[0.5])
                report += 'И бьл ослаблен.'
            report += '\n'
        send(ctx, report)


    def thirdAction(self, other, ctx):
        if other.health >= other.max_hp * 0.2:
            send(ctx, f'В {other} еще слишком много жизненных сил, чтобы провести эту атаку.')
            return -1
        other.kill()
        send(ctx, f'Дракон пожирает ослабевшего {other}, не оставляя тому ни единого шанса на спасение. Овация, аплодисменты.')

    def fourthAction(self, other, ctx):
        report = f'[0]. Выйти из меню. \n'
        N = len(vb.Team.Entry(self.team).graveyard)
        for i, unit in enumerate(vb.Team.Entry(self.team).graveyard):
            report += f'{i + 1}. {unit}, уровень {unit.lvl}, {"🚫" if unit.isForbiddenToResurrect else "✅"} \n'
        send(ctx, report)
        for event in longpoll.listen():
            if not id_checker(self.id, ctx): continue
            current: str = event.obj['message']['text'].lower()
            if current == '0': break
            if current.isdigit() and int(current) <= N:
                target: root.HeroInstance = vb.Team.Entry(self.team).graveyard[int(current) - 1]
                if target.race != RACES.UNDEAD:
                    send(ctx, f'Цель не является нежитью, дракон не способен её воскресить!')
                    continue
                if not target.animate(self.team):
                    send(ctx, 'Цель невозможно поднять, так как она была подвержена проклятью искоренения.')
                    continue
                else:
                    send(ctx, f'{target} успешно восстал из мёртвых!')
                    if Chance(80): target.isForbiddenToResurrect = True
                    break

    def fifthAction(self, other, ctx):
        return self.MeleePattern(other, ctx, armorIgnore=0.25 if other.hasEffect(EFF.MARKED) else 0, specialReport=Template(f'Змий обрушивает на {other} свой хвост, нанося $dmg урона.'))

    def levelup(self, ind=1):
        self.dmg += 2 * ind
        self.power += 2 * ind
        super().levelup(ind)