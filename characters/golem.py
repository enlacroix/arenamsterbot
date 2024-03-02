from random import randint
from datastore.deffect import EFF
from datastore.dsources import SRC
from datastore.misc import RACES
from myrandom import Chance
from resists.rstcls import Resist
from resists.rstmanager import ResistManager
from resists.rststates import Ward
from core.root import Hero, HeroInstance
from vkmodule import send
import varbank as vb

class GoldGolem(Hero):
    def __init__(self, _id):
        super().__init__(_id)
        self.race = RACES.ARTIFICIAL
        self.isForbiddenToResurrect = True
        self.resists = ResistManager({SRC.FIRE: Resist(25, Ward), SRC.AIR: Resist(25, Ward), SRC.DEATH: Resist(25)})
        self.addEffect(EFF.REFLECTION, 6)
        self.isMercenary = True

    def options(self, other):
        opt_report = f'[1]* Апперкот машины, {Chance(20+self.lvl, source=SRC.WEAPON, extra=SRC.STUN).show(other)} нокаута. \n ' \
                     f'[2] {{Разум}} Загадки во тьме. Наложить Помехи(?), поглотить ману, {Chance(70, source=SRC.MIND).show(other)} \n' \
                     f'[3] Блестящее покрытие. Наложение эффекта сопротивления к стихиям на цель. \n'\
                     f'[4] Временно увеличить силу магии на {25+5*self.lvl}% всем в отряде. \n' + super().options(other)
        return opt_report

    def preChoiceAction(self, other, ctx):
        x = self.getRandomUnitsFromTeamWhichNotEqualMe(self.team, 1)
        if len(x) > 0 and Chance(50): x[0].resists[SRC.LOWERINGLEVEL].setWard()

    def firstAction(self, other, ctx):
        result = self.MeleePattern(other, ctx)
        if result not in (0, -1) and other.stunMyself(Chance(20+self.lvl, source=SRC.WEAPON)):
            send(ctx, f'Голем отправляет противника в глубокий нокаут. {other} описывает красивую дугу и вылетает за пределы арены.')
        return result

    def secondAction(self, other, ctx):
        if Chance(70, source=SRC.MIND).roll(other):
            x = randint(2, 3)
            send(ctx, f'"Одна твоя загадка охренительней другой! Меня они, сударь, уже доконали!", - раздражённо говорит оппонент, не решив ни одной из предложенных задач. '
                      f'Самооценка его падает,  и поглощена мана на {x} пт.')
            other.mana -= x
            other.addEffect(EFF.INTERFERENCE, 1, power=[0.25 + self.lvl//25])
            self.getMaster().mana += x
        else:
            send(ctx, f'Оппонент с легкостью решает все загадки голема, попросив даже задачу со звездочкой. Он победно тыкает в вас пальцем '
                      f'и кричит "А у меня сошелся ответ!". Вы чувствуете, что мораль {other} выросла.')
            other.morale += 10

    def thirdAction(self, other: HeroInstance, ctx):
        if self.allyActionForEnemy(other, ctx): return -1
        other.addEffect(EFF.ELEMENTALPROTECTION, 2, power=[40+self.lvl])
        send(ctx, f'Голем даёт вам парочку уроков как выглядеть также неотразимо, как он.')

    def fourthAction(self, other, ctx):
        for ally in tuple(filter(lambda x: x != self, vb.teams[self.team])):
            ally: HeroInstance
            ally.addEffect(EFF.ABSOLUTEPOWER, randint(1, 2), power=[0.25 + self.lvl * 0.05])
        send(ctx, f'Голем испускает энергетическое поле, входящее в резонанс с союзными ему чародеями.')


    def levelup(self, ind=1):
        self.dmg += 2 * ind
        super().levelup(ind)