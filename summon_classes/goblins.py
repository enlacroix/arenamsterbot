from random import randint
from core import root
import varbank as vb
from datastore.deffect import EFF
from datastore.dsources import SRC
from datastore.misc import RACES
from vkmodule import send
from myrandom import Chance


class GoblinShaman(root.Hero):
    def __init__(self, pvp_id: int):
        super().__init__(pvp_id)
        self.race = RACES.NONHUMAN

    def options(self, other):
        opt_report = f'[1] {{Воздух, 2 МР}} Степная буря (на ряд) \n ' \
                     f'[2] Кротовый отвар и вкуусный булка: изменение удачи и точности. 2 МР \n' \
                     f'[3] Отправиться к праотцам. Пожертвовать собой для восстановления жизней хозяина. \n' \
                     f'[4] Поцелуй Лепрекона. временное увеличение удачи, 3 МР. \n' \
                     + super().options(other)
        return opt_report

    def firstAction(self, other, ctx, source=SRC.AIR, multCoef=1, addComp=0):
        if not self.spend_mana(2, ctx): return -1
        for enemy in filter(lambda x: x.position == other.position, vb.teams[(self.team + 1) % 2]): # Атака по ряду.
            send(ctx, f'Зачарованная гроза шамана нанесла {enemy.harmWithSRC(source, self.power)} урона существу {enemy.cls_name}.')

    def secondAction(self, other, ctx):
        if not self.spend_mana(2, ctx): return -1
        a = randint(-3, 4 + self.lvl)
        b = randint(-3, 4 + self.lvl)
        other.acc += a
        other.crit += b
        send(ctx, f'Шаман вливает вам в рот жёлтую вязкую жидкость, которая изменяет параметр удачи на {b} единиц, а точности на {a} единиц.')


    def thirdAction(self, other, ctx):
        if self.hasMaster():
            send(ctx, f'Шаман закалывает себя ритуальным ножом с криками о том, что победа непременно будет за {self.master.cls_name}... '
                      f'Когда его речь превращается в булькание, заклятье передает жизненные силы шамана {self.name} '
                      f'в размере {self.master.heal(self.health)} здоровья. Жил грешно, а умер смешно.')
            self.kill()
        else:
            send(ctx, f'У вас нет повелителя - бесполезно.')
            return -1

    def fourthAction(self, other: root.HeroInstance, ctx):
        if not self.spend_mana(3, ctx): return -1
        other.addEffect(EFF.LUCKY, rounds=1, power=[20+self.lvl]) # Хан должен подождать этого баффа.
        send(ctx, f'Шаман подпитывает своего повелителя мистической энергией, которая временно увеличит его удачу на {20+self.lvl} пт.')


    def levelup(self, ind=1):
        self.mana += ind
        self.power += 4 * ind
        self.max_hp += 4 * ind
        self.heal(4 * ind)
        super().levelup(ind)



    def death(self, ctx):
        if super().death(ctx):
            if self.hasMaster(('OrcKing', )):
                self.master.cum_rage += 0.03
                send(ctx, f'{self.cls_name} погиб, и ярость его Хана немного растёт (хотя шаманов он не очень-то и любил, но нужно сохранить лицо)')
                return 1
            return 0


class GoblinTrapper(root.Hero):
    def __init__(self, pvp_id):
        super().__init__(pvp_id)
        self.race = RACES.NONHUMAN

    def options(self, other):
        opt_report = f'[1] {{Оружие|Земля}} Хитиновый лук | Яд ({1 + self.lvl // 5}), {Chance(75 + self.lvl * 2, SRC.EARTH).show(other)}\n' \
                     f'[2] Кража золота, {65 + self.lvl * 2}% \n' \
                     f'[3] Шпионаж. Показать инвентарь и финансы противника. +уровень себе. \n' \
                     f'[4] Сладкие радости. Ускорение (+25 ини) на союзника \n' + super().options(other)
        return opt_report

    def firstAction(self, other: root.HeroInstance, ctx):
        x = self.ArcherPattern(other, ctx)
        if x not in (0, -1) and Chance(75 + self.lvl * 2, SRC.EARTH).roll(other):
            send(ctx, 'Гоблин подпирает с пола использованный шприц и смачно втыкает его в коленную чашечку врага. Похоже он теперь отравлен какой-то дрянью...')
            other.addEffect(EFF.POISON, 1 + self.lvl // 5, [0.9])
        return x

    def secondAction(self, other, ctx):
        if Chance(65 + self.lvl * 2):
            stolen_gold = min(randint(60, 100 + self.getMaster().lvl * 15), vb.Team.Entry(self.enemyTeam).gold)
            if stolen_gold <= 0:
                send(ctx, 'Денег у врага нет. Попробуйте другое действие.')
                return -1
            vb.Team.Entry(self.enemyTeam).gold -= stolen_gold
            vb.Team.Entry(self.team).gold += stolen_gold
            send(ctx, f'Гоблин успешно крадет {stolen_gold} монет.')
        else:
            self.health = randint(-3, 0)  # -3, -2 - смерть, лвлап не вылечит его. -1, 0 - спасение.
            send(ctx, f'Попытка воровства провалилась, но гоблин сумел выскользнуть из импровизированной виселицы,'
                      f' которую соорудил {other}. Траппер хрипит и держится за шею - выживет ли он? Узнаем в следующей серии!')

    def thirdAction(self, other, ctx):
        send(ctx, str(other.inv) + '\n' + f'Золото: {other.gold} монет. Сходив в разведку, гоблин чувствует, что стал опытнее.')
        self.levelup()

    def fourthAction(self, other, ctx):
        if self.team != other.team: return -1
        other.addEffect(EFF.HASTE, 2, power=[25])

    def levelup(self, ind=1):
        self.lvl += ind
        self.acc += ind * 2
        self.dmg += 4 * ind
        self.crit += 3 * ind
        self.max_hp += 2 * ind
        self.heal(2 * ind)  # Здесь тонкая калибровка по казни за монеты.

    def death(self, ctx):
        if super().death(ctx):
            if self.hasMaster(('OrcKing',)):
                self.master.cum_rage += 0.05
                send(ctx, f'{self.cls_name} погиб. Хан орков оплакивает его, как родного сына. Он поклялся отомстить.')
                return 1
            return 0

