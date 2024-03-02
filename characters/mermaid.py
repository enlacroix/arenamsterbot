from random import choice
from datastore.deffect import EFF
from datastore.dsources import SRC
from datastore.misc import RACES
from myrandom import Chance
from core.root import Hero, HeroInstance
from vkmodule import send
import varbank as vb

class Mermaid(Hero):
    # Русал.
    def __init__(self, _id):
        super().__init__(_id)
        self.race = RACES.NONHUMAN
        self.ulta = 1

    def options(self, other):
        # Высокоинициативный хилер и контролер.
        opt_report = f'[1] Морской бриз. Лечение (эфф. при низком ОЗ цели), + {self.lvl * 2 + 2}точности пост. \n ' \
                     f'[2] {{Вода}}. Массовое обледенение (паралич) ряда противника, {Chance(38 + self.lvl, SRC.WATER, SRC.STUN).show(other)}. \n ' \
                     f'[3] Песнь сирены, {self.ulta} раз осталось. Регенерация на одного случ союзника, поработить вражескую цель. \n ' \
                     f'[4] Наложить эффект Волшебных оков на противника, 2 МР' + super().options(other)
        return opt_report

    def firstAction(self, other, ctx):
        if self.allyActionForEnemy(other, ctx): return -1
        bonusForLowHP = round(20 * (2 - other.health / other.max_hp))
        send(ctx, f'Здоровье {other.cls_name} было восстановлено на {other.heal(self.lvl * 5 + bonusForLowHP)}, а точность увеличена на {self.lvl * 2 + 2}%.')
        other.acc += self.lvl * 2 + 2

    def secondAction(self, other: HeroInstance, ctx):
        for unit in other.getOwnRow():
            if unit.stunMyself(Chance(38 + self.lvl, source=SRC.WATER)):
                send(ctx, f'Русалка обращает {unit} в ледяную статую...')
            else:
                send(ctx, f'{unit} отразил атаку русалки!')


    def thirdAction(self, other: HeroInstance, ctx):
        if not self.ulta > 0: return -1
        for ally in self.RandomUnitsFromMyTeam(1): ally.addEffect(EFF.REGENHP, 2, power=[1+self.lvl*0.2])
        songs = [f'Мое сердце так тоскует \n Ни к чему мне денег звон, \n Лишь {other.cls_name} меня утешит \n Ведь дороже злата он',
                 f'Моряки нас всех бояться \n Но и любят страстно нас, \n Ведь красавица-русалка \n Не проста как первый взгляд',
                 f'Ах, красавицы-девицы \n Всем давно известно нам, \n Что {other.cls_name} нам смелый дорог \n Тот скользящий по волнам',
                 f'В пенной бухте мы остались \n И наводим на всех страх, \n Спамеров особо жестко \n Обрекаем на наказ'
                 ]
        self.ulta -= 1
        if other.race in (RACES.UNDEAD, RACES.ARTIFICIAL):
            send(ctx, 'Нежить и механизмы не купятся на эти штучки.')
            return 1
        send(ctx, f'Русалка доверительно смотрит в глаза {other.name} и начинает петь: \n {choice(songs)}. \n Она овладевает рассудком {other}.')
        vb.teams[other.team].remove(other)
        vb.teams[self.team].append(other)
        other.id = self.id
        other.addEffect(EFF.ENSLAVED, 1)

    def fourthAction(self, other, ctx):
        if not self.spend_mana(2, ctx): return -1
        other.addEffect(EFF.MAGIC_SHACKLES, 2+self.lvl//6)
        send(ctx, f'Русалка заковывает {other} в магические кандалы, которые будут обжигать его всякий раз, когда он будет применять магию.')
        # send(ctx, f'{other} был прикован к своему ряду якорем морской твари.')
        # other.addEffect(EFF.CHAINED, 2+self.lvl//6)

    def levelup(self, ind=1):
        if self.hidden_lvl % 4 == 0:
            self.ulta += 1
        self.mana += ind
        super().levelup(ind)

