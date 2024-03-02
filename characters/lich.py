from random import randint
from string import Template
from core import root
from characters.eviltree import EvilTree
from characters.ghwarrior import GhostWarrior
from datastore.deffect import EFF
from datastore.dperks import PRK
from datastore.dsources import SRC
from datastore.misc import RACES
from myrandom import Chance
from resists.rstcls import Resist
from resists.rstmanager import ResistManager
from resists.rststates import Ward
from summon_classes.undeads import Zombie, SkeletonChampion
from vkmodule import send, longpoll, id_checker
import varbank as vb
# Переставить порядок импортов?


class Archlich(root.Hero):
    def __init__(self, pvp_id):
        super().__init__(pvp_id)
        self.race = RACES.UNDEAD
        self.radius = 1
        self.max_summons = 2
        self.skills += [PRK.ORBS]
        self.resists = ResistManager({SRC.FIRE: Resist(-20), SRC.DEATH: Resist(75, Ward), SRC.HOLY: Resist(-20)})

    def options(self, other):
        opt_rep = f'[1] ☠ Облако смерти (+{self.radius} случайные цели), 3 МР \n' \
                  f'[2] Призыв новой нежити (свой п-ф) | Эволюция (п-ф текущей нежити), 3 МР. \n' \
                  f'[3] Восстановить ОЗ и +уровень выбранного саммона | Наложить вампиризм на союзника, 2 МР. \n' \
                  f'[4] 💫 Показ коллекции. Ужас и снять контрудар, {Chance(80, SRC.MIND).show(other)}, 3 МР \n' \
                  f'[5] Поглотить душу. Пожертвовать союзником в обмен на его 75% уровней и восстановление маны. \n ' + super().options(other)
        return opt_rep

    def startInventory(self):
        self.addRandItemsByTier(supremum=4)

    def firstAction(self, other, ctx):
        result = self.MagicPattern(other, ctx, SRC.DEATH, mana=3)
        if result not in (0, -1):
            for target in other.getRandomUnitsFromTeamWhichNotEqualMe(self.enemyTeam, self.radius):
                self.MagicPattern(target, ctx, SRC.DEATH, mana=1, multCoef=0.5, evadeCoef=1.25, specialReport=Template(f'Ядовитое облако настигает и {target}, нанося $dmg урона.'))
        return result

    def secondAction(self, other: root.HeroInstance, ctx):
        if other != self and not other.isLichSummon: # избыточно, но показательно
            send(ctx, 'Выбранная цель не является призывной нежитью архилича.')
            return -1
        if not self.spend_mana(3, ctx): return -1
        if other == self: # Если действие вызывается с постфиксом себя же самого, то создаётся новая нежить.
            if not self.createSummon(Zombie, ctx): return -1
            newSummon = self.summons[-1]
            newSummon.isLichSummon = True
            send(ctx, 'Архилич призывает на поле боя зомби - низшая нежить, чьи болезненные укусы могут ударить по вашей психике.')
            return 1
        if other.grade >= 0:
            send(ctx, f'Темная энергия усиливает {other} и подготавливает его к новой ступени развития...')
            other.grade += 1

        if other.grade == 3: # (было 3)
            ratio = min(1, other.health / other.max_hp + 0.2)
            if not self.createSummon(SkeletonChampion, ctx, definedPosition=other.position, instantSummonExchange=1): return -1
            send(ctx, 'Зомби превращается в грозного скелета-чемпиона, которые в прошлом были гладиаторами или знаменитыми наемниками.')
            newSummon = self.summons[-1]
            newSummon.isLichSummon = True
            newSummon.health = round(ratio * newSummon.max_hp)
            # newSummon.levelup(max(other.lvl - 3, 0))
            newSummon.grade = other.grade
            other.kill()

        if other.grade == 5: #(было 5)
            ratio = min(1, other.health / other.max_hp + 0.2)
            send(ctx, f'{self}, настало время выбрать финальное развитие вашей нежити: \n [а] Воин-призрак: парализующий клинок, бафф уровней. \n'
                      ' [б] Хуорн: бафф точности и крита, вампиризм. ') # Заменить на храмовника (темплара?)
            for event in longpoll.listen():
                if event.obj['message']['text'].lower() == 'а' and id_checker(self.id, ctx):
                    if not self.createSummon(GhostWarrior, ctx, definedPosition=other.position, instantSummonExchange=1): return -1
                    send(ctx, 'Скелет-чемпион превращается в воина-призрака - одного из офицеров, предавшие своих товарищей в бою, проклятых сражаться до скончания веков.')
                    break
                if event.obj['message']['text'].lower() == 'б' and id_checker(self.id, ctx):
                    if not self.createSummon(EvilTree, ctx, definedPosition=other.position, instantSummonExchange=1): return -1
                    send(ctx, 'Скелет-чемпион поглощается сосудом душ, а из под земли вырывается чёрное сгнившое дерево.')
                    break
            newSummon: root.HeroInstance = self.summons[-1]
            newSummon.health = round(ratio * newSummon.max_hp)
            newSummon.levelup(max(other.lvl - 3, 0))
            # newSummon.addEffect(EFF.STUNNED, 1)
            newSummon.grade = other.grade
            newSummon.isLichSummon = True
            other.kill()

    def thirdAction(self, other: root.HeroInstance, ctx):
        if not self.spend_mana(2, ctx): return -1
        report = ''
        if other.isSummon:
            report += f'Архилич направляет всю энергию на улучшение уже призванного {other}... '
            other.levelup()
            if other.isLichSummon: report += f' И восстанавливает {other.heal(self.lvl*5 + 10)} здоровья путём некромантического ритуала.'
        else:
            report += f'Лич придаёт вампирические свойства оружию {other}.'
            other.addEffect(EFF.VAMPWEAPON, 1 + self.lvl // 7, [0.5+self.lvl/25])
        send(ctx, report)


    def fourthAction(self, other: root.HeroInstance, ctx):
        if not self.spend_mana(3, ctx): return -1
        if self.evade(other, 1, ctx): return 0
        if Chance(80, SRC.MIND).roll(other):
            send(ctx, f'Архилич увлечённо проводит экскурсию по своей кунсткамере. На пятой заспиртованной голове, подозрительно похожей на собственную, {other} с визгом выбегает из помещения.')
            other.addEffect(EFF.FEAR, 2, power=[3])
            other.effects.delEffect(EFF.CONTR)
        else:
            send(ctx, 'Вы смогли собраться с мыслями и не поддаться провокациям лича.')


    def fifthAction(self, other: root.HeroInstance, ctx):
        if self == other:
            send(ctx, f'Самопожертвование, конечно, дело благородное, но сейчас крайне бессмысленное.')
            return -1
        if other.team != self.team: return -1
        manaBoost = round(other.health / 30)
        levelBoost = max(1, round(other.lvl * 0.75))
        self.mana += manaBoost
        self.levelup(levelBoost)
        other.kill()
        send(ctx, f'Лич направляет на {other} филактерий и поглощает его душу. Было восстановлено {manaBoost} маны и получено {levelBoost} уровней.')



    def levelup(self, ind=1):
        if self.hidden_lvl % 5 == 0 and ind > 0:
            self.radius += 1
            self.resists[SRC.FIRE].setWard()
        if vb.stage == 10 and ind > 0: self.max_summons += 1
        self.power += randint(0, 2) * self.lvl // 2 * ind
        self.mana += randint(1, 2) * ind

        super().levelup(ind)

    def protection(self, ctx):
        self.addEffect(EFF.REGENHP, 1, power=[0.5 + self.lvl / 10])
        super().protection(ctx)


    # def how_long(self):
    #     if self.grade == 0 or self.grade > 6:
    #         return ''
    #     if 1 <= self.grade < 3:
    #         return f'Осталось {3 - self.grade} применений(-ие)'
    #     if 3 <= self.grade < 5:
    #         return f'Осталось {5 - self.grade} применений(-ие)'
    #     else:
    #         return ''







