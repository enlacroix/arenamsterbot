from datastore.deffect import EFF
from datastore.dperks import PRK
from datastore.dsources import SRC
from datastore.misc import RACES
from myrandom import Chance
from core.root import Hero
from utils import getMember
from vkmodule import send, longpoll, id_checker

class Specter(Hero):
    def __init__(self, _id):
        super().__init__(_id)
        self.race = RACES.UNDEAD
        self.skills.append(PRK.BONUS_MOVEMENT)

    def options(self, other):
        opt_report = f'[1] {{Разум}} Паралич цели (от точности) х2, {Chance(self.acc+self.lvl, source=SRC.MIND, extra=SRC.STUN).show(other)} \n' \
                     f'[2] Тёмный ритуал. Дать вард от Оружия, но цель потеряет {3 * self.lvl + 15} ОЗ. \n' \
                     f'[3] Сглаз. Наложить Метку на противника и снизить боевой дух на {self.lvl+3}. \n' \
                     f'[4] Кровавая трава. 80% шанс вызвать кровотечение у цели. \n' \
                     + super().options(other)
        return opt_report

    def preChoiceAction(self, other, ctx):
        other.mana -= 2
        if other.mana >= 0: send(ctx, 'Призрак поглотила 2 маны лидера.')

    def ghostPrl(self, other, ctx):
        if other.stunMyself(Chance(self.acc+self.lvl, source=SRC.MIND)):
            send(ctx, f'Холодные очи полуденницы приводят в ужас {other.cls_name}. Он обездвижен на один раунд.')
        else:
            send(ctx, f'Цель сопротивляется ужасу призрака и теряет только {other.harmWithSRC(SRC.MIND, self.power * 0.5)} здоровья.')

    def firstAction(self, other, ctx):
        self.ghostPrl(other, ctx)
        send(ctx, 'Укажите постфикс цели для второй атаки:')
        for choice in longpoll.listen():
            try: postfix = choice.obj['message']['text'].lower()
            except: continue
            if not id_checker(self.id, choice): continue
            if len(postfix) == 2 and postfix[0] in ('e', 'е'):
                B = getMember(self.enemyTeam, postfix, choice)
                if B == -1: continue
                self.ghostPrl(B, ctx)
                break

    def secondAction(self, other, ctx):
        other.resists[SRC.WEAPON].setWard()
        other.health -= 3 * self.lvl + 15
        send(ctx, f'Привидение грязно надругалось над телом {other}: его тошнит и он потерял {3 * self.lvl + 15} здоровья. Однако вард от Оружия есть вард от Оружия.')

    def thirdAction(self, other, ctx):
        other.addEffect(EFF.MARKED, 1 + self.lvl // 4)
        other.morale -= self.lvl + 3
        # Дать еще проклятье на неудачу?
        send(ctx, f'Призрак отмечает {other} смертной Меткой.')

    def fourthAction(self, other, ctx):
        if Chance(80):
            other.addEffect(EFF.BLEEDING, 2, power=[1+self.lvl*0.06, 10])
            send(ctx, f'Мерзкая тварь вызвала кровотечение!')
        else:
            send(ctx, f'Это фиаско, сестра!')