from random import randint

from datastore.dperks import PRK
from datastore.dsources import SRC
from datastore.misc import RACES
from myrandom import Chance
from resists.rstcls import Resist
from resists.rstmanager import ResistManager
from resists.rststates import Ward
from core.root import Hero
from vkmodule import send
import varbank as vb

class Oracle(Hero):
    def __init__(self, _id):
        super().__init__(_id)
        self.ulta = 1
        self.resists = ResistManager({SRC.FIRE: Resist(0, Ward)})
        self.skills += [PRK.SCROLLS]
        self.race = RACES.ELF

    def options(self, other):
        opt_report = f'[1] Восстановление ОЗ, +увеличение на 15% максимального здоровья, 2 МР\n' \
                     f'[2] Миг могущества. Дополнительный ход для цели, {70 + self.lvl*3}%, 3 МР \n' \
                     f'[3] Знамение Галлеана. Вард от разума и поднятие боевого духа. \n' \
                     f'[4] Аркана энергии. ({self.ulta} применений) Восстановить ману всем на ряду. \n' + super().options(other)
        return opt_report

    def startInventory(self):
        self.addRandItemsByTier(supremum=2)

    def firstAction(self, other, ctx):
        if self.allyActionForEnemy(other, ctx): return -1
        if not self.spend_mana(2, ctx): return -1
        send(ctx, f'Оракул восстановила {other.heal(randint(35 + self.lvl, 50 + self.lvl * 4))} здоровья {other}.')
        other.max_hp = round(other.max_hp * 1.15)

    def secondAction(self, other, ctx):
        if self.allyActionForEnemy(other, ctx): return -1
        if not other in vb.done:
            send(ctx, f'Дождитесь пока {other} сделает свой ход, иначе магия пропадёт впустую.')
            return -1
        if not self.spend_mana(3, ctx): return -1
        if Chance(70 + self.lvl*3):
            vb.done.remove(other)
            send(ctx, f'Используя знаменитые отвары древних эльфов и другие женские хитрости, Оракул даёт дополнительный ход {other}.')
        else:
            send(ctx, f'Настои эльфов не подействовали, и Оракул не смогла сподвигнуть {other.cls_name} на ещё одно действие. '
                      f'Может быть помогут сметана и грецкие орехи...')

    def thirdAction(self, other, ctx):
        if self.allyActionForEnemy(other, ctx): return -1
        send(ctx, f'Пророчество защищает вас от вторжений в Разум и поднимает боевой дух {other.cls_name} на {self.lvl*2} пт')
        other.resists[SRC.MIND].setWard()
        other.morale += self.lvl * 2

    def fourthAction(self, other, ctx):
        if self.ulta <= 0:
            send(ctx, f'У вас пока нет сил, чтобы провести ритуал.')
            return -1
        self.ulta -= 1
        for unit in self.getOwnRow(): unit.mana += randint(4, 8)
        send(ctx, f'Бойцы ряда {self.position+1} восполняют запасы магической энергии благодаря вашему ритуалу.')



    def levelup(self, ind=1):
        self.mana += 2 * ind
        if self.hidden_lvl % 6 == 0: self.ulta += 1
        super().levelup(ind)