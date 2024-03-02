from random import randint
from datastore.deffect import EFF
from datastore.misc import RACES
from myrandom import Chance
from core.root import Hero, HeroInstance
from datastore.dsources import SRC
from resists.rstcls import Resist
from resists.rstmanager import ResistManager
from resists.rststates import Ward
from vkmodule import send



# class LichSummons(root.Hero):
#     def death(self, ctx):
#         if super().death(ctx):
#             try:
#                 self.master.grade = 0
#                 send(ctx, f'Гибель {self.cls_name} разрушила планы лича - весь процесс придётся начинать заново...')
#                 return 1
#             except AttributeError:
#                 return 0

# f'[1] Экзальтация мертвых. Лечение отряда (с возможностью воскрешения хозяина), 4 МР. \n' \
# f'[2] Высшая защита. Наложить временную броню на повелителя, 2 МР \n' \
# f'[3] Открыть раны. Искоренение и наложение кровотечения {mf.show_chance(80, other.resists[2])}% на противника. \n' \


class Zombie(Hero):
    def __init__(self, pvp_id):
        super().__init__(pvp_id)
        self.race = RACES.UNDEAD
        self.resists = ResistManager({SRC.FIRE: Resist(-25), SRC.DEATH: Resist(50), SRC.HOLY: Resist(-40)})


    def options(self, other):
        opt_report = f'[1]* Укус вслепую / Уменьшить боевой дух. +25% точности против Метки. \n' \
                     f'[2] Заразное касание. {60+self.lvl*2}% одарить цель Пепельной язвой: ослабить мощь и инициативу. \n' \
                     f'[3] Инфицирование (после 6 уровня). Превратить саммона противника в зомби {min(60, 22 + self.lvl * 3)}%, {min(60, 22 + self.lvl * 3)}% \n' \
                     + super().options(other)
        return opt_report

    def firstAction(self, other, ctx):
        x = self.MeleePattern(other, ctx, evadeCoef=-25 if other.hasEffect(EFF.MARKED) else 0)
        if x not in (0, -1):
            cf = 1 if other.morale <= 0 else 1.5
            dirt = round(randint(3, 4 + self.lvl) * other.getSRCFactor(SRC.MIND) * cf)
            if dirt > 0: send(ctx, f'{other.cls_name} теряет {dirt} пунктов боевого духа от укуса омерзительного {self}.')
            other.morale -= dirt
        return x

    def secondAction(self, other, ctx):
        if other.position != 0: return -1
        if other.race in (RACES.UNDEAD, RACES.ARTIFICIAL):
            send(ctx, 'Нежить и механизмы невосприимчивы к данному воздействию. ')
            return -1
        if Chance(60 + self.lvl*2):
            other.addEffect(EFF.ASHILLNESS, power=[0.25, 0.25], rounds=1+self.lvl//5)
            send(ctx, f'{other} был успешно заражен.')
        else:
            send(ctx, f'Сработал спасбросок от болезни.')

    def thirdAction(self, other: HeroInstance, ctx):
        if self.lvl < 6:
            send(ctx, 'Твой уровень ещё слишком мал! Тебе надо тренироваться.')
            return -1
        if other.race in (RACES.UNDEAD, RACES.ARTIFICIAL):
            send(ctx, 'Нельзя укусить данное существо, так как невозможно заразить нежить или механизм.')
            return -1
        if not other.isSummon:
            send(ctx, f'{other} не является призванным существом, поэтому его обращение невозможно.')
            return -1

        if Chance(min(60, 22 + self.lvl * 3)):
            other.transformToAnotherClass(Zombie)
            send(ctx, f'МОЗГИ! Ходячий труп своим укусом превратил {other} в своего братика-зомби! Они обнимаются...')
        else:
            send(ctx, f'Заражение не прошло, мертвец смог только ослабить урон противника на {self.lvl} пт.')
            other.dmg -= self.lvl

    def levelup(self, ind=1):
        self.max_hp += ind * 5
        self.heal(ind * 3)
        self.dmg += ind * 4
        super().levelup(ind)


class SkeletonChampion(Hero):
    def __init__(self, pvp_id):
        super().__init__(pvp_id)
        self.race = RACES.UNDEAD
        self.resists = ResistManager({SRC.AIR: Resist(-25), SRC.DEATH: Resist(65), SRC.ARROWS: Resist(50, Ward), SRC.HOLY: Resist(-30)})

    def options(self, other):
        opt_report = f'[1]* Боевой молот / Разбить броню. \n' \
                     f'[2] Псалом неупокоенных. Снижение сопротивления к Смерти, +точность \n' \
                     f'[3] Костяной щит. Охрана своего хозяина, активировать Контрудар. \n' \
                     f'[4] Контракт на убийство. Навесить Метку на цель и дебаффнуть уклонение. \n' \
                     + super().options(other)
        return opt_report

    def firstAction(self, other, ctx):
        x = self.MeleePattern(other, ctx)
        if x not in (0, -1): send(ctx, f'Чемпионский молот уничтожил {other.destroyArmor(randint(5, 10 + self.getMaster().lvl), 0)} брони противника. ')
        return x

    def secondAction(self, other: HeroInstance, ctx):
        other.resists.changeValue(SRC.DEATH, -randint(6, 10))
        self.acc += self.getMaster().lvl + 2
        send(ctx,
             f'Скелет откладывает в сторону свой молот и складывает руки в молитвенном жесте. {other} начинает знобить неестественным, могильным холодом.'
             f' Теперь {other} чувствуете, что ваша смерть стала еще ближе. Скелет же за свою праведность был вознаграждён {self.getMaster().lvl - 2}% точности.')

    def thirdAction(self, other, ctx):
        if not self.hasMaster():
            send(ctx, 'Нет цели для защиты!')
            return -1
        self.master.addEffect(EFF.GUARDED, 1)
        self.addEffect(EFF.CONTR, 2)
        send(ctx, f'{self.master} теперь под охраной скелета.')

    def fourthAction(self, other, ctx):
        other.addEffect(EFF.MARKED, 3)
        other.addEffect(EFF.FATMAN, 2, power=[20+self.lvl])
        send(ctx, f'Скелет неприятно улыбается и указывает краем своего молота на {other}. Он чувствует, что на него открылась охота, а в ногах появилась странная слабость...')


    def levelup(self, ind=1):
        self.heal(ind * 7)
        self.dmg += ind * randint(2, 5)
        self.crit += ind * 2
        if self.hidden_lvl > 8 and not self.isMercenary: self.isMercenary = True
        super().levelup(ind)



