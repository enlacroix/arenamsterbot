from enum import Enum

from datastore.dsources import SRC


# from collections import namedtuple
#
# effectDescr = namedtuple("effectDescr", "nm pos canRemove type attrs required_args")

'''
if key == '-imp':
    send(ctx, 'Ваше пребывание в шкуре беса завершено, идёт обратная трансформация...')
    unit.__class__ = unit.memory[0]
    #unit.dmg *= 2
    unit.arm = unit.memory[2]
    unit.cls = unit.memory[1]
    unit.cls_name = class_dict[unit.memory[1]][0]
if key == 'polymorph':
    send(ctx, 'Настало время вернуться, симурай...')
    unit.__class__ = unit.memory[0]
    unit.cls = unit.memory[1]
    unit.cls_name = class_dict[unit.memory[1]][0]
'''

class EffType(Enum):
    BuffsDebuffs = 0
    VOT = 1
    TempLabels = 2
    Custom = 3
    ResistChanger = 4

effects_images = {
'contr': 'Контрудар 🔪', '-poison': 'Отравление 🤮', '-drunk': 'Опьянение 🍺', '-fear': 'Ужас 😱', '+holyarmor': 'Святая броня 🛡', '+fireshield': '',
'-imp': 'Бес 👺', '+strength': 'Сила 💪', 'stun_resist': 'Неоглушаемость 🗿', '-burn': 'Поджог 😡', '-gall': 'Желчь ⚱', '+regenmana': 'Аркана маны ✨',
'+firedweapon': 'Пылающий клинок 🗡🔥', '+regenhp': 'Регенерация 💝', '-dnote': 'Лже-Кира 🤦‍♀', 'masochism': 'Мазохизм 🔌', '-stone': 'Окаменение 🧱',
'-weakness': 'Слабость 🥵', '+power': 'Могущество 🤟', '-ice': 'Мороз 🥶', '-silence': 'Безмолвие 🤫', '-killmana': '', '+thunder': 'Громовой клинок 🗡⚡',
'+strongarmor': 'Укрепленный доспех 🤠', '+protection': 'Силовое поле 😎', '+vigor': 'ПОЛОН СИЛ ✊', '+haste': 'Ускорение 👠', '+lucky': 'Поцелуй Лепрекона 👒',
'+invis': 'Мгла 👁', '-slow': 'Замедление 🚭', '+imaginary_health': 'Мнимое величие 🤝', '-blood': 'Кровотечение 💉', 'reflect': 'Отражение 👓',
'+poisonedweapon': 'Отравленный клинок 🗡🤢', '+breakarmor': 'Рунический клинок 🗡😭', 'def': 'Защитная стойка', '+vampire': 'Вампирическое оружие 🗡💞',
'-shackles': 'Волшебные оковы ❗', '-verdict': 'Смертный приговор ☠', '-interdict': 'Отлучение ✋', '-curse': 'Проклятье 🧹', '+acc': 'Маяк Ллойда 🕯',
'head_injured': 'Повреждение головы 🤕', 'groin_injured': 'Повреждение паха 😰', 'polymorph': 'Полиморфизм 🤡', 'crit_im': 'Иммунитет к критам 🧱'
}
# https://emojidb.org/scroll-emojis?user_typed_query=1&utm_source=user_search
class EFF(Enum):
    """
    self.health, self.dmg, self.arm, self.ini, self.dodge, self.crit, self.morale, self.mana, self.power, self.gold, self.acc
    'pos' - isPositive - является ли этот эффект положительным.
    """
    SILENCE = {'nm': 'Безмолвие ☝', 'pos': False, 'type': EffType.TempLabels}
    MAGIC_SHACKLES = {'nm': 'Волшебные оковы ✋', 'pos': False, 'type': EffType.TempLabels}
    FIRESHIELD = {'nm': 'Огненный щит 👹', 'type': EffType.TempLabels}
    CONTR = {'nm': 'Контрудар 🔪', 'type': EffType.TempLabels}
    REFLECTION = {'nm': 'Отражение 👓', 'type': EffType.TempLabels}
    STUNNED = {'nm': 'Оглушён', 'type': EffType.TempLabels, 'pos': False}
    INVISIBLE = {'nm': 'Невидимость 🕯', 'type': EffType.TempLabels}
    GUARDED = {'nm': 'Под охраной 😎', 'type': EffType.TempLabels}
    SANCTUM = {'nm': 'Святилище ', 'type': EffType.TempLabels} # аналог невидимости, только отсюда еще можно атаковать
    SLEEPING = {'nm': 'Магический сон 😴', 'pos': False, 'type': EffType.TempLabels}
    CHAINED = {'nm': 'Обездвиженный', 'pos': False, 'type': EffType.TempLabels}
    FIREDWEAPON = {'nm': 'Пылающий клинок 🗡🔥', 'type': EffType.TempLabels}
    POISONEDWEAPON = {'nm': 'Отравленный клинок 🗡🤢', 'type': EffType.TempLabels}
    VAMPWEAPON = {'nm': 'Пьющий жизни 🗡💞', 'type': EffType.TempLabels}
    BREAKWEAPON = {'nm': 'Рунический клинок 🗡🈂️', 'type': EffType.TempLabels}
    MARKED = {'nm': 'Меченный', 'type': EffType.TempLabels}
    CHANGEOFSOURCE = {'nm': 'Смена источника атаки', 'type': EffType.TempLabels} # source=SRC.MIND if self.hasEffect() else SRC.WEAPON

    POISON = {'nm': 'Отравление 🤢', 'pos': False, 'type': EffType.VOT}
    BURNING = {'nm': 'Поджог 🌶️', 'pos': False, 'type': EffType.VOT}
    FEAR = {'nm': 'Ужас 😱', 'pos': False, 'type': EffType.VOT}
    REGENHP = {'nm': 'Регенерация 💝', 'pos': True, 'type': EffType.VOT}
    REGENMANA = {'nm': 'Источник маны ✨', 'pos': True, 'type': EffType.VOT}
    KILLMANA = {'nm': 'Высасывание 😳', 'pos': False, 'type': EffType.VOT}
    BLEEDING = {'nm': 'Кровотечение 💉', 'pos': False, 'type': EffType.VOT, 'required_args': 2}
    GALL = {'nm': 'Токсичная желчь ⚱', 'pos': False, 'type': EffType.VOT}

    STRENGTH = {'nm': 'Сила 💪', 'pos': True, 'type': EffType.BuffsDebuffs, 'attrs': ['dmg']}
    WEAKNESS = {'nm': 'Слабость 🥵', 'pos': False, 'type': EffType.BuffsDebuffs, 'attrs': ['dmg']}
    FOCUSED = {'nm': 'Концентрация 🎯', 'pos': True, 'type': EffType.BuffsDebuffs, 'attrs': ['acc']}
    DRUNK = {'nm': 'Опьянение 🍺', 'pos': False, 'type': EffType.BuffsDebuffs, 'attrs': ['acc']}
    ABSOLUTEPOWER = {'nm': 'Могущество 🤟', 'pos': True, 'type': EffType.BuffsDebuffs, 'attrs': ['power']}
    INTERFERENCE = {'nm': 'Помехи 😵‍', 'pos': False, 'type': EffType.BuffsDebuffs, 'attrs': ['power']}
    HAPPY = {'nm': 'Радость 🤣', 'pos': True, 'type': EffType.BuffsDebuffs, 'attrs': ['morale']}
    STONEFLESH = {'nm': 'Каменная кожа 🗿', 'pos': True, 'type': EffType.BuffsDebuffs, 'attrs': ['arm']}
    LUCKY = {'nm': 'Поцелуй Лепрекона 👒', 'pos': True, 'type': EffType.BuffsDebuffs, 'attrs': ['crit']}
    UNLUCKY = {'nm': 'Поцелуй мумии ', 'pos': False, 'type': EffType.BuffsDebuffs, 'attrs': ['crit']}
    CHAMELEON = {'nm': 'Хамелеон 👁', 'pos': True, 'type': EffType.BuffsDebuffs, 'attrs': ['dodge']}
    FATMAN = {'nm': 'Головокружение ', 'pos': False, 'type': EffType.BuffsDebuffs, 'attrs': ['dodge']}
    SLOW = {'nm': 'Замедление 🚭', 'pos': False, 'type': EffType.BuffsDebuffs, 'attrs': ['ini']}
    HASTE = {'nm': 'Ускорение 👠', 'pos': True, 'type': EffType.BuffsDebuffs, 'attrs': ['ini']}
    MAXHPBUFF = {'nm': 'Запас сил 30/30 ✊', 'pos': True, 'type': EffType.BuffsDebuffs, 'attrs': ['max_hp']}
    PAINMARK = {'nm': 'Печать боли', 'pos': False, 'type': EffType.BuffsDebuffs, 'attrs': ['max_hp']} # Снижение макс ОЗ не даёт лечиться.
    TRADING = {'nm': 'ВОЛЧАРА 🤪', 'pos': True, 'type': EffType.BuffsDebuffs, 'attrs': ['merchant']}
    IMAGINARYHEALTH = {'nm': 'Мнимое здоровье 🤝', 'pos': True, 'type': EffType.BuffsDebuffs, 'attrs': ['health']}
    # todo внимание! только для умножения, но не сложения на меньше, чем 1, т.к. в [0.1]
    BETTERCRITICAL = {'nm': 'Улучшенный критический', 'pos': True, 'type': EffType.BuffsDebuffs, 'attrs': ['crit_mf']}
    INTERDICT = {'nm': 'Отлучение ✋', 'pos': False, 'type': EffType.BuffsDebuffs, 'attrs': ['heal_rate']}
    BLESSED = {'nm': 'Благословение 🤞', 'pos': True, 'type': EffType.BuffsDebuffs, 'attrs': ['heal_rate']}

    ASHILLNESS = {'nm': 'Пепельная язва 🤒', 'pos': False, 'type': EffType.BuffsDebuffs, 'attrs': ['ini', 'power']}
    INSANITY = {'nm': 'Безумие 🤪', 'pos': False, 'type': EffType.BuffsDebuffs, 'attrs': ['power', 'mana']}  # уменьшает на 50% силу магии и уменьшает на 5 ману - пример.
    FALSEKIRA = {'nm': 'Ложный Кира 🤦‍♀', 'pos': False, 'type': EffType.BuffsDebuffs, 'attrs': ['dodge', 'crit']}

    TEMPLVLUP = {'nm': 'Интенсив 📈', 'canRemove': True, 'pos': True, 'type': EffType.Custom}
    IMPISH = {'nm': 'Бесёнок 👺', 'canRemove': True, 'pos': False, 'type': EffType.Custom}
    ENSLAVED = {'nm': 'Порабощённый 👠', 'canRemove': False, 'pos': False, 'type': EffType.Custom}
    DEFEND = {'nm': 'Защитная стойка', 'canRemove': False, 'pos': True, 'type': EffType.Custom}
    POLYMORPH = {'nm': 'Многоликий 🤡', 'canRemove': False, 'pos': True, 'type': EffType.Custom}

    ELEMENTALPROTECTION = {'nm': 'Защита от стихий ', 'canRemove': True, 'pos': True, 'type': EffType.ResistChanger, 'attrs': [SRC.FIRE, SRC.EARTH, SRC.AIR, SRC.WATER]}
    STUNRESIST = {'nm': 'Сопротивление оглушению 🗿', 'pos': True, 'type': EffType.ResistChanger, 'attrs': [SRC.STUN]}
    DEATHSENTENCE = {'nm': 'Смертный приговор ☠', 'pos': False, 'type': EffType.ResistChanger, 'attrs': [SRC.DEATH, SRC.MIND]}
    AIRSHIELD = {'nm': 'Воздушный щит', 'pos': True, 'type': EffType.ResistChanger, 'attrs': [SRC.ARROWS]}
    PETRIFIED = {'nm': 'Каменная статуя', 'canRemove': True, 'pos': True, 'type': EffType.ResistChanger, 'attrs': [SRC.FIRE, SRC.EARTH, SRC.WEAPON, SRC.AIR, SRC.WATER]}





# def find_first_occurrence(pool: list, desire):
#     return next((x for x in pool if x == desire), 'not found')
#
#
# print(find_first_occurrence([4, 5, 7, 6, 7], 4))

# 'msg': Template('Яд нанёс $value урона') .substitute(value=50) - способ определить место для переменной, а только потом её заполнить.
