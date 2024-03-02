from functools import reduce
from datastore.deffect import EFF
from datastore.dperks import PRK
from datastore.dsources import SRC
from datastore.misc import RACES
from ditems.inventory import Inventory
from ditems.itemcls import Item
from myrandom import Chance
from settings import health_bonus, GOLD_BONUS, MAX_TEAM_SIZE, MAX_ROW_SIZE
from effects.effmanager import EffectManager
from resists.rstmanager import ResistManager
from vkmodule import send, get_first_name, longpoll, id_checker
from background import stats_dict, enumOfStatsDict, COMBAT_MESSAGES, DEFEND_OPTIONS
from utils import hide_morale, isMemberOfClass
from random import randint, sample
import varbank as vb
from typing import Self, TypeVar, Type, Iterable
from string import Template

HeroInstance = TypeVar("HeroInstance", bound="Hero")

class Hero:
    size = 1 # "Размер" персонажа в клетках игрового поля.

    def __init__(self, user_id: int):
        self.cls_name, self.health, self.dmg, self.arm, self.ini, self.dodge, self.crit, self.morale, \
        self.mana, self.power, self.gold, self.acc = stats_dict[self.__class__.__name__]
        #self.cls: int = enumOfStatsDict[self.__class__.__name__]
        self.health = round(self.health * health_bonus)
        self.name = get_first_name(user_id)
        # self.gold = round(self.gold * gold_bonus)
        self.lvl = 1
        self.race = RACES.HUMAN
        self.summons: list = []
        # self.stun = 0
        # self.sleeping = 0
        self.inv = Inventory(self)
        self.resists = ResistManager() # todo выставляется вручную каждым классом
        self.skills: list[PRK] = [PRK.MISC] # todo выставляется вручную каждым классом
        self.master = None
        self.isSummon = False
        self.illness = False
        self.effects = EffectManager(self)
        self.max_hp = self.health  # Чтобы контролировать оверхилл. В лвлапе можно прописать, что макс_НР тоже увеличивается.
        self.id = user_id
        self.memory = [self.__class__, 0, self.id]  # Последняя ячейка под броню превращённого беса todo класс Memorizer
        self.merchant = 0
        self.hidden_lvl = 1  # Ведьмочка понижениями уровня способна вызвать повторное получение перка.
        self.lives = 0
        self.crit_mf = 0
        self.crit_resist = 0
        self.crit_bank = 0
        self.dodge_bank = 0
        self.modificators = []
        self.permission_to_summoning = True
        self.develop = 6
        self.armor_penetration = 0
        self.heal_rate = 1
        self.was_effected = False
        self.not_waited = True
        self.bonusAction = False
        self.isMercenary = False
        self.previousHealth = self.health
        self.position = 0 # 0 - передний ряд, 1 - задний ряд.
        self.max_summons = 1 # Какое максимальное количество саммонов может контролировать один герой.
        self.isLichSummon = False
        self.isForbiddenToResurrect = False
        self.grade = 0
        self.ulta = 0 # Суперспособность (индивидуальная для всех)
        self.otherUlta = 0
        self.gun = 0 # Для ведьмочки и детектива.
        self.lengthOfWeapon = 1

    def __str__(self):
        return f'{self.cls_name} {self.name}' if not self.isSummon else f'{self.cls_name} ({self.getMaster().name})'

    def getSRCFactor(self, source: SRC):
        return self.resists[source].getMultiplier()

    # @property
    # def cls_name(self):
    #     return stats_dict[self.__class__.__name__].nm

    @property
    def team(self):
        if self in vb.teams[0]: return 0
        if self in vb.teams[1]: return 1
        print(f'Команда не определена для {self}')
        return

    def cumulativeModificator(self, other):
        # Допустим, взял перк (чем больше трупов, тем выше урон), урон по конкретной расе. Тогда будет произведен перерасчёт.
        res = 1
        if self.hasPerk(PRK.DARK_CREATURES_SLAYER) and other.race in (RACES.UNDEAD, RACES.DEMON): res *= 1.2
        if self.hasPerk(PRK.NONHUMAN_SLAYER) and other.race == RACES.NONHUMAN: res *= 1.2
        # продолжение следует
        return res


    def __getattribute__(self, item):
        if item == 'inv': return vb.Team.Entry(self.team).getTeamInventory(self)
        if item == 'gold': return vb.Team.Entry(self.team).gold
        return object.__getattribute__(self, item)

    def startInventory(self):
        pass

    @property
    def enemyTeam(self):
        return (self.team + 1) % 2

    def teamIndex(self):
        return vb.teams[self.team].index(self) + 1

    def alive(self): return self.health > 0

    def calcSRCFactor(self, source: SRC):
        return self.resists[source].calcMultiplier()

    def getMaster(self):
        if self.master is None: return self
        return self.master

    def getOwnRow(self, ally=True) -> Iterable[HeroInstance]:
        return filter(lambda x: x.position == self.position, vb.teams[self.team if ally else self.enemyTeam])

    def getRow(self, row_num: int, ally=True) -> tuple:
        return tuple(filter(lambda x: x.position == row_num, vb.teams[self.team if ally else self.enemyTeam]))

    def getOwnColumn(self, ally=True) -> Iterable[HeroInstance]:
        return filter(lambda x: x.column == self.column, vb.teams[self.team if ally else self.enemyTeam])

    def getNeighbourOnMyColumn(self, ally=True) -> HeroInstance | None:
        return next(filter(lambda x: x != self, self.getOwnColumn(ally)), None)

    def preChoiceAction(self, other, ctx):
        pass

    def addGold(self, amount): vb.Team.Entry(self.team).gold += amount

    def normalize(self):
        self.dmg = max(0, self.dmg)
        self.power = max(0, self.power)
        # self.arm = max(-30, self.arm)
        self.lvl = max(0, self.lvl)
        self.dodge = min(45, self.dodge)
        self.crit = min(60, self.crit)
        self.morale = min(65, self.morale)

    def addEffect(self, identifier: EFF, rounds: int, power: list = None):
        return self.effects.addEffect(identifier, rounds, power)

    def heal(self, amount):
        x = max(min(self.max_hp - self.health, round(amount * self.heal_rate)), 0)
        self.health += x
        return x

    def transformToAnotherClass(self, newClass: Type[Self]):
        self.__class__ = newClass
        self.cls_name = stats_dict[self.__class__.__name__].nm

    def hasMaster(self, concreteClassTuple: tuple[str, ...] | None = None) -> bool:
        """
        :param concreteClassTuple: можно передать конкретный класс, чтобы проверить принадлежность мастера к этому классу, e.g. - архилич.
        :return: есть ли хозяин у саммона или он сам по себе.
        """
        if self.master is None: return False
        if concreteClassTuple is not None: return isMemberOfClass(self.master, concreteClassTuple)
        return True

    def hasPerk(self, perk: PRK):
        return perk in self.skills

    def destroyArmor(self, amount, cap=0):
        x = round(min(amount, self.arm - cap) * self.getSRCFactor(SRC.DESTROYARMOR))
        self.arm -= x
        return x

    def isAtSecondRow(self, ctx) -> bool:
        # атаки помеченные двумя звездами.
        if self.position == 0:
            send(ctx, 'Данное действие требует особой концентрации и невозможно к выполнению на первом ряду.')
            return False
        return True

    @property
    def column(self):
        return list(self.getOwnRow()).index(self)

    def checkStun(self, event):
        if self.hasEffect(EFF.STUNNED):
            send(event, f'{self} пропускает ход! ')
            self.effects.getEffect(EFF.STUNNED).rounds -= 1
            vb.done.append(self)
            return True
        return False

    def stunMyself(self, probability: Chance, num=1):
        """
        :param probability: Chance c двумя источниками: исходный / стан. Разум / стан.
        :param num: на сколько раундов станим.
        Обеспечивает контроль над всеми станами в игре.
        n - на сколько раундов висит стан резист.
        """
        probability.addExtraSRC(SRC.STUN)
        if probability.roll(self):
            # Почему минус? Поскольку STUNNED эффект отрицательный, то для его дельты, вы домножаете на -1.
            self.addEffect(EFF.STUNNED, num)
            self.addEffect(EFF.STUNRESIST, num + 2, power=[100])
            return 1
        return 0


    def kill(self):
        self.health = -999
        self.resists[SRC.FINALSTRIKE].setDefault()
        self.resists[SRC.FINALSTRIKE].changeValue(-100)
        self.lives = -1
        # if self.isSummon: self.master.summons.remove(self)
        # vb.teams[self.team].remove(self)
        # Нужно убить еще саммонов, которые принадлежат цели этой команды. - дублирование кода с death.

    def update(self):
        self.not_waited = True
        self.was_effected = False

    def psycho(self, ctx):
        """
        Отслеживание психического состояния игрока
        """
        if self.race in (RACES.UNDEAD, RACES.ARTIFICIAL):
            return 0
        if self.morale > -70:
            return 0
        if self.morale < -100:
            send(ctx, f'Вы не выдерживаете последней психологической атаки, и вас настигает сердечный приступ, который ставит точку в этой истории.'
                      f' Покойтесь с миром.')
            self.kill()
            return 0
        if self.illness:  # Если ты уже заболел, то вторую болезнь не накинут.
            return 0
        fate = randint(1, 6)
        self.addMentalIllness(fate, ctx)
        self.illness = True

    def wait(self, ctx):
        if self.not_waited and self not in vb.delayed:
            vb.delayed.append(self)
            send(ctx, f'{self.cls_name} {self.name}(-а) медлит и ждёт лучшего момента.')
            self.not_waited = False
            return 0
        else:
            send(ctx, f'{self.name}, вы уже ждали в этом раунде! Настало время решительных действий.')
            return -1

    def contr_attack(self, other, ctx):
        if other.hasEffect(EFF.CONTR) and other.health > 0 and not other.hasEffect(EFF.STUNNED):
            other.effects[EFF.CONTR].rounds -= 1
            contr_dmg = round(other.dmg * 0.75) + other.lvl
            self.health -= contr_dmg
            send(ctx, f'👀 Противник проводит ответную контратаку и наносит вам {contr_dmg} урона!')

        if other.hasEffect(EFF.FIRESHIELD): # можно убиться и об огненный щит трупа
            other.effects[EFF.FIRESHIELD].rounds -= 1
            self.arm -= other.lvl
            send(ctx, f'💥 Огненный щит обжигает вас на {self.harmWithSRC(SRC.FIRE, self.dmg * 0.6 + other.lvl)} и разрушает доспехи на {other.lvl} пт.')



    def evade(self, other, mod: int, ctx):
        """
        :param other:
        :param mod: целочисленный модификатор, изменяющий точность.
        Если он отрицательный, то попасть по цели легче.
        :param ctx:
        :return:
        """
        if other.dodge_bank >= 1:
            other.dodge_bank -= 1
            send(ctx, f'👏 {other.cls_name} мастерски уклоняется от атаки {self.cls_name}!')
            return 1
        if Chance(other.dodge + mod + 95 - self.acc):
            send(ctx, f'👏 {self.cls_name} промахивается по {other.cls_name}! Шанс на это был равен: {other.dodge + mod + 95 - self.acc}%.')
            return 1
        else:
            return 0

    def describe(self) -> str:
        return f'{self.cls_name}({self.ini}): [{"I"*(self.team + 1)}, {self.teamIndex()}]{"⛔" if self.hasEffect(EFF.STUNNED) else ""}'


    def show_stats(self, inv: bool, effects: bool, resists: bool, perks: bool) -> str:
        """
        \nМф крита: х{round(2 + (self.acc / 100 - 1) * 1.4 + self.crit_mf, 2)} Пробитие брони: {self.armor_penetration*100}% ' \
         f'Мф лечения: х{self.heal_rate} \n Мф резиста к критам: x{self.crit_resist}
        """
        show_report = f'{self.teamIndex()}. {self}, уровень {self.lvl} ({self.position + 1} ряд, {self.column + 1} клн, {"I"*(self.team + 1)})\n' \
                      f' ✙ {self.health} / {self.max_hp} 🗡 {self.dmg} 🔰 {self.arm} 🔮 {self.power} ⌛ {self.ini} 🎯 {self.acc} \n ☘ {self.crit} ' \
                      f'⚗ {self.mana} 💨 {self.dodge} 🎷 {hide_morale(self.morale)} 💔 {round(self.lives, 2)} \n'
        if inv:
            show_report += f'\n {self.inv}'
        if effects:
            show_report += f'Эффекты: {self.effects} \n '
        if perks:
            show_report += 'ПЕРКИ: ' + ', '.join((skill.value[0] for skill in self.skills)) + f'\n Пробитие брони: {self.armor_penetration*100}% Банк критов: {self.crit_bank} Банк уклонений: {self.dodge_bank} ' \
            f'Тип: {self.race.value}. Запрещ воскр: {"Да" if self.isForbiddenToResurrect else "Нет"}. Макс саммонов: {self.max_summons}. Золото: {self.gold} \n'
            if self.isSummon: show_report += f'Хозяин: {self.master} c номером {self.master.teamIndex()}. Исчезнет после смерти: {"Нет" if self.isMercenary else "Да("}. \n'
            else: show_report += f'Саммоны: {", ".join([str(unit) + " №" + str(unit.teamIndex()) for unit in self.summons])} \n'
        if resists:
            show_report += f'СОПРОТИВЛЕНИЯ: {self.resists}'
        return show_report + '\n'

    def getRandomUnitsFromTeamWhichNotEqualMe(self, team: int, amount: int) -> list[HeroInstance]:
        seq = list(filter(lambda x: x != self, vb.teams[team]))
        if 0 < amount <= len(seq): return sample(seq, amount)
        return seq

    def RandomUnitsFromMyTeam(self, amount: int) -> list[HeroInstance]:
        if 0 < amount <= len(vb.teams[self.team]): return sample(vb.teams[self.team], amount)
        else: return vb.teams[self.team]


    def luck(self, ctx, other, mod=1):
        if self.crit >= 0:
            mfd = max(1, 2 + (self.acc / 100 - 1) * 1.4 + self.crit_mf - other.crit_resist)
            if self.crit_bank >= 1:
                self.crit_bank -= 1
                return mfd
            if Chance(self.crit * mod):
                self.morale += 5
                return mfd
            else:
                return 1
        if self.crit < 0 and Chance(abs(self.crit)):
            calcDamage = lambda target: self.magicDamage(other=target, source=SRC.DEFAULT) if self.power > self.dmg else self.phys_damage(other=target)

            # Проклятье! Кажется Вам выпала 1 на d6, поскольку вместо врага вы нанесли {max(0, self.dmg - self.arm)} урона по себе. Понимаемо...
            self.morale -= 5
            report = f'[Критический провал!] Потеряно 5 единиц боевого духа. '
            punishment = randint(0, 2)
            match punishment:
                case 0:
                    pass
                case 1:
                    report += f'Более того, вы ударили себя на {calcDamage(self)} урона... Понимаемо.'
                    self.health -= calcDamage(self)
                case 2:
                    pityAlly = self.getRandomUnitsFromTeamWhichNotEqualMe(self.team, 1)
                    if len(pityAlly) == 0:
                        send(ctx, report)
                        return -1
                    pityAlly = pityAlly[0]
                    report += f'Более того, вместо противника ваша атака достаётся несчастному {pityAlly}, который получил от вас {calcDamage(pityAlly)}. Нехорошо.'
                    pityAlly.health -= calcDamage(pityAlly)
            send(ctx, report)
            return -1
        return 1

    def enchanted_weapon(self, other, ctx, damage=0):
        for key in self.effects.pool:
            match key.identifier:
                case EFF.VAMPWEAPON:
                    send(ctx, f'Чары, наложенные на оружие, восстановили вам {self.heal(damage * self.effects.getEffect(EFF.VAMPWEAPON).power[0])} здоровья.')
                case EFF.FIREDWEAPON:
                    send(ctx, f'Зачарованное пламя дополнительно наносит {other.harmWithSRC(SRC.FIRE, (self.power // 4 + 6))} ущерба.')
                case EFF.POISONEDWEAPON:
                    send(ctx, f'Яд просачивается в кровь {other}!')
                    other.addEffect(EFF.POISON, randint(1, 2), power=[1.2])
                case EFF.BREAKWEAPON:
                    send(ctx, f'Руны уничтожают доспех на {other.destroyArmor(10+self.lvl, 0)} пунктов.')
                case _:
                    continue

        # if kind != 0:
        #     return 0
        # for key in self.effects.pool:
        #     if key == '+firedweapon':
        #         dmg = round( * modtype(other, 3, ctx))
        #
        #         other.health -= dmg
        #     if key == '+poisonedweapon':
        #         # Может быть добавить шанс, но сделать помощнее? ОНА И ТАК МОЩНАЯ, БРАТАН - НЕ НАДО!!!1
        #         add_effect(other, '-poison', 2 + self.lvl // 5)
        #         send(ctx, f'Яд просачивается в вашу кровь...')
        #     if key == '+breakarmor':
        #         send(ctx, f'Сила гномьих рун дополнительно разбила броню {other.cls_name} на {self.destroy_armor(other, self.lvl*2 + 12, 0)} единиц.')
        #     if key == '+thunder':
        #         dmg = round((self.power // 5 + self.lvl * 2 + 15) * modtype(other, 4, ctx))
        #         send(ctx, f'Молнии, окутывающие оружие, наносят дополнительные {dmg} урона.')
        #         other.health -= dmg
        #         if chance(15 + self.lvl // 2):
        #             other.stun += 1
        #             send(ctx, f'Электрический разряд оглушил противника на 1 раунд.')
        #     if key == '+vampire':
        #
        #     else:
        #         continue

    def phys_damage(self, other, cf=1):
        return round(max(1, self.dmg - other.arm * (1 - self.armor_penetration) + randint(0, 3)) * other.getSRCFactor(SRC.WEAPON) * cf)

    def magicDamage(self, other, source, multCoef=1, addComp=0):
        return max(1, round(self.power * other.getSRCFactor(source) * multCoef + addComp + randint(-5, 5)))

    def harmWithSRC(self, source: SRC, damage):
        value = round(damage * self.getSRCFactor(source))
        self.health -= value
        return value

    def IsGuarded(self, ctx) -> bool:
        if self.hasEffect(EFF.GUARDED):
            send(ctx, f'{self} находится под охраной, его невозможно выбрать как цель данной атаки.')
            return True
        return False

    def isReachableForMelee(self, other, ctx) -> bool:
        """
        Достижима ли цель.
        1. Атака ближнего боя не может быть произведена из заднего ряда, когда на переднем ряду твоей команды кто-то есть.
        2. Атака ближнего боя не может достать дальний ряд, если на переднем ряду противника кто-то есть.
        """
        if abs(self.column - other.column) > self.lengthOfWeapon:
            X, Y = max(self.column, other.column), min(self.column, other.column)
            possibleColumns = list(range(Y, X + 1))
            possibleColumns.remove(other.column)
            if any([True for unit in vb.teams[other.team] if unit.position == 0 and unit.column in possibleColumns]):
                send(ctx, f'Вы не можете достать оружием до {other}: он слишком далеко от вас.')
                return False
        if self.position == 1 and any([True for unit in vb.teams[self.team] if unit.position == 0]):
            send(ctx, 'Вы не можете провести данную атаку с заднего ряда, когда кто-то есть на переднем ряду вашей команды.')
            return False
        if other.position == 1 and any([True for unit in vb.teams[self.enemyTeam] if unit.position == 0]):
            send(ctx, 'Атака ближнего боя не может достать задний ряд, если на переднем ряду противника кто-то есть.')
            return False
        return True

    def spend_mana(self, amount: int | float, ctx) -> bool:
        if amount == -1: return True
        if self.hasEffect(EFF.SILENCE):
            send(ctx, f'На вас наложено проклятье Безмолвия: ни один маг не сможет произнести свои отвратительные заклятья. Ты в муте.')
            return False
        if self.mana >= amount:
            self.mana -= amount
            if self.hasEffect(EFF.MAGIC_SHACKLES):
                self.health -= amount * (10 + self.lvl // 4)
                send(ctx, f'Магические оковы обжигают вас на {amount * (10 + self.lvl // 4)}, наказывая вас за применение магии!')
            return True
        else:
            send(ctx, f'У вас недостаточно магической энергии для совершения данного действия: необходимо {amount}, а у вас {self.mana}.')
            return False

    def firstAction(self, other: HeroInstance, ctx):
        return self.MeleePattern(other, ctx)

    def allyActionForEnemy(self, other, ctx) -> bool:
        if self.team != other.team:
            send(ctx, 'Не стоит применять данное действие на своего противника.')
            return True
        return False


    def MeleePattern(self, other: HeroInstance, ctx, source=SRC.WEAPON, evadeCoef=1, critCoef=1, multCoef=1, addComp=0, ignoreMelee=False, armorIgnore=1, specialReport: Template = None, ignoreContr=False, ignoreGuard=False):
        if not ignoreGuard and other.IsGuarded(ctx): return -1
        if not ignoreMelee and not self.isReachableForMelee(other, ctx): return -1
        if self.evade(other, evadeCoef, ctx): return 0
        critMult = self.luck(ctx, other, mod=critCoef)
        if critMult == -1: return 0
        crit_piercing = 0.5 if critMult > 1 else 0
        damage = max(1, round((self.dmg - other.arm * (1 - self.armor_penetration - crit_piercing) * armorIgnore + randint(0, 2)) * other.getSRCFactor(source) *
                              critMult * multCoef * self.cumulativeModificator(other) + addComp))
        other.health -= damage
        if specialReport is None:  report = COMBAT_MESSAGES.get(self.__class__.__name__, Template('Нанесено $dmg урона, у $enemy осталось $hp ОЗ.')).substitute(dmg=str(damage), hp=str(other.health),                                                                                                                                   enemy=str(other))
        else: report = specialReport.substitute(dmg=str(damage))
        if critMult > 1: report = '[Критический удар!] ' + report
        send(ctx, report)
        self.enchanted_weapon(other, ctx, damage)
        if not ignoreContr: self.contr_attack(other, ctx)
        return damage

    def MagicPattern(self, other: HeroInstance, ctx, source: SRC, mana, evadeCoef=1, critCoef=1, meleeFlag=False, multCoef=1, addComp=0, specialReport: Template = None, ignoreGuard=False):
        # meleeFlag - если магия типа Касание, то она должна быть подвержена эффектам ближнего боя.
        if not ignoreGuard and other.IsGuarded(ctx): return -1
        if meleeFlag and not self.isReachableForMelee(other, ctx): return -1
        if not self.spend_mana(mana, ctx): return -1
        if self.evade(other, evadeCoef, ctx): return 0
        critMult = self.luck(ctx, other, critCoef)
        if critMult == -1: return 0
        damage = max(1, round(self.power * other.getSRCFactor(source) * critMult * multCoef + addComp + randint(-5, 5)))
        other.health -= damage
        if specialReport is None:
            report = COMBAT_MESSAGES.get(self.__class__.__name__, Template('Нанесено $dmg урона, у $enemy осталось $hp ОЗ.')).substitute(dmg=str(damage), hp=str(other.health),                                                                                                                                enemy=str(other))
        else:
            report = specialReport.substitute(dmg=str(damage))
        if critMult > 1: report = '[Критический удар!] ' + report
        send(ctx, report)
        #if meleeFlag: self.contr_attack(other, ctx)
        return damage

    def ArcherPattern(self, other: HeroInstance, ctx, source: SRC = SRC.WEAPON, evadeCoef=1, critCoef=1, multCoef=1, addComp=0, armorIgnore=1, specialReport: Template = None, ignoreGuard=False):
        if not ignoreGuard and other.IsGuarded(ctx): return -1
        if self.evade(other, evadeCoef, ctx): return 0
        critMult = self.luck(ctx, other, critCoef)
        if critMult == -1: return 0
        crit_piercing = 0.25 if critMult > 1 else 0
        damage = max(1, round((self.dmg - other.arm * (1 - self.armor_penetration - crit_piercing) * armorIgnore) * other.getSRCFactor(source) *
                              critMult * multCoef + addComp))
        other.health -= damage
        if specialReport is None:
            report = COMBAT_MESSAGES.get(self.__class__.__name__, Template('Нанесено $dmg урона, у $enemy осталось $hp ОЗ.')).substitute(dmg=str(damage), hp=str(other.health), enemy=str(other))
        else:
            report = specialReport.substitute(dmg=str(damage))
        if critMult > 1: report = '[Критический удар!] ' + report
        send(ctx, report)
        return damage

    def MassPattern(self):
        pass

    def options(self, other):  # [справка] По интерфейсу. todo сменить защиту на [d], вейт на [w], мув на [m], инвентарь на [i], использовать на [u], отдать на [g]
        return f'[d] Защититься ({DEFEND_OPTIONS.get(self.__class__.__name__, "")}). [w] Подождать. [m] Сменить ряд. \n[i]/[u k] Инвентарь/Исп предмет k. [ti] Состав команды i. \n[s P] Отчёт по юниту P. [f] Расстановка. [s] Очерёдность.'

    def levelup(self, ind=1):
        self.lvl += ind
        self.hidden_lvl = self.hidden_lvl + ind if ind > 0 else self.hidden_lvl
        # Избыточно, поскольку левел ап происходит для каждого члена команды.
        # if self.summons and ind == 1: # Нормальный случай лвлапа.
        #     for summ in self.summons: summ.levelup()


    def protection(self, ctx):
        self.resists.changeSeveralResists((SRC.WEAPON, SRC.FIRE, SRC.WATER, SRC.AIR, SRC.EARTH, SRC.DEATH, SRC.MIND), 50)
        self.addEffect(EFF.DEFEND, 1)
        send(ctx, f'{self.cls_name} встаёт в защитную стойку.')

    def death(self, ctx) -> bool:
        """

        """
        if self.health > 0: return False
        if self.resurrect(ctx): return False  # если воскрес, то останови процесс.
        if not Chance(100, SRC.FINALSTRIKE).roll(self):
            self.health = 1
            send(ctx, f'{self} на Пороге смерти, но сумел пережить эту атаку!')
            self.resists[SRC.FINALSTRIKE].changeValue(-25)
            return False
        if self.isSummon:
            self.master.summons.remove(self)
        if not self.isSummon: # Уничтожить саммонов. Саммоны не попадают на кладбище, а наемники - да.
            vb.Team.Entry(self.team).graveyard.append(self)
            for summon in filter(lambda x: not x.isMercenary, self.summons):
                summon.kill()
        vb.teams[self.team].remove(self)
        send(ctx, f'{self} погибает...')
        return True

    def movement(self):
        if self.hasEffect(EFF.CHAINED): return False
        if len(self.getRow((self.position + 1) % 2)) >= MAX_ROW_SIZE: return False
        self.position = (self.position + 1) % 2
        return True

    def getSizeOfMyTeam(self):
        return reduce(lambda a, x: a + x.size, vb.teams[self.team], 0)

    def createSummon(self, summonCls: Type[Self], ctx, definedPosition: int | None=None, instantSummonExchange=0) -> bool:
        """
        1. Если параметр max_summon был превышен, то происходит замена текущего саммона.
        definedPosition - место для саммона предопределено, не нужно спрашивать куда его поставить.
        """
        if not self.permission_to_summoning:
            send(ctx, f'Призванное существо не способно на вызов себе подобных.')
            return False
        if self.getSizeOfMyTeam() + summonCls.size - instantSummonExchange > MAX_TEAM_SIZE:
            send(ctx, f'В вашем отряде нет места для данного существа.')
            return False

        S: HeroInstance = summonCls(self.id).turnToSummon(master=self)
        S.position = -1 # todo Здесь создаётся саммон, где у него по умолчанию стоит ряд = 0!
        # Когда вызываешь нового саммона, а мест нет, то удаляется первый из списка.
        if len(self.summons) == self.max_summons:
            target = self.summons.pop(0)
            send(ctx, f'{target} исчезает, так как вы не можете поддерживать столько существ под своим началом...')
            vb.teams[self.team].remove(target)

        self.summons.append(S)
        vb.teams[self.team].append(S)
        if definedPosition is not None:
            S.position = definedPosition
        else:
            send(ctx, 'Выберите на какой ряд вы хотите призвать саммона. [пр | fr] - 1 ряд, [зр | br] - 2 ряд. [отмена] - отменить призыв.')
            for event in longpoll.listen():
                if not id_checker(self.id, event): continue
                try: current = event.obj['message']['text'].lower()
                except: continue
                match current:
                    case 'пр' | 'fr':
                        if len(self.getRow(0)) >= MAX_ROW_SIZE:
                            send(ctx, f'На первом ряду нет места!')
                            continue
                        else:
                            S.position = 0
                            break
                    case 'зр'| 'br':
                        if len(self.getRow(1)) >= MAX_ROW_SIZE:
                            send(ctx, f'На втором ряду нет места!')
                            continue
                        else:
                            S.position = 1
                            break
                    case 'отмена':
                        S.kill()
                        break
                    case _:
                        continue
        if self.hasPerk(PRK.SUMMON_LEVEL_UP): S.levelup(3)
        return True

    def turnToSummon(self, master: HeroInstance):
        self.isSummon = True
        self.master = master
        self.permission_to_summoning = False
        self.isMercenary = False # Кто-то может в конструкторе поставить себе этот параметр истиной.
        return self


    # def auto_perks(self, freq):
    #     if self.lvl % freq != 0:
    #         return 0
    #     knowledge = [n for n in range(0, 10) if str(n) not in self.item_skills]
    #     if len(knowledge) == 0:
    #         return -1
    #     self.item_skills += str(choice(knowledge))

    def resurrect(self, ctx) -> bool:
        if self.health <= 0 and self.lives >= 1:
            self.lives -= 1
            self.health = round(self.max_hp * 0.5)
            self.ini = round(self.ini * 0.5)
            send(ctx, f'Герои не умирают! {self} воскресает c {self.health} ОЗ, чтобы продолжить борьбу, потратив одну жизнь.')
            return True
        return False

    def animate(self, team, coef=0.5):
        if self.isForbiddenToResurrect:
            return False
        self.health = round(self.max_hp * coef)
        self.ini = round(self.ini * 0.5)
        vb.teams[team].append(self)
        return True



    def hasEffect(self, eff: EFF):
        return self.effects.hasEffect(eff)

    def hasSummon(self, ctx):
        if self.summons is None:
            send(ctx, f'Невозможно выполнить данное действие, т.к. у вас отсутствует призванное существо.')
            return False
        return True

    def rewardForHighMorale(self):
        return self.addEffect(EFF.STRENGTH, 2, [0.25])

    def addRandItemsByTier(self, supremum, infimum=1, count=1):
        self.inv.addSeveralItems(Item.createRandItemsByTier(infimum, supremum, count))

    def addMentalIllness(self, fate, ctx):
        match fate:
            case 1:
                send(ctx, 'Охваченный беспричинной паранойей вы убиваете своего саммона, подло закалывая его кинжалом.')
                try:
                    self.summons[0].kill()
                except AttributeError | IndexError:
                    send(ctx,
                         f'Ах да, у вас же даже его нет... От осознания собственного одиночества, вы теряете {self.max_hp // 4} здоровья.')
                    self.health -= self.max_hp // 4
            case 2:
                self.dmg += self.arm // 2
                self.arm = 0
                self.mana = 0
                self.acc -= 20
                send(ctx,
                     f'Последние события полностью уничтожили остатки разума в вас. Теперь вы берсерк, у которого лишь кровавая пелена перед глазами.'
                     f' Ваша точность снижена, мана и броня обнулены, но урон увеличился на {self.arm // 2}.')
            case 3:
                send(ctx,
                     f'Зачем куда-то бежать, прятаться, уклоняться - все равно мы все умрём. Ваше уклонение и положительная удача обнулены.')
                self.dodge = 0
                self.crit = 0 if self.crit > 0 else self.crit
            case 4:
                send(ctx, f'У меня есть две новости - хорошая и плохая. Начнем с хорошей - у вас появился настоящий Друг.'
                          f' Такому другу не жалко отдать все предметы вашего инвентаря и передать содержимое вашего кошеля. Плохая новость - у вас шизофрения, и друг воображаемый.')
                self.gold = 0
                self.inv.clearInventory()
                self.acc -= 15
            case 5:
                send(ctx, 'От переживаний и стресса вы деградировали, потеряв 4 уровня и все навыки владения предметами.')
                self.levelup(-4)
                self.skills.clear()
            case 6:
                send(ctx, f'ДУШЕВНЫЙ ПОДЪЁМ! Ваш боевой дух обнулён, ГЕРОИЧЕСКИЙ {self.name} увеличил атаку и силу магии на 15 пунктов.')
                self.morale = 0
                self.dmg += 15
                self.power += 15
            case _:
                send(ctx, 'Подобной болезни еще не придумали...')

    def secondAction(self, other, ctx):
        pass

    def thirdAction(self, other, ctx):
        pass

    def fourthAction(self, other, ctx):
        pass

    def fifthAction(self, other, ctx):
        pass





class Imp(Hero):

    def options(self, other):
        return f'[1] Месть беса \n Остальные действия заблокированы. \n' + super().options(other)

    def firstAction(self, other, ctx):
        return self.MeleePattern(other, ctx)

    def secondAction(self, other, ctx):
        send(ctx, 'В форме беса вы не способны на это!')
        return -1

    def fifthAction(self, other, ctx):
        send(ctx, 'В форме беса вы не способны на это!')
        return -1

    def fourthAction(self, other, ctx):
        send(ctx, 'В форме беса вы не способны на это!')
        return -1

    def thirdAction(self, other, ctx):
        send(ctx, 'В форме беса вы не способны на это!')
        return -1

