from string import Template

from core import root
from random import randint

from datastore.deffect import EFF
from datastore.dperks import PRK
from datastore.dsources import SRC
from datastore.misc import RACES
from myrandom import Chance
from resists.rstcls import Resist
from resists.rstmanager import ResistManager
from resists.rststates import Ward, Immunity
from vkmodule import send
import varbank as vb
'''
что было раньше у демонолога:
# Удар хвостом + Кислота (2 МР), уничтожение брони (можно было и в отриц)
f'[2] 🔥 Геенна. Огненный шторм на команду, % шанс поджога врага, 5 МР \n ' \
f'[3] Медитация. Восстановление маны, +мастерство. Огненный щит. \n' \
f'[4] ⚔ Кнут бездны. уменьшение атаки, макс. ОЗ оппонента, 2 МР \n' \
5. Призыв доппеля
'''

class DemonLord(root.Hero):
    size = 2 # Гигант

    def __init__(self, pvp_id):
        super().__init__(pvp_id)
        self.resists = ResistManager({SRC.MOVEMENT: Resist(0, Immunity), SRC.FIRE: Resist(50, Ward), SRC.MIND: Resist(0, Ward)})
        self.race = RACES.DEMON
        self.ulta = 2
        self.lengthOfWeapon = 2
        self.skills.append(PRK.TALISMANS)

    def options(self, other):
        opt_rep = f'[1]* Трёхглавый удар (по ряду). Умершие от атаки восстановят вам ОЗ. \n'\
                  f'[2]* Клинок Бездны / Обратить в камень, {Chance(70+self.lvl, SRC.EARTH, SRC.STUN).show(other)} \n'\
                  f'[3] {{Вода}} Плевок кислотой / Уничтожить броню, 75% \n'\
                  f'[4] Глубинная защита. Окутать себя огненным щитом, а на цель Регенерацию. \n'\
                  f'[5] Катавасия, {self.ulta} применений. Перемешивает ряды противника, небольшой массовый урон. \n' + super().options(other)
        return opt_rep

    def firstAction(self, other, ctx):
        if not self.isReachableForMelee(other, ctx): return -1
        for enemy in filter(lambda x: x.position == other.position, vb.teams[self.enemyTeam]): # удар по ряду, где находится вражеская цель
            self.MeleePattern(enemy, ctx, specialReport=Template(f'Демон-принц наносит $dmg урона по {enemy}...'))
            if enemy.health < 0 and enemy.lives <= 0 and enemy.resists[SRC.FINALSTRIKE].value == 0: send(ctx, f'Демон пожирает труп {enemy} и восстанавливает {self.heal(0.25 * other.max_hp)} ОЗ.')
        return 'mass'

    def secondAction(self, other: root.HeroInstance, ctx):
        x = self.MeleePattern(other, ctx, multCoef=2)
        if x not in (0, -1) and other.stunMyself(Chance(70+self.lvl, SRC.EARTH), 1 + self.lvl // 8):
            send(ctx, f'{other} обратился в каменную статую! Но есть и плюсы - вы теперь надежно защищены от вражеского урона Стихиями и Оружием.')
            other.addEffect(EFF.PETRIFIED, 2, power=[75, 75, 75, 75, 75])
        return x


    def thirdAction(self, other: root.HeroInstance, ctx):
        x = self.MagicPattern(other, ctx, mana=0, source=SRC.WATER, specialReport=Template(f'Демон прицеливается и плюёт кислотой аккурат в бедолагу {other} на $dmg урона.'))
        if x not in (0, -1) and Chance(75):
            send(ctx, f'Доспехи {other} были уничтожены на {other.destroyArmor(x*0.4, cap=-15-self.lvl)} пунктов.')
        return x

    def fourthAction(self, other: root.HeroInstance, ctx):
        if self.team != other.team: return -1
        self.addEffect(EFF.FIRESHIELD, 2)
        other.addEffect(EFF.REGENHP, 2 + self.lvl // 5, power=[1.25])
        # other.addEffect(EFF.MAXHPBUFF, 2 + self.lvl // 4, power=[50+self.lvl*5])
        send(ctx, f'Покровительство от демона-принца окутало его огненным плащом и дало {other} небывалый прилив сил.')


    def fifthAction(self, other, ctx):
        if not self.ulta > 0: return -1
        self.ulta -= 1
        for enemy in vb.teams[self.enemyTeam]:
            enemy: root.HeroInstance
            enemy.harmWithSRC(SRC.WEAPON, 15+self.lvl)
            enemy.position = randint(0, 1)
        send(ctx, 'Демон сотрясает землю, заставляя падать своих противников на землю - кто-то вернётся на свои позиции, кто-то нет.')


    def protection(self, ctx):
        super().protection(ctx)
        self.heal(randint(20, 35 + self.lvl*2))

    def startInventory(self):
        self.addRandItemsByTier(infimum=2, supremum=4, count=2)

    def levelup(self, ind=1):
        if self.hidden_lvl % 5 == 0: self.ulta += 1
        self.power += randint(2, 4) * ind
        self.crit += ind * 2
        self.mana += ind
        self.armor_penetration += 0.04 * ind
        self.dmg += (self.lvl // 2 + randint(1, 2)) * ind
        self.ini += randint(-2, 3) * ind
        super().levelup(ind)

