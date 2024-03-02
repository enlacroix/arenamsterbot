from random import randint
from datastore.deffect import EFF
from datastore.dsources import SRC
from myrandom import Chance


class VOT:
    # VOT(EffEnum.POISON, power=[25], rounds=2)
    # VOT(EffEnum.BLEEDING, power=[25, self.level*2], rounds=2)
    def __init__(self, identifier: EFF, power: list, rounds: int):
        self.name, self.isPositive = identifier.value['nm'], identifier.value['pos']
        self.canRemove = identifier.value.get('canRemove', True)
        # Если ключа не существует, то значение по умолчанию - 1.
        assert len(power) == identifier.value.get('required_args', 1), 'Передано неправильное число аргументов'
        self.identifier = identifier
        self.rounds = rounds
        self.canRemove = True
        self.message = None
        self.power = power

    def apply(self, unit):
        match self.identifier:
            case EFF.REGENHP:
                self.message = f'{unit} регенерирует на {unit.heal(25 * self.power[0])} пунктов.'
            case EFF.REGENMANA:
                self.message = f'{unit} восполняет {self.power[0]} маны.'
                unit.mana += self.power[0]
            case EFF.KILLMANA:
                self.message = f'{unit} теряет {self.power[0]} маны.'
                unit.mana -= self.power[0]
            case EFF.POISON:  # 1 аргумент в power
                currentValue = unit.harmWithSRC(SRC.DEATH, (randint(4, 6) + self.rounds * 6) * self.power[0])
                self.message = f'Яд растекается по жилам, заставляя вас корчиться от боли. Вы потеряли' \
                               f' {currentValue} ОЗ.'
            case EFF.BURNING:
                currentValue = unit.harmWithSRC(SRC.FIRE, (randint(4, 6) + 15) * self.power[0])
                self.message = f'Вы тщетно пытаетесь потушить себя и теряете {currentValue} ОЗ.'
            case EFF.BLEEDING:  # 2 аргумента в power
                currentValue = unit.harmWithSRC(SRC.DEATH, (4 + self.rounds * 3 + unit.lvl) * self.power[0])
                self.message = f'Вы истекаете кровью и теряете {currentValue} ОЗ.'
                if Chance(35 + self.power[1]):
                    unit.addEffect(EFF.WEAKNESS, power=[0.5], rounds=2)
            case EFF.FEAR:
                currentValue = round((5 + self.power[0]) * unit.getSRCFactor(SRC.MIND))
                unit.morale -= currentValue
                self.message = f'От магического страха {unit} теряет {currentValue} единиц боевого духа.'
            case EFF.GALL:
                currentValue = unit.harmWithSRC(SRC.WATER, 20 * self.power[0])
                currArm = unit.destroyArmor(currentValue // 5, -5)
                self.message = f'Желчь наносит {currentValue} урона, обжигая вас и уничтожая броню на {currArm} единиц.'
            case _:
                self.message = 'Идентификатор не найден!'
        return self.message

    def __str__(self):
        return f'{self.name}: ({self.rounds})'
