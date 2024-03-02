"""
Повзрослевший Ученик чародея. Другое название - Демиург, Белый маг
- Воздушный щит: Дать всем на ряду временную 50% защиту от стрел.
- Философский камень. (напоминаю: это генерация предметов. отнять у Алхимика тогда?)
Тогда Алхимика можно переименовать красиво в Травницу и добавить ей действия вида +(50+5%*уровень)% Силы на 1 раунд либо (25%) на 2+k раундов (можно кастовать на нескольких)
- Массовая атака + разбитие брони (аля тиург). Другое предложение todo шрапнель (Земля), магия Касание - удар по колонне и разбитие брони.
"""
from random import randint
from string import Template
from datastore.deffect import EFF
from datastore.dsources import SRC
from datastore.misc import RACES
from ditems.itemcls import Item
from myrandom import Chance
from resists.rstcls import Resist
from resists.rstmanager import ResistManager
from resists.rststates import Immunity, Ward
from core.root import Hero, HeroInstance
from copy import deepcopy
import varbank as vb
from summon_classes.another import Ectoplasm
from vkmodule import send


class Demiurge(Hero):
    def __init__(self, _id):
        super().__init__(_id)
        self.race = RACES.MYST
        self.resists = ResistManager({SRC.IMITATION: Resist(0, Immunity), SRC.AIR: Resist(20), SRC.POLYMORPH: Resist(0, Ward)})

    def options(self, other):
        opt_report = f'[1]* {{Воздух}} Цепная молния (+поражает 2 случайные цели, но урон ополовинивается), 3 МР. \n ' \
                     f'[2]** Клоны. К отряду присоединяется фантомная копия союзника/врага, 5 МР \n' \
                     f'[3] Помрачение рассудка, {Chance(85, SRC.MIND).show(other)}. Цель использует [1] действие на случ союзника, 2 МР\n' \
                     f'[4] Призыв Эктоплазмы. Вард от оружия, размножается от ударов. \n' \
                     f'[5] Философский камень. Создать случайный предмет, 3 МР, {8*self.lvl}% сохранить ход \n' + super().options(other)
        return opt_report

    def preChoiceAction(self, other, ctx):
        x = self.getRandomUnitsFromTeamWhichNotEqualMe(self.team, 1)
        if len(x) > 0 and Chance(50): x[0].addEffect(EFF.AIRSHIELD, 2, power=[50])

    def firstAction(self, other, ctx):
        if self.position != 0: return -1
        result = self.MagicPattern(other, ctx, SRC.AIR, mana=3)
        if result not in (0, -1):
            for i, target in enumerate(other.getRandomUnitsFromTeamWhichNotEqualMe(self.enemyTeam, 2)):
                self.MagicPattern(target, ctx, SRC.AIR, mana=0, multCoef=0.5**(i+1), evadeCoef=1.25, specialReport=Template(f'Разряд настигает {target}, нанося $dmg урона.'))
        return result
    

    def secondAction(self, other, ctx):
        """
        Копировать своих/чужих?
        """
        if self == other: return -1
        if not self.isAtSecondRow(ctx): return -1
        if not self.spend_mana(5, ctx): return -1
        copiedUnit: HeroInstance = deepcopy(other)
        copiedUnit.health = randint(1, 10)
        copiedUnit.permission_to_summoning = False
        copiedUnit.cls_name = 'Фантом '+ copiedUnit.cls_name
        copiedUnit.position = (other.position + 1) % 2
        copiedUnit.id = self.id
        vb.teams[self.team].append(copiedUnit)
        send(ctx, f'{other} был успешно скопирован.')

    def thirdAction(self, other: HeroInstance, ctx):
        if not self.spend_mana(2, ctx): return -1
        lst = other.getRandomUnitsFromTeamWhichNotEqualMe(other.team, 1)
        if len(lst) > 0: target = lst[0]
        else:
            send(ctx, f'Для {other} нет целей для атаки.')
            return -1
        if Chance(85, SRC.MIND).roll(other):
            send(ctx, f'Демиург полностью подчиняет разум {other} и заставляет его атаковать {target}:')
            other.firstAction(target, ctx)
        else:
            send(ctx, f'Демиургу не удалось подчинить рассудок {other}')
            return 0


    def fourthAction(self, other: HeroInstance, ctx):
        # self.MagicPattern(other, ctx, mana=2, source=SRC.FIRE, multCoef=other.getSRCFactor(SRC.WATER) * other.getSRCFactor(SRC.AIR) * other.getSRCFactor(SRC.EARTH), specialReport=Template(f'Сфера четырёх стихий наносит $dmg урона'))
        if self.createSummon(Ectoplasm, ctx):
            send(ctx, 'Маг Порядка кидает склянку с агар-агаром в центр поля. Добавив кипятка, он наделяет желейную массу разумом, причём агрессивным.')
        else:
            return -1


    def fifthAction(self, other, ctx):
        if not self.spend_mana(3, ctx): return -1
        genItem = Item.createRandItemsByTier(infimum=1 + self.lvl // 5, supremum=2 + self.lvl // 3)[0]
        send(ctx, f'Демиург создает {genItem}!')
        self.inv.addItem(genItem)
        if Chance(8*self.lvl):
            send(ctx, 'Благодаря своей сноровке демиург может сделать дополнительный ход.')
            return -1
        

    def levelup(self, ind=1):
        super().levelup(ind)
        self.power += 2 * ind
        self.mana += randint(0, 3) * max(ind, 0)
        self.arm += 2 * ind
        #self.auto_perks(2) - быстрый набор перков на вещи как фишка?
