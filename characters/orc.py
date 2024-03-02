from string import Template
from core import root
from random import randint
from datastore.deffect import EFF
from datastore.dperks import PRK
from datastore.dsources import SRC
from datastore.misc import RACES
from ditems.itemcls import Item
from myrandom import Chance
from summon_classes.goblins import GoblinShaman, GoblinTrapper
from utils import getMember
from vkmodule import send, longpoll, id_checker



class OrcKing(root.Hero):
    def __init__(self, pvp_id):
        super().__init__(pvp_id)
        self.cum_rage = 0
        self.max_summons = 1
        self.authority = randint(2, 3)
        self.skills.append(PRK.MILITARY)
        self.race = RACES.NONHUMAN

    def get_rage(self): return round(2 - self.health / self.max_hp + self.cum_rage, 2)

# {{Разум}} Боевой вопль. Оглушение / -уклонение, {Chance(60+self.lvl*2, source=SRC.MIND, extra=SRC.STUN).show(other)}
    def options(self, other):
        opt_rep = f'[1]* Орочий бердыш. Ярость от ран x{self.get_rage()}. \n' \
                  f'[2] Созыв гоблинов. Осталось {self.authority} вызовов. \n' \
                  f'[3]* Кастет. Игнорирует 50% брони, {Chance(60+self.lvl, source=SRC.MOVEMENT).show(other)} сместить цель.\n' \
                  f'[4] Метательный топор х2 (д/б). При попадании дебаффает уклонение c шансом {60+self.lvl}%. \n' \
                  f'[5] Сила семьи. Укрепление брони, Радость на свой ряд, -ярость. \n' + super().options(other)
        return opt_rep

    def firstAction(self, other, ctx):
        return self.MeleePattern(other, ctx, multCoef=self.get_rage())

    def preChoiceAction(self, other, ctx):
        """
        если дважды вызвать option(), то действие ниже будет вызвано два раза.
        """
        x = self.getRandomUnitsFromTeamWhichNotEqualMe(other.team, 1)
        delta = self.lvl-1 if self.crit < -10 else 0  # Проклятая аура, пока сам не станет критовиком.
        if len(x) > 0: x[0].crit -= delta
        if delta != 0: send(ctx, f'\n Проклятая аура хана орков поглотила {delta} удачи {other}...')


    def secondAction(self, other, ctx):
        if self.authority <= 0:
            send(ctx, 'Ваши поданные не доверяет вам, милорд. Никто из гоблинов пока не собирается умирать за вас. МЕРЗАВЦЫ!')
            return -1
        self.authority -= 1
        send(ctx, f'Какого гоблина вы хотите призвать, Хан {self.name}? \n [а] Шаман. Усиления, площадный урон. \n [б] Разведчик. Яд и кража золота.')
        for event in longpoll.listen():
            if event.obj['message']['text'].lower() == 'а':
                if self.createSummon(GoblinShaman, ctx):
                    send(ctx, 'Гоблинский шаман готов вступить в схватку.')
                    break
                else:
                    return -1
            if event.obj['message']['text'].lower() == 'б':
                if self.createSummon(GoblinTrapper, ctx):
                    send(ctx, 'Гоблин-разведчик прибывает на поле битвы.')
                    break
                else:
                    return -1

    def thirdAction(self, other, ctx):
        damage = self.MeleePattern(other, ctx, armorIgnore=0.5, multCoef=0.75, specialReport=Template(f'Орк наносит мощный удар на $dmg урона кастетом по {other}.'))
        if damage in (0, -1): return damage
        report = 'Ох! '
        if Chance(60+self.lvl, source=SRC.MOVEMENT).roll(other):
            report = f'Слабый морра {other} не выдержал могучего удара и был позорно откинут на другой ряд! '
            other.movement()
        if Chance(20 + self.lvl*1.5):
            report += f'Более того, {self} повредил пах {other}.'
            other.addEffect(EFF.CHAINED, 2)
        send(ctx, report)
        return damage


    def fourthAction(self, other, ctx):
        # if self.luck(ctx, other) == -1:
        #     return 0
        # if self.evade(other, -10, ctx):
        #     return 0
        # other: root.HeroInstance
        # if other.stunMyself(Chance(60+self.lvl*2, source=SRC.MIND)):
        #     send(ctx, 'Неистовый вопль орка оглушил вашего противника!')
        # else:
        #     x = randint(6, self.lvl + 7)
        #     send(ctx, f'{other} успешно сопротивляется вашему крику, однако вы уменьшили уклонение на {x} пт.')
        #     other.dodge -= x
        x = self.ArcherPattern(other, ctx, multCoef=0.5, specialReport=Template(f'Метательный топорик орка прилетает точно в несчастную {other.name} на $dmg урона.'))
        if x not in (0, -1) and Chance(60+self.lvl): other.addEffect(EFF.FATMAN, 2, power=[15+self.lvl])
        send(ctx, 'Укажите постфикс цели для второй атаки:')
        for choice in longpoll.listen():
            try:
                postfix = choice.obj['message']['text'].lower()
            except:
                continue
            if not id_checker(self.id, choice): continue
            if len(postfix) == 2 and postfix[0] in ('e', 'е'):
                B = getMember(self.enemyTeam, postfix, choice)
                if B == -1: continue
                y = self.ArcherPattern(B, ctx, multCoef=0.5, specialReport=Template(f'Метательный топорик орка прилетает точно в несчастную {other.name} на $dmg урона.'))
                if y not in (0, -1) and Chance(60+self.lvl): B.addEffect(EFF.FATMAN, 2, power=[15 + self.lvl])
                break
        self.crit -= randint(1, 5) # Если хочешь продолжать распространять ауру.

    def fifthAction(self, other, ctx):
        for unit in self.getOwnRow():
            unit.addEffect(EFF.HAPPY, 2, [15 + self.lvl*2])
        armorDelta = randint(2 * self.lvl, 3 * self.lvl + 7)
        send(ctx, f'Уйдя в воспоминания, орк надевает элемент отцовского доспеха... Он приобретёт {armorDelta} брони и придаст себе душевно-моральных сил.')
        self.arm += armorDelta
        self.cum_rage = max(-0.5, self.cum_rage - 0.06)

    def protection(self, ctx):
        self.addEffect(EFF.STRENGTH, 2, [0.25 + self.lvl//25])
        super().protection(ctx)

    def levelup(self, ind=1):
        num = (self.lvl // 2 + 3) * ind if self.crit <= 0 else 2 * ind
        self.crit += num
        self.dmg += (self.lvl // 2 + 1) * ind
        self.acc += 2 * ind
        if self.hidden_lvl % 6 == 0:
            self.authority += 1
        if self.hidden_lvl % 10 == 0:
            self.max_summons += 1
        super().levelup(ind)

    def startInventory(self):
        self.inv.addItem(Item(619))
        self.addRandItemsByTier(supremum=1)
        # Операции с инвентарём нужно производить не в конструкторе, а отдельно.

