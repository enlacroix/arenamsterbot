from core import root
from datastore.dsources import SRC
from datastore.misc import RACES
from myrandom import Chance
from resists.rstcls import Resist
from resists.rstmanager import ResistManager
from resists.rststates import Ward
import varbank as vb
from vkmodule import send
from utils import countObjectsOfCertainClassInList

class Ectoplasm(root.Hero):

    def __init__(self, _id):
        super().__init__(_id)
        self.race = RACES.ARTIFICIAL
        self.resists = ResistManager({SRC.WEAPON: Resist(0, Ward)})

    def options(self, other):
        opt_report = f'[1]* {{Вода}} Шлепок слизи. \n' + super().options(other)
        return opt_report

    def preChoiceAction(self, other, ctx):
        if self.health == self.max_hp: return 0
        if Chance(65 - countObjectsOfCertainClassInList(vb.teams[self.team], Ectoplasm) * 20):
            newChild = Ectoplasm(self.id)
            send(ctx, f'Коварная эктоплазма размножилась от удара!')
            vb.teams[self.team].append(newChild)

    def firstAction(self, other, ctx):
        return self.MagicPattern(other, ctx, SRC.WATER, 0, meleeFlag=True)




# class CyclopesKing(root.Hero):
#     def __init__(self, _id):  # Страж пивоварни "Черниговское"
#         super().__init__(_id)
#         self.isMercenary = True
#         # self.master.item_skills += '0'  # Обучает Аурам.
#
#     def options(self, other):
#         opt_report = f'[1] 🏹 Метание валуна. Дальний бой, игнорирование половины брони. \n' \
#                      f'[2] Пронзительный взгляд. Снятие охраны вражеского саммона. \n' \
#                      f'[3] Экспериментальная терапия. Восстановить себе {50 + self.lvl * 2} здоровья. \n' \
#                      + super().options(other)
#         return opt_report
#
#     def firstAction(self, other, ctx, kind=0):
#         if self.evade(other, 1, ctx):
#             return 0
#         damage = round((max(1, self.dmg - other.arm * 0.5 + randint(1, 5))) * mf.modtype(other, 0, ctx))
#         sol = self.luck(ctx, other)
#         if sol == -1:
#             return 0
#         other.health -= round(damage * sol)
#         if sol > 1:
#             crit_report = '[Критический удар!] ' + message_bank(self.cls, round(damage * sol), other.health)
#             send(ctx, crit_report)
#         else:
#             send(ctx, message_bank(self.cls, damage, other.health))
#         return round(damage * sol)
#
#     def secondAction(self, other, ctx):
#         try:
#             other.summons.guard = False
#             send(ctx, f'{other.summons.cls_name} не в силах держать оборону перед взором единственного глаза циклопа. Охрана снята - путь свободен.')
#             return 1
#         except AttributeError:
#             send(ctx, 'Это замечательно, но саммона у противника-то нет.')
#             return -1
#
#     def fourthAction(self, other, ctx):
#         send(ctx, f'Циклоп откупорил бутылку своего любимого пива "Черниговское". А вкус еще приятнее, чем запах! Он восстановил {self.heal(50 + self.lvl * 2)} здоровья.')
#
#     def levelup(self, ind=1):
#         self.lvl += ind
#         self.dmg += 3 * ind
#         self.crit += 2 * ind
#
#
# class Gargoyle(root.Hero):
#     def __init__(self, _id):
#         super().__init__(_id)
#         self.race = RACES.DEMON
#
#     def options(self, other):
#         opt_report = f'[1] Град осколков. Ближний бой, источник: Порядок. \n ' \
#                      f'[2] Послание Маврезена. Массовое Замедление (100%) и Ослабление с шансом {12 * self.lvl}% \n' \
#                      + super().options(other)
#         return opt_report
#
#     def firstAction(self, other, ctx, kind=0):
#         return root.Hero.firstAction(self, other, ctx, 4)
#
#     def secondAction(self, other, ctx):
#         report = 'Горгулья испускает жуткий утробный рёв, который чуть не разорвал ваши барабанные перепонки. Вы чувствуете сильное головокружение. \n'
#         for enemy in vb.teams[(self.team + 1) % 2]:
#             add_effect(other, '-slow', 1)
#             report += f'{enemy.cls_name} был замедлен... '
#             if mf.chance(12 * self.lvl):
#                 add_effect(enemy, '-weakness', 2 + self.lvl // 5)
#                 report += 'и ослаблен!'
#             report += '\n'
#         send(ctx, report)
#
#     def levelup(self, ind=1):
#         self.lvl += ind
#         self.dmg += 3
#         add_effect(self, 'contr', 2)

# class WiseTree(root.Hero):
#     def __init__(self, master):
#         alias = 'дуб'
#         super().__init__(master, alias)
#         self.race = RACES.DEMON
#         self.spikes = 1
#
#     def options(self, other):
#         opt_report = f'[1] Лесное лечение: +броня на {self.lvl * 4 + 10} пт. \n ' \
#                      f'[2] Поделиться мудростью: +{self.lvl//5} уровней и +5% торговли \n ' \
#                      f'[3] Опутывание корнями: обездвижить, осталось {self.spikes} применений \n ' \
#                      f'[4] Сила земли: временное увеличение сопротивлений к стихиям \n ' \
#                      + super().options(other)
#         return opt_report
#
#     def firstAction(self, other, ctx, kind=0):
#         send(ctx, f'Дерево восстановило {self.master.heal(randint(30, 65))} здоровья и укрепило вашу броню на {self.lvl * 4 + 10}')
#         self.master.arm += self.lvl * 4 + 10
#
#     def secondAction(self, other, ctx):
#         self.master.levelup(self.lvl//5)
#         self.master.merchant += 0.05
#         send(ctx, f'Дерево даёт парочку уроков нашему герою, поднимая его уровни и обучая его параллельно рыночной теории.')
#
#     def fourthAction(self, other, ctx):
#         if self.spikes > 0:
#             other.stun += 1
#             self.spikes -= 1
#             send(ctx, f'Древо опутывает ветвями {other}, не оставляя ему шанса на побег')
#         else:
#             send(ctx, f'Недостаточно силы в тебе вижу я.')
#             return -1
#
#     def fifthAction(self, other, ctx):
#         send(ctx, 'Дерево временно усиливает ваше сопротивление к стихиям.')
#         add_effect(self.master, '+protection', 2)

















