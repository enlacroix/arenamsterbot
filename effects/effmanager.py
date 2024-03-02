"""
Типы эффектов:
1. Баффы/дебаффы.
имеют время действия, имеют прямой и обратный эффект. Имеют силу (мощность).
2. Доты
Имеют силу (мощность). слабые/сильные яды.
Имеют время действия, время уменьшается только один раз в раунд, имеют только прямой эффект. Могут быть также положительными и отрицательными.
3. Временные метки
Временный эффект - это то, что не имеет методов straight() и reverse(), и не является дотом (некий эффект, который применяется ровно 1 раз в раунд).
Проверяется только его наличие у игрока и важно то, что он висит некое время, которое идёт одинаково для всех трёх типов.
Примеры: укреплённая броня, безмолвие, защитная стойка и т.д.
*Огненный щит, контрудар, парирование - время уменьшается не только тиком, но и вручную, когда срабатывает этот эффект.

Архитектурное требование:
- избегать импортирования модуля эффектов, сделав интерфейс, который не требует классов.
- избегать хардкодинга названий кодировок эффектов и использовать поля класса перечислений.
- использовать именованные аргументы для большей читаемости кода.
Пример: other.addEffect(EffEnum.POISON, rounds=2, power=25)
"""
from effects.rstchanger import ResistChanger
from datastore.deffect import EFF, EffType
from effects.effect_cls import Effect
from effects.valovertime import VOT
from effects.templabels import TempLabel
from effects.customeffs import CustomEffect
from vkmodule import send


class EffectManager:
    # TODO ДОБАВИТЬ ВОЗМОЖНОСТЬ ЮНИТАМ ИМЕТЬ ИММУНИТЕТЫ И СТОЙКОСТЬ К ЭФФЕКТАМ (БЕЗ ПРИВЯЗКИ К ИСТОЧНИКУ)
    def __init__(self, unit):
        self.unit = unit
        self.pool = []

    def effectFabric(self, identifier: EFF, rounds: int, power, typeOfEffect):
        match typeOfEffect:  # Шоколадная абстрактная фабрика, мать её.
            case EffType.BuffsDebuffs:
                eff = Effect(identifier, power, rounds)
                eff.straight(self.unit)  # TODO Помни, что сразу при инициализации мы накладываем straight() на юнита.
            case EffType.VOT:
                eff = VOT(identifier, power, rounds)
            case EffType.TempLabels:
                eff = TempLabel(identifier, rounds, power)
            case EffType.Custom:
                eff = CustomEffect(identifier, rounds, power)
                eff.straight(self.unit)
            case EffType.ResistChanger:
                eff = ResistChanger(identifier, power, rounds)
                eff.straight(self.unit)
            case _:
                # Почти невозможно. Сообщи об ошибке.
                eff = None
        return eff

    def addEffect(self, identifier: EFF, rounds: int, power):
        """
         if name_of_key.startswith('-'):
        try:
            n = unit.effects['reflect']
        except KeyError:
            return
        k = mf.check_effect(vb.teams[(unit.team + 1) % 2][0], 'reflect')
        if mf.chance(50 * n) and not k:
            add_effect(vb.teams[(unit.team + 1) % 2][0], name_of_key, num)
        """
        if identifier.value.get('pos', None) is False and self.hasEffect(EFF.REFLECTION):
            targetList = self.unit.getRandomUnitsFromTeamWhichNotEqualMe((self.unit.team + 1) % 2, 1)
            if len(targetList) > 0 and not targetList[0].effects.hasEffect(EFF.REFLECTION):
                targetList[0].addEffect(identifier, rounds, power)
                return 1
        formerEffect = self.getEffect(identifier)
        if formerEffect is None:
            newEffect = self.effectFabric(identifier, rounds, power, typeOfEffect=identifier.value['type'])
            self.pool.append(newEffect)
            return 0
        else:  # Избыточный else. для читабельности оставлю.
            formerEffect.rounds += rounds
            # Так нельзя делать, поскольку уже были рассчитаны возвращающие дельты для ТЕКУЩЕГО значения power.
            # power увеличится, но delta нет - пришлось бы запускать механизм пересчёта, если у меня когда-то будет желание реализовать подобное.
            # formerEffect.power = max(abs(power), abs(formerEffect.power))
            return 1

    def getEffect(self, identifier):
        return next((eff for eff in self.pool if eff.identifier == identifier), None)

    def delEffect(self, identifier):
        eff = self.getEffect(identifier)
        if eff is None: return # print('Такого эффекта нет в пуле')
        self.pool.remove(eff)

    def removeBadEffects(self):
        for eff in filter(lambda x: x.isPositive == False, self.pool):
            self.pool.remove(eff)
            if isinstance(eff, (Effect, CustomEffect, ResistChanger)): eff.reverse(self.unit)


    def getEffectRounds(self, identifier) -> int:
        my_eff = self.getEffect(identifier)
        if my_eff is None: return 0
        return my_eff.rounds


    def __getitem__(self, item):
        return self.getEffect(item)

    def hasEffect(self, identifier) -> bool:
        for eff in self.pool:
            if eff.identifier == identifier:
                return True
        return False

    def timeTicks(self):
        for eff in filter(lambda x: not isinstance(x, VOT) and x.rounds > 0 and not x.identifier == EFF.STUNNED, self.pool): eff.rounds -= 1


    def applyVOTs(self, event):
        for eff in filter(lambda x: isinstance(x, VOT) and x.rounds > 0, self.pool):
            send(event, eff.apply(self.unit))
            eff.rounds -= 1
        self.unit.was_effected = True

    def __str__(self):
        if len(self.pool) == 0:
            return 'Нет'
        return ', '.join(map(str, self.pool))

    def checkEnding(self):
        for eff in self.pool:
            if eff.rounds <= 0:
                self.pool.remove(eff)
                if isinstance(eff, (Effect, CustomEffect, ResistChanger)): eff.reverse(self.unit)

'''
    def timeTicks(self, event):
        for eff in self.pool:
            if isinstance(eff, VOT) and eff.rounds > 0:
                send(event, eff.apply(self.unit))
            eff.rounds -= 1
        self.unit.was_effected = True
'''