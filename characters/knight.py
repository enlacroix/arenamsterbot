"""
Свадийский рыцарь: Кавалерийская пика, удар по задним х1,5 но с меньшей точностью. Если оз меньше половины, то лошадь умирает и кавалерский удар не доступен
Нагайка - всыпать плетей, х2 без брони, классика, дебаффнуть мораль и урон
"""
from random import randint, choice
from string import Template

from datastore.deffect import EFF
from datastore.dperks import PRK
from datastore.dsources import SRC
from datastore.misc import RACES
from myrandom import Chance
from resists.rstcls import Resist
from resists.rstmanager import ResistManager
from core.root import Hero
from vkmodule import send


class Knight(Hero):
    def __init__(self, _id):
        super().__init__(_id)
        self.race = RACES.NONHUMAN
        self.horseIsDead = False
        self.lengthOfWeapon = 2
        self.resists = ResistManager({SRC.FINALSTRIKE: Resist(25)})
        self.skills.append(PRK.LOWHP_EXTRATURN)
        # self.skills.append(PRK.MILITARY)

    def options(self, other):
        opt_report = f'[1]* Полированное копьё. Игнор контрудара. С {50+self.lvl*2}% шансом атака заденет юнита позади. \n ' \
                     f'[2]* {"✅" if not self.horseIsDead else "⛔"} Удар пикой наперевес. (достанет задние ряды). \n' \
                     f'[3] Боевая баллада. +{20+self.lvl*2} атаки и +50% получаемого лечения за {100 + self.lvl * 2} монет. \n' \
                     f'[4] Заступник. Охрана выбранного союзника. \n' \
                     f'[5] Приложить подорожник. Снять с себя эффекты Яда, Ожога и Кровотока, {5*self.lvl}% сохранить ход. \n'+ super().options(other)
        return opt_report

    def preChoiceAction(self, other, ctx):
        for unit in self.getOwnRow(): unit.arm += self.lvl + 1
        send(ctx, f'Кентавр укрепляет доспехи сопартийцев на своем ряду на {self.lvl + 1} единиц.')

    def firstAction(self, other, ctx):
        x = self.MeleePattern(other, ctx, ignoreContr=True)
        target = other.getNeighbourOnMyColumn()
        if target is not None and Chance(50+self.lvl*2):
            self.MeleePattern(target, ctx, multCoef=0.6, ignoreMelee=True, specialReport=Template(f'Атака рыцаря задевает и {target}, нанося ему $dmg урона.'))
        else:
            return x

    def secondAction(self, other, ctx):
        if self.horseIsDead:
            send(ctx, 'Ваша "внутренняя" лошадь погибла, поэтому провести такую атаку невозможно.')
            return -1
        return self.MeleePattern(other, ctx, ignoreMelee=True, multCoef=0.75, specialReport=Template(f'На полном скаку кентавр-рыцарь наносит кавалерийский удар копьём  по {other} на $dmg урона!'))


    def thirdAction(self, other, ctx):
        poetry = [f'Узрев {self.name} все застыли от страха... \n Охальника в миг превратил он в кастрата! \n Кишки натянулись, как струны на дыбе… \n' f'Рыцарь ему брюхо вспорол словно рыбе.',
                  f'За цыплёнок мы пьём, прошлым дням наш почёт. \n Скоро век Гарвета совсем истечёт. \n Побьём {other.cls_name}, землю нашу вернём. \n Защищать {self.name} будем мы день за днём.',
                  f'Сдохни, {other.name}, изменник лихой!\n Как ты сгинешь, так будет у нас пир горой.\n Мы {self.name}овы дети, битва нам словно мать.\n Пелагиад ждёт нас светлый, каждый рад жизнь отдать. '
                  f'Но прежде очистим мы Свадию свою. \n Не уступим мы наших надежд воронью.']
        if self.gold >= 100 + self.lvl * 2:
            send(ctx, f'Без проблем, ваше благородие. Вспоминая Правенские застолья, Рыцарь начинает музицировать на лютне: \n {choice(poetry)}')
            self.gold -= 100 + self.lvl * 2
            for ally in self.getOwnRow():
                ally.addEffect(EFF.STRENGTH, 1 + self.lvl // 5, power=[20+self.lvl*2])
                ally.addEffect(EFF.BLESSED, 1 + self.lvl // 6, power=[0.5])
            return 1
        else:
            send(ctx, 'Кентавр презрительно усмехается. Ваших жалких сбережений не хватает, чтобы оплатить услуги боевого барда.')
            return -1

    def fourthAction(self, other, ctx):
        if self.allyActionForEnemy(other, ctx): return -1
        other.addEffect(EFF.GUARDED, 2)
        send(ctx, f'{other} теперь под охраной бравого латника.')

    def fifthAction(self, other, ctx):
        self.effects.delEffect(EFF.BLEEDING)
        self.effects.delEffect(EFF.POISON)
        self.effects.delEffect(EFF.BURNING)
        send(ctx, 'Кентавр использует мешочек с эльфийскими травами, настоями и мазями, которые мигом избавят его от недугов.')
        if Chance(5 * self.lvl):
            send(ctx, 'Кентавр может сделать еще один ход!')
            return -1

    def levelup(self, ind=1):
        if ind > 0 and not self.horseIsDead and self.health <= self.max_hp * 0.5:
            self.ini //= 2
            self.horseIsDead = True
        self.arm += 2 * ind
        self.acc += 3 * ind
        self.dmg += (randint(1, 2) + self.lvl // 3) * ind
        super().levelup(ind)