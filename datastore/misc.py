from enum import Enum

class RACES(Enum):
    HUMAN = 'Человеческий'
    UNDEAD = 'Нежить'
    DEMON = 'Демон'
    MYST = 'Мистика'
    ARTIFICIAL = 'Техногенный' # голем, горгулья.
    NONHUMAN = 'Нелюдь' # e.g. орки, если кому-то нужна будет абилка с ненавистью против конкретного вида
    ELF = 'Эльф'


class TURN_STATE(Enum):
    ACTIVE = 0,
    DONE = 1,
    WAIT = 2,

class CLS(Enum):
    Assassin = 'Assassin'