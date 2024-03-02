from string import Template

from core import root
from random import randint
from datastore.deffect import EFF
from datastore.dsources import SRC
from vkmodule import send, id_checker, longpoll
from myrandom import Chance
import varbank as vb
from settings import FAIR_FREQUENCY
'''
 под невидимостью атака ближнего боя становится атакой лучника, как будто пол инвизом подбегаешь и бьешь.
Мастер-шпион, добавить ей воровские действия, как в дисах - 
отравление всего отряда (на след раунд после ярмарки), подделывание приказа, убийство слабого (c минимальным хп, причем его текущее менее 25% от максимума),
 шпионаж, воровство предметов
'''
class Detective(root.Hero):
    def __init__(self, pvp_id):
        super().__init__(pvp_id)
        self.gun = 1  # Перезарядка орудия
        self.ulta = 2 # Количество уходов в невидимость.
        self.develop = 5  # Перк каждые 5 уровней, быстрое развитие.

    def options(self, other): # ➡️ - означает, что после атаки будет перемещение на другой ряд.
        opt_rep = f'[1]* Короткая рапира, игнор охраны, х2 шанса крита против Метки.  \n' \
                  f'[2] Диверсия. Украсть предмет, {60 + self.lvl*2}% | Отравить отряд. \n' \
                  f'[3] Выпить зелье, {self.ulta} шт. Невидимость, атака [1] станет д/б. \n'\
                  f'[4]** Выпад дуэлянта ➡️, контрудар, (+уклонение) \n' \
                  f'[5]* Выстрел в упор ➡️(50%) | Перезарядка (+крит). Оружие {"заряжено" if self.gun == 1 else "разряжено"}. \n'\
                  + super().options(other) # Пистолет Герсталь?
        return opt_rep

    def startInventory(self):
        self.addRandItemsByTier(infimum=1, supremum=2, count=2)

    def firstAction(self, other, ctx):
        return self.MeleePattern(other, ctx, ignoreGuard=True, ignoreMelee=self.hasEffect(EFF.INVISIBLE), critCoef=2 if other.hasEffect(EFF.MARKED) else 1)

    def secondAction(self, other: root.HeroInstance, ctx):
        # if other.hasPerk(PRK.NOBILITY):
        #     send(ctx, f'{other}, известный как Погибель воров, с легкостью пресекает ваши жалкие попытки воровства, сломав вам ноготь. Грубый мужлан, свинья!')
        #     return 0
        if not len(other.inv) > 0:
            send(ctx, 'Пока нечего воровать, зайдите позже.')
            return -1
        if abs(vb.stage - FAIR_FREQUENCY) < 2:
            send(ctx, 'Небезопасно проводить диверсии до или после ярмарки - все слишком насторожены. Нужно выждать подходящего момента.')
            return -1
        send(ctx, f'Вы нащупали следующие вещи: \n {other.inv}')
        send(ctx, f'[укр k], где k - номер предмета, который вы хотите украсть. (без кв. скобок) \n [яд] отравить весь отряд, {self.ulta} яда \n[стоп] - остановить операцию.')
        for choice in longpoll.listen():
            try: current = choice.obj['message']['text'].lower()
            except: continue
            if not id_checker(self.id, choice): continue
            match current.split(' '):
                case['укр', num]:
                    item = other.inv.getItem(int(num))
                    if item is None:
                        send(ctx, f'Предмета с номером {num} не существует в инвентаре.')
                        continue
                    if item.protection_from_steal:
                        send(ctx, f'{item} невозможно украсть! Попробуйте другое действие.')
                        continue
                    if Chance(60 + self.lvl*2):
                        send(ctx, f'{item} был успешно украден!')
                        self.inv.addItem(item)
                        other.inv.removeItem(item)
                    else:
                        send(ctx, 'Попытка кражи провалилась! Вы спешно отступаете, стараясь минимизировать свой провал.')
                    break
                case ['стоп']:
                    break
                case ['яд']:
                    if not self.ulta > 0:
                        send(ctx, f'У вас кончился крысиный яд.')
                        break
                    self.ulta -= 1
                    for enemy in vb.teams[self.enemyTeam]: enemy.addEffect(EFF.POISON, 2, power=[0.8])
                    send(ctx, 'Детектив успешно подмешивает яды в напитки вражеского отряда. Приятного аппетита.')
                    break
                case _:
                    continue

    def thirdAction(self, other, ctx):
        if self.ulta > 0:
            self.ulta -= 1
            self.addEffect(EFF.INVISIBLE, 2)
            send(ctx, f'{self} быстро опрокидывает в себя стопку с зельем, становясь невидимым.')
        else:
            send(ctx, 'Склянки с зельем невидимости закончились!')
            return -1

    def fourthAction(self, other, ctx):
        if not self.isAtSecondRow(ctx): return -1
        self.movement()
        res = self.MeleePattern(other, ctx, ignoreMelee=True, multCoef=0.5, specialReport=Template(f'Шпионка делает особой выпад клинком на $dmg урона, становясь в контратакующую стойку.'))
        if res not in (0, -1):
            self.addEffect(EFF.CONTR, 2 + self.lvl // 6)
        return res


    def fifthAction(self, other, ctx):
        if self.position != 0: return -1
        if self.gun == 1:
            shotgun = max(round((self.dmg * 1.25 - other.arm * 1.5) * (1 - other.dodge / 100) * other.getSRCFactor(SRC.ARROWS) * (0.5 if other.position == 1 else 1)) + randint(10, 15), 0)
            other.health -= shotgun
            send(ctx, f'Детектив молниеносно вынимает обрез и стреляет на {shotgun} урона. Мистер Сальери передаёт вам поклон.')
            self.gun = 0
            if Chance(50): self.movement()
            return
        if self.gun == 0:
            critBonus = randint(1, 4) + self.lvl // 4
            self.crit += critBonus
            send(ctx, f'Детектив ловко перезаряжает дробовик. Она впадает в кураж: удача поднялась на {critBonus} пунктов!')
            self.gun = 1
            return

    def levelup(self, ind=1):
        if vb.stage % 5 == 0 and ind > 0:
            self.crit += 5
            self.steals += 1
        self.dodge += randint(1, 2) * ind
        self.dmg += (self.lvl // 2 + randint(1, 3)) * ind
        super().levelup(ind)

    def protection(self, ctx):
        super().protection(ctx)
