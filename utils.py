from background import PASSIVE_ACTIONS
import varbank as vb
from vkmodule import send


def isPassive(unit, method): return method.__name__ in PASSIVE_ACTIONS.get(unit.__class__.__name__, ())

def isMemberOfClass(entity, tupleOfClassNamesOfObject: tuple[str, ...]) -> bool:
    """
    Позволяет проверить (без импорта) является ли объект членом хотя бы одного из перечисленных имён классов.
    """
    return entity.__class__.__name__ in tupleOfClassNamesOfObject


def hide_morale(morale):
    """
    - замени это тернарным оператором и не позорься.
    - нет)
    """
    return 'N/A' if morale < -150 else morale

def getMember(team, postfix, event):
    try:
        target = vb.teams[team][int(postfix[1]) - 1]
        return target
    except IndexError:
        send(event, f'Был выбран несуществующий персонаж.')
        return -1
    except ValueError:
        return -1

def countObjectsOfCertainClassInList(container: list, cls) -> int:
    return sum([1 if x.__class__ == cls else 0 for x in container])


def sumTwoLists(A: list, B: list) -> list:
    return [b+a for a, b in zip(A, B)] + B[len(A):]

def mergeTwoDicts(acum: dict, new: dict) -> dict:
    """
    loadData = {
        "1": [0, 2, 1],
        "2": [1, 0, 1]
    }

    newData = {
        "1": [0, 1, 1],
        "2": [0, 0, 1, 1], # Вероломно был добавлен новый класс.
        "3": [1, 1, 0, 0] # Вероломно новый персонаж
    }
    result = {'1': [0, 3, 2], '2': [1, 0, 2, 1], '3': [1, 1, 0, 0]}
    """
    return {key: value for key, value in zip(new.keys(), [sumTwoLists(acum.get(k, []), new[k]) for k in new.keys()])}