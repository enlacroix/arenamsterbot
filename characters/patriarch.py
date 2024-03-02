from datastore.deffect import EFF
from datastore.dsources import SRC
from core.root import Hero, HeroInstance
import varbank as vb
from myrandom import Chance
from vkmodule import send, longpoll, id_checker

# TODO давать немного защиты от элементов
# раньше было Лечение с добавлением Жизней. - слишком сильно и противоречит механике отдельного воскреса.

class Patriarch(Hero):
    def __init__(self, _id):
        super().__init__(_id)
        self.ulta = 1

    def options(self, other):
        opt_report = f'[1] {{Воздух}} Гнев богов (По колонне), 2 МР \n ' \
                     f'[2] Изобильный свет. Лечение цели, 3 МР \n' \
                     f'[3]** Милость Младшего. Воскрешение союзников, 5 МР \n' \
                     f'[4] Святилище. Временно защитить цель так, что её нельзя выбрать целью атаки, {self.ulta} применений. \n' \
                     + super().options(other)
        return opt_report

    def firstAction(self, other, ctx):
        for enemy in other.getOwnColumn():
            x = self.MagicPattern(enemy, ctx, source=SRC.AIR, mana=1)
            if x in (0, -1): return x

    def secondAction(self, other, ctx):
        if self.allyActionForEnemy(other, ctx): return -1
        if not self.spend_mana(3, ctx): return -1
        send(ctx, f'{other.heal(other.lvl * 7 + self.power // 3)} здоровья было восстановлено Патриархом.')


    def thirdAction(self, other, ctx):
        if not self.isAtSecondRow(ctx): return -1
        if not self.spend_mana(5, ctx): return -1
        report = f'[0]. Выйти из меню. \n'
        N = len(vb.Team.Entry(self.team).graveyard)
        for i, unit in enumerate(vb.Team.Entry(self.team).graveyard):
            report += f'{i+1}. {unit}, уровень {unit.lvl}, {"🚫" if unit.isForbiddenToResurrect else "✅"} \n'
        send(ctx, report)
        for event in longpoll.listen():
            if not id_checker(self.id, ctx): continue
            current: str = event.obj['message']['text'].lower()
            if current == '0': break
            if current.isdigit() and int(current) <= N:
                target : HeroInstance = vb.Team.Entry(self.team).graveyard[int(current) - 1]
                if not target.animate(self.team):
                    send(ctx, 'Цель невозможно поднять, так как она была подвержена проклятью искоренения.')
                    continue
                else:
                    send(ctx, f'{target} успешно восстал из мёртвых!')
                    if Chance(50): target.isForbiddenToResurrect = True
                    break

    def fourthAction(self, other: HeroInstance, ctx):
        if not self.ulta > 0: return -1
        self.ulta -= 1
        other.addEffect(EFF.SANCTUM, 2 + self.lvl // 5)
        send(ctx, f'Вы оказываетесь под защитным куполом Патриарха.')

    def levelup(self, ind=1):
        if self.hidden_lvl % 7 == 0: self.ulta += 1
        self.arm += 3 * ind
        self.power += 4 * ind
        self.mana += 1 * ind
        super().levelup(ind)