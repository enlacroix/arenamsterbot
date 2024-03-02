from datastore.deffect import EFF
from datastore.dsources import SRC
import varbank as vb

class CustomEffect:
    """
    Кастомный эффект является расширением класса Effect, который имеет методы .straight() и .reverse(),
    но может прописать свою собственную реализацию, не опираясь на список изменяемых атрибутов персонажа.
    Пример: дать Вард от огня и воздуха на 3 раунда.
    """
    def __init__(self, identifier: EFF, rounds: int, power: list = None):
        self.identifier = identifier
        self.name, self.isPositive = identifier.value['nm'], identifier.value['pos']
        self.rounds = rounds
        self.power = power
        self.canRemove = identifier.value.get('canRemove', True)

    def __str__(self):
        return f'{self.name}: ({self.rounds})'

    def straight(self, unit):
        match self.identifier:
            case EFF.TEMPLVLUP:
                unit.levelup(self.power[0])
            case EFF.STUNNED:
                unit.resists.changeValue(SRC.STUN, 65)
            case _:
                pass

    def reverse(self, unit):
        match self.identifier:
            case EFF.TEMPLVLUP:
                unit.levelup(-self.power[0])
                unit.hidden_lvl -= self.power[0]
            case EFF.IMPISH:
                unit.transformToAnotherClass(unit.memory[0])
                unit.arm = max(unit.memory[1], unit.arm)
            case EFF.STUNNED:
                unit.resists.changeValue(SRC.STUN, -65)
            case EFF.DEFEND:
                unit.resists.changeSeveralResists((SRC.WEAPON, SRC.FIRE, SRC.WATER, SRC.AIR, SRC.EARTH, SRC.DEATH, SRC.MIND), -50)
            case EFF.POLYMORPH:
                unit.transformToAnotherClass(unit.memory[0])
            case EFF.ENSLAVED:
                n = unit.enemyTeam
                vb.teams[unit.team].remove(unit)
                vb.teams[n].append(unit)
                unit.id = unit.memory[2]
            case _:
                pass
